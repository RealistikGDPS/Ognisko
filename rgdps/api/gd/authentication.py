from __future__ import annotations

from fastapi import Depends
from fastapi import Form
from pydantic import EmailStr

from rgdps import logger
from rgdps.api.context import HTTPContext
from rgdps.constants.errors import ServiceError
from rgdps.constants.responses import GenericResponse
from rgdps.constants.responses import LoginResponse
from rgdps.constants.responses import RegisterResponse
from rgdps.usecases import users


async def register_post(
    # ctx: HTTPContext = Depends(),
    username: str = Form(..., alias="userName", max_length=15),
    email: EmailStr = Form(...),
    password: str = Form(..., max_length=20),
) -> str:
    user = await users.register(
        ctx,
        name=username,
        password=password,
        email=email,
    )

    if isinstance(user, RegisterResponse):
        logger.info(f"Failed to register {username} due to {user!r}.")
        return str(user)

    logger.info(f"{user} has registered!")

    return str(GenericResponse.SUCCESS)


async def login_post(
    ctx: HTTPContext = Depends(),
    username: str = Form(..., alias="userName", max_length=15),
    password: str = Form(..., max_length=20),
    _: str = Form(..., alias="udid"),
) -> str:

    user = await users.authenticate(ctx, username, password)
    if isinstance(user, ServiceError):
        logger.info(f"Failed to login {username} due to {user!r}.")

        if user is ServiceError.AUTH_NO_PRIVILEGE:
            return str(LoginResponse.ACCOUNT_DISABLED)

        return str(LoginResponse.FAIL)

    logger.info(f"{user} has logged in!")

    return f"{user.id},{user.id}"
