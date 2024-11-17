from __future__ import annotations

from fastapi import Depends
from fastapi import Form
from fastapi import Request

from ognisko import logger
from ognisko import settings
from ognisko.api import responses
from ognisko.api.context import HTTPContext
from ognisko.api.gd.dependencies import authenticate_dependency
from ognisko.api.validators import GameSaveData
from ognisko.constants.errors import ServiceError
from ognisko.models.user import User
from ognisko.services import save_data


async def save_data_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
):
    # TODO: Streaming
    data = await save_data.get(ctx, user.id)

    if isinstance(data, ServiceError):
        logger.info(
            "Failed to fetch save data.",
            extra={
                "user_id": user.id,
                "error": data.value,
            },
        )
        return responses.fail()

    logger.info(
        "Successfully fetched save data.",
        extra={
            "user_id": user.id,
        },
    )
    return data


async def save_data_post(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    data: GameSaveData = Form(..., alias="saveData"),  # Pain.
    game_version: int = Form(..., alias="gameVersion"),
    binary_version: int = Form(..., alias="binaryVersion"),
):
    res = await save_data.save(
        ctx,
        user.id,
        data,
        game_version,
        binary_version,
    )

    if isinstance(res, ServiceError):
        logger.info(
            "Failed to write save data.",
            extra={
                "user_id": user.id,
                "error": res.value,
            },
        )
        return responses.fail()

    logger.info(
        "Successfully wrote save data.",
        extra={
            "user_id": user.id,
        },
    )
    return responses.success()


# An endpoint that specified which server to use for storing user save data.
# TODO: Support an external save server.
async def get_save_endpoint(request: Request) -> str:
    return f"https://{request.url.hostname}{settings.OGNISKO_HTTP_URL_PREFIX}"
