from __future__ import annotations

from fastapi import Form
from pydantic import EmailStr

from realistikgdps import logger
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.constants.responses import LoginResponse
from realistikgdps.constants.responses import RegisterResponse
from realistikgdps.usecases import users


async def register_post(
    username: str = Form(..., alias="userName", max_length=15),
    email: EmailStr = Form(...),
    password: str = Form(..., max_length=20),
) -> str:
    user = await users.register(
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
    username: str = Form(..., alias="userName", max_length=15),
    password: str = Form(..., max_length=20),
    _: str = Form(..., alias="udid"),
) -> str:

    user = await users.authenticate(username, password)
    if isinstance(user, LoginResponse):
        logger.info(f"Failed to login {username} due to {user!r}.")
        return str(user)

    logger.info(f"{user} has logged in!")

    return f"{user.id},{user.id}"
