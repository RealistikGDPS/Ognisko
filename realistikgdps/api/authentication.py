from __future__ import annotations

from fastapi import Form
from pydantic import EmailStr

import realistikgdps.repositories
import realistikgdps.usecases.hashes
import realistikgdps.usecases.user_accounts
from realistikgdps import logger
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.constants.responses import LoginResponse


async def register_post(
    username: str = Form(..., alias="userName", max_length=15),
    email: EmailStr = Form(...),
    password: str = Form(..., max_length=20),
) -> str:
    user = await realistikgdps.usecases.user_accounts.register(
        name=username,
        password=password,
        email=email,
    )

    logger.info(f"{user.account} has registered!")

    return str(GenericResponse.SUCCESS)


async def login_post(
    username: str = Form(..., alias="userName", max_length=15),
    password: str = Form(..., max_length=20),
    _: str = Form(..., alias="udid"),
) -> str:

    account = await realistikgdps.repositories.account.from_name(username)
    if account is None:
        return str(LoginResponse.FAIL)

    # TODO: Privileges.

    # TODO: Password verification.
    if not await realistikgdps.usecases.hashes.compare_bcrypt_async(
        account.password,
        password,
    ):
        return str(LoginResponse.FAIL)

    logger.info(f"{account} has logged in!")

    return f"{account.id},{account.user_id}"
