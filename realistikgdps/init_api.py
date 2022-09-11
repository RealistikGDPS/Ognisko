from __future__ import annotations

from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.responses import Response

import realistikgdps.api
import realistikgdps.state
from realistikgdps import logger
from realistikgdps.config import config
from realistikgdps.constants.responses import GenericResponse


def init_events(app: FastAPI) -> None:
    @app.on_event("startup")
    async def on_startup() -> None:
        await realistikgdps.state.services.database.connect()
        await realistikgdps.state.services.redis.initialize()
        logger.info("The server has started!")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("The server is shutting down...")

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


def init_api() -> FastAPI:
    app = FastAPI(
        title="RealistikGDPS",
        # openapi_url=None,
        # docs_url=None,
    )

    init_events(app)

    app.include_router(realistikgdps.api.router)

    return app


asgi_app = init_api()
