from __future__ import annotations

from typing import Awaitable
from typing import Callable

from fastapi import Form
from fastapi.exceptions import HTTPException

from rgdps import logger
from rgdps import repositories
from rgdps.constants.responses import GenericResponse
from rgdps.models.user import User
from rgdps.repositories import auth

# TODO: add option to replicate https://github.com/RealistikDash/GDPyS/blob/9266cc57c3a4c5d1f51363aa3899ee3c09a23ee8/web/http.py#L338-L341
# FastAPI dependency for seemless authentication.
def authenticate_dependency(
    account_id_alias: str = "accountID",
    password_alias: str = "gjp",
) -> Callable[[int, str], Awaitable[User]]:
    async def wrapper(
        account_id: int = Form(..., alias=account_id_alias),
        gjp: str = Form(..., alias=password_alias),
    ) -> User:
        user = await repositories.user.from_id(account_id)

        if user is None:
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        if not await auth.compare_bcrypt_gjp(
            user.password,
            gjp,
        ):
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        return user

    return wrapper


def password_authenticate_dependency(
    username_alias: str = "userName",
    password_alias: str = "password",
) -> Callable[[str, str], Awaitable[User]]:
    async def wrapper(
        username: str = Form(..., alias=username_alias),
        password: str = Form(..., alias=password_alias),
    ) -> User:
        user = await repositories.user.from_name(username)

        if user is None:
            logger.debug(f"Authentication failed for user {username} (user not found)")
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        if not await auth.compare_bcrypt(
            user.password,
            password,
        ):
            logger.debug(
                f"Authentication failed for user {username} (password mismatch)",
            )
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        return user

    return wrapper
