from __future__ import annotations

import urllib.parse
import uuid

from databases import DatabaseURL
from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi_limiter import FastAPILimiter
from starlette.middleware.base import RequestResponseEndpoint

from ognisko import logger
from ognisko import settings
from ognisko.adapters import MeiliSearchClient
from ognisko.adapters.boomlings import GeometryDashClient
from ognisko.adapters.mysql import MySQLService
from ognisko.adapters.redis import RedisClient
from ognisko.adapters.storage import LocalStorage
from ognisko.adapters.storage import S3Storage
from ognisko.constants.responses import GenericResponse
from ognisko.utilities.cache.memory import SimpleAsyncMemoryCache

from . import context
from . import gd
from . import pubsub


def init_logging() -> None:
    logger.init_basic_logging(settings.OGNISKO_LOG_LEVEL)


def init_events(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def on_validation_error(
        request: Request,
        e: RequestValidationError,
    ) -> Response:
        logger.exception(
            f"A validation error has occured while parsing a request.",
            extra={
                "url": str(request.url),
                "method": request.method,
                "errors": e.errors(),
                "uuid": request.state.uuid,
            },
        )

        # If its a GD related request, give them something the client understands.
        if str(request.url).startswith(settings.OGNISKO_HTTP_URL_PREFIX):
            return Response(str(GenericResponse.FAIL))

        return JSONResponse(
            {"message": "Validation error!"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


def init_mysql(app: FastAPI) -> None:
    # Use asyncmy if available (~2x faster than the default MySQL driver).
    protocol = "mysql"
    try:
        import asyncmy  # noqa

        protocol = "mysql+asyncmy"
        logger.debug("Using asyncmy as the MySQL driver.")
    except ImportError:
        logger.debug("Using Database's default MySQL driver.")

    database_url = DatabaseURL(
        "{protocol}://{username}:{password}@{host}:{port}/{db}".format(
            protocol=protocol,
            username=settings.MYSQL_USER,
            password=urllib.parse.quote(settings.MYSQL_PASSWORD),
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_TCP_PORT,
            db=settings.MYSQL_DATABASE,
        ),
    )

    app.state.mysql = MySQLService(database_url)

    @app.on_event("startup")
    async def on_startup() -> None:
        await app.state.mysql.connect()
        logger.info(
            "Connected to the MySQL database.",
            extra={
                "host": settings.MYSQL_HOST,
                "db": settings.MYSQL_DATABASE,
            },
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await app.state.mysql.disconnect()


def init_redis(app: FastAPI) -> None:
    app.state.redis = RedisClient(
        settings.REDIS_HOST,
        settings.REDIS_PORT,
        settings.REDIS_DATABASE,
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        # TODO: Fix.
        shared_ctx = context.PubsubContext(app)
        pubsub.inject_context(shared_ctx)
        app.state.redis.include_router(pubsub.router)

        await app.state.redis.initialise()

        # TODO: Custom ratelimit callback that returns `-1`.
        await FastAPILimiter.init(
            app.state.redis,
            prefix="ognisko:ratelimit",
        )

        logger.info(
            "Connected to the Redis database.",
            extra={
                "host": settings.REDIS_HOST,
                "db": settings.REDIS_DATABASE,
            },
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await app.state.redis.close()


def init_meili(app: FastAPI) -> None:
    app.state.meili = MeiliSearchClient.from_host(
        settings.MEILI_HOST,
        settings.MEILI_PORT,
        settings.MEILI_MASTER_KEY,
        timeout=10,
    )

    @app.on_event("startup")
    async def startup() -> None:
        await app.state.meili.health()
        logger.info(
            "Connected to the MeiliSearch database.",
            extra={
                "host": settings.MEILI_HOST,
            },
        )


# def init_s3_storage(app: FastAPI) -> None:
#     app.state.storage = S3Storage(
#         region=settings.S3_REGION,
#         endpoint=settings.S3_ENDPOINT,
#         access_key=settings.S3_ACCESS_KEY,
#         secret_key=settings.S3_SECRET_KEY,
#         bucket=settings.S3_BUCKET,
#         retries=10,
#         timeout=5,
#     )
#
#     @app.on_event("startup")
#     async def startup() -> None:
#         app.state.storage = await app.state.storage.connect()
#         logger.info(
#             "Connected to S3 storage.",
#             extra={
#                 "bucket": settings.S3_BUCKET,
#                 "region": settings.S3_REGION,
#             },
#         )
#
#     @app.on_event("shutdown")
#     async def shutdown() -> None:
#         await app.state.storage.disconnect()


def init_local_storage(app: FastAPI) -> None:
    app.state.storage = LocalStorage(
        root=settings.OGNISKO_INTERNAL_DATA_DIRECTORY,
    )

    @app.on_event("startup")
    async def startup() -> None:
        logger.info("Connected to the local storage.")


def init_gd(app: FastAPI) -> None:
    app.state.gd = GeometryDashClient(
        settings.OGNISKO_OFFICIAL_SERVER_MIRROR_URL,
    )

    logger.info(
        "Initialised the main Geometry Dash client.",
        extra={
            "server_url": settings.OGNISKO_OFFICIAL_SERVER_MIRROR_URL,
        },
    )


def init_cache(app: FastAPI) -> None:
    app.state.password_cache = SimpleAsyncMemoryCache()

    logger.info("Initialised stateful password caching.")


def init_gd_routers(app: FastAPI) -> None:
    import ognisko.api

    app.include_router(ognisko.api.gd.routes.router)


def init_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def mysql_transaction(request: Request, call_next):
        logger.debug(
            "Opened a new MySQL transaction for request.",
            extra={
                "uuid": request.state.uuid,
            },
        )
        async with app.state.mysql.transaction() as sql:
            request.state.mysql = sql
            return await call_next(request)

    if settings.OGNISKO_USE_USER_AGENT_GUARD:
        logger.debug("Using User-Agent guard middleware.")

        @app.middleware("http")
        async def enforce_user_agent(
            request: Request,
            call_next: RequestResponseEndpoint,
        ) -> Response:
            # Verifying request header for client endpoints.
            if str(request.url).startswith(settings.OGNISKO_HTTP_URL_PREFIX):
                # GD sends an empty User-Agent header.
                user_agent = request.headers.get("User-Agent")
                if user_agent != "":
                    logger.info(
                        "Client request stopped due to invalid User-Agent header.",
                        extra={
                            "url": str(request.url),
                            "uuid": request.state.uuid,
                            "user_agent": user_agent,
                        },
                    )
                    return Response(str(GenericResponse.FAIL))

            return await call_next(request)

    else:
        logger.debug("Skipping User-Agent guard middleware.")

    @app.middleware("http")
    async def exception_logging(
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(
                f"An exception has occured while processing a request!",
                extra={
                    "url": str(request.url),
                    "method": request.method,
                    "uuid": request.state.uuid,
                },
            )
            raise e

    @app.middleware("http")
    async def assign_uuid(request: Request, call_next):
        request.state.uuid = str(uuid.uuid4())
        return await call_next(request)


def init_api() -> FastAPI:
    init_logging()
    app = FastAPI(
        title="Ognisko Backend",
        openapi_url=None,
        docs_url=None,
    )

    init_events(app)
    init_middlewares(app)
    init_mysql(app)
    init_redis(app)
    init_meili(app)
    init_gd(app)

    # if settings.S3_ENABLED:
    #    init_s3_storage(app)
    # else:
    init_local_storage(app)

    init_cache(app)

    init_gd_routers(app)

    return app
