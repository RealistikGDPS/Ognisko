from __future__ import annotations

from typing import Awaitable
from typing import Callable

from fastapi import Depends
from fastapi import Form
from fastapi.exceptions import HTTPException

from rgdps import logger
from rgdps import usecases
from rgdps.api.context import HTTPContext
from rgdps.common import hashes
from rgdps.constants.errors import ServiceError
from rgdps.constants.responses import GenericResponse
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User

# TODO: add option to replicate https://github.com/RealistikDash/GDPyS/blob/9266cc57c3a4c5d1f51363aa3899ee3c09a23ee8/web/http.py#L338-L341
def authenticate_dependency(
    user_id_alias: str = "accountID",
    password_alias: str = "gjp",
    required_privileges: UserPrivileges | None = None,
) -> Callable[[HTTPContext, int, str], Awaitable[User]]:
    async def wrapper(
        ctx: HTTPContext = Depends(),
        user_id: int = Form(..., alias=user_id_alias),
        gjp: str = Form(..., alias=password_alias),
    ) -> User:
        password_plain = hashes.decode_gjp(gjp)
        user = await usecases.auth.authenticate(
            ctx,
            user_id,
            password_plain,
        )

        if isinstance(user, ServiceError):
            logger.debug(
                "Authentication failed for user.",
                extra={
                    "user_id": user_id,
                    "error": user.value,
                },
            )
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        if required_privileges is not None and not (
            user.privileges & required_privileges == required_privileges
        ):
            logger.debug(
                "Authentication failed for user due to insufficient privileges.",
                extra={
                    "user_id": user_id,
                    "privileges": user.privileges,
                    "required_privileges": required_privileges,
                },
            )
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        return user

    return wrapper


def password_authenticate_dependency(
    username_alias: str = "userName",
    password_alias: str = "password",
    required_privileges: UserPrivileges | None = None,
) -> Callable[[HTTPContext, str, str], Awaitable[User]]:
    async def wrapper(
        ctx: HTTPContext = Depends(),
        username: str = Form(..., alias=username_alias),
        password_plain: str = Form(..., alias=password_alias),
    ) -> User:
        user = await usecases.auth.authenticate_from_name(
            ctx,
            username,
            password_plain,
        )

        if isinstance(user, ServiceError):
            logger.debug(
                "Authentication failed for user.",
                extra={
                    "username": username,
                    "error": user.value,
                },
            )
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        if required_privileges is not None and not (
            user.privileges & required_privileges == required_privileges
        ):
            logger.debug(
                "Authentication failed for user due to insufficient privileges.",
                extra={
                    "username": username,
                    "privileges": user.privileges,
                    "required_privileges": required_privileges,
                },
            )
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        return user

    return wrapper
