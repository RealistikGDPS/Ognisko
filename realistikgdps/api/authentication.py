from __future__ import annotations

from fastapi import Form
from fastapi import Response
from pydantic import EmailStr

import realistikgdps.usecases.user_accounts
from realistikgdps.constants.responses import GenericResponse


async def register_post(
    username: str = Form(..., alias="userName", max_length=15),
    email: EmailStr = Form(...),
    password: str = Form(..., max_length=20),
) -> str:
    await realistikgdps.usecases.user_accounts.register(
        name=username,
        password=password,
        email=email,
    )

    return str(GenericResponse.SUCCESS)
