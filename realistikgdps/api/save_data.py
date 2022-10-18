from __future__ import annotations

from fastapi import Depends
from fastapi import Form
from fastapi import Request
from fastapi.responses import FileResponse

from realistikgdps import logger
from realistikgdps.config import config
from realistikgdps.constants.errors import ServiceError
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.models.user import User
from realistikgdps.usecases import save_data
from realistikgdps.usecases.users import password_authenticate_dependency


async def load_save_data(
    user: User = Depends(password_authenticate_dependency()),
):
    data_path = save_data.get_as_path(user)

    if isinstance(data_path, ServiceError):
        logger.info(f"Failed to fetch save data with error {data_path!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully fetched save data {data_path}.")
    return FileResponse(data_path)  # FIXME: The gd client doesnt like this.


async def save_user_save_data(
    req: Request,
    user: User = Depends(password_authenticate_dependency()),
    data: str = Form(..., alias="saveData"),  # Pain.
    game_version: int = Form(..., alias="gameVersion"),
    binary_version: int = Form(..., alias="binaryVersion"),
) -> str:
    res = save_data.save(user, data, game_version, binary_version)

    if isinstance(res, ServiceError):
        logger.info(f"Failed to write save data with error {res!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully wrote save data of {user}.")
    return str(GenericResponse.SUCCESS)


# An endpoint that specified which server to use for storing user save data.
# TODO: Support an external save server.
async def get_save_endpoint(request: Request) -> str:
    return f"{request.url.scheme}://{request.url.hostname}{config.http_url_prefix}"
