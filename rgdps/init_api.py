from __future__ import annotations

from urllib.parse import quote

import httpx
from databases import DatabaseURL
from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from meilisearch_python_async import Client as MeiliClient
from redis.asyncio import Redis
from starlette.middleware.base import RequestResponseEndpoint

from rgdps import logger
from rgdps.common.cache.memory import SimpleAsyncMemoryCache
from rgdps.common.cache.redis import SimpleRedisCache
from rgdps.config import config
from rgdps.constants.responses import GenericResponse
from rgdps.services.mysql import MySQLService


def init_events(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def on_validation_error(
        request: Request,
        e: RequestValidationError,
    ) -> Response:
        logger.error(
            f"A validation error has occured while parsing the request to "
            f"{request.url}",
        )
        logger.debug(e.errors())

        # If its a GD related request, give them something the client understands.
        if str(request.url).startswith(config.http_url_prefix):
            return Response(str(GenericResponse.FAIL))

        return JSONResponse(
            {"message": "Validation error!"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.middleware("http")
    async def http_middleware(
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Verifying request header for client endpoints.
        if str(request.url).startswith(config.http_url_prefix):
            # GD sends an empty User-Agent header.
            if request.headers.get("User-Agent") != "":
                logger.info(
                    "A user has sent a request to a client endpoint with a "
                    "non-empty User-Agent header. This implies the usage of bots.",
                )
                return Response(str(GenericResponse.FAIL))

        return await call_next(request)


def init_mysql(app: FastAPI) -> None:
    database_url = DatabaseURL(
        "mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
            username=config.sql_user,
            password=quote(config.sql_pass),
            host=config.sql_host,
            port=config.sql_port,
            db=config.sql_db,
        ),
    )

    app.state.mysql = MySQLService(database_url)

    @app.on_event("startup")
    async def on_startup() -> None:
        await app.state.mysql.connect()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await app.state.mysql.disconnect()


def init_redis(app: FastAPI) -> None:
    app.state.redis = Redis.from_url(
        f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        await app.state.redis.initialize()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await app.state.redis.close()


def init_meili(app: FastAPI) -> None:
    app.state.meili = MeiliClient(
        f"http://{config.meili_host}:{config.meili_port}",
        config.meili_key,
        timeout=10,
    )

    @app.on_event("startup")
    async def startup() -> None:
        await app.state.meili.health()


def init_http(app: FastAPI) -> None:
    app.state.http = httpx.AsyncClient()

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await app.state.http.aclose()


def init_cache_stateful(app: FastAPI) -> None:
    app.state.user_cache = SimpleAsyncMemoryCache()
    app.state.password_cache = SimpleAsyncMemoryCache()


def init_cache_stateless(app: FastAPI) -> None:
    app.state.user_cache = SimpleRedisCache(
        redis=app.state.redis,
        key_prefix="rgdps:cache:user",
    )
    app.state.password_cache = SimpleRedisCache(
        redis=app.state.redis,
        key_prefix="rgdps:cache:password",
        deserialise=lambda x: x.decode(),
        serialise=lambda x: x.encode(),
    )


def init_routers(app: FastAPI) -> None:
    import rgdps.api

    app.include_router(rgdps.api.gd.router)


def init_api() -> FastAPI:
    app = FastAPI(
        title="RealistikGDPS",
        openapi_url=None,
        docs_url=None,
    )

    init_events(app)
    init_mysql(app)
    init_redis(app)
    init_meili(app)
    init_http(app)

    if config.srv_stateless:
        init_cache_stateless(app)
    else:
        init_cache_stateful(app)

    init_routers(app)

    return app


asgi_app = init_api()
