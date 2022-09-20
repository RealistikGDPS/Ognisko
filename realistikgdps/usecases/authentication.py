from __future__ import annotations

from typing import Any
from typing import Awaitable
from typing import Callable

from fastapi import HTTPException

import realistikgdps.repositories.account
import realistikgdps.usecases.hashes
import realistikgdps.usecases.user_accounts
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.usecases.user_accounts import UserAccount


async def authenticate_account_by_password(account: Account, password: str) -> bool:
    return await realistikgdps.usecases.hashes.compare_bcrypt_async(
        hashed=account.password,
        plain=password,
    )


async def authenticate_account_id_by_password(account_id: int, password: str) -> bool:
    account = await realistikgdps.repositories.account.from_id(account_id)

    if account is None:
        return False

    return await authenticate_account_by_password(account, password)


# TODO: add option to replicate https://github.com/RealistikDash/GDPyS/blob/9266cc57c3a4c5d1f51363aa3899ee3c09a23ee8/web/http.py#L338-L341
# FastAPI dependency for seemless authentication.
def authenticate_dependency(
    param_function: Callable[..., Any],
    account_id_alias: str = "accountID",
    gjp_alias: str = "gjp",
) -> Callable[[int, str], Awaitable[UserAccount]]:
    async def wrapper(
        account_id: int = param_function(..., alias=account_id_alias),
        gjp: str = param_function(..., alias=gjp_alias),
    ) -> UserAccount:
        user = await realistikgdps.usecases.user_accounts.from_id(account_id)

        if user is None:
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        if not await authenticate_account_by_password(
            account=user.account,
            password=realistikgdps.usecases.hashes.decode_gjp(gjp),
        ):
            raise HTTPException(
                status_code=200,
                detail=str(GenericResponse.FAIL),
            )

        return user

    return wrapper
