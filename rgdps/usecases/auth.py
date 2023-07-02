from __future__ import annotations

from typing import Union

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User
from rgdps.repositories import auth


async def authenticate(
    ctx: Context,
    user_id: int,
    password: str,
) -> Union[User, ServiceError]:
    user = await repositories.user.from_id(ctx, user_id)

    if user is None:
        return ServiceError.AUTH_NOT_FOUND

    if not user.privileges & UserPrivileges.USER_AUTHENTICATE:
        return ServiceError.AUTH_NO_PRIVILEGE

    if not await auth.compare_bcrypt(
        ctx,
        user.password,
        password,
    ):
        return ServiceError.AUTH_PASSWORD_MISMATCH

    return user


async def authenticate_from_name(
    ctx: Context,
    username: str,
    password: str,
) -> Union[User, ServiceError]:
    user = await repositories.user.from_name(ctx, username)

    if user is None:
        return ServiceError.AUTH_NOT_FOUND

    return await authenticate(
        ctx,
        user.id,
        password,
    )
