from __future__ import annotations

from fastapi import Depends
from fastapi import Form
from future import __annotations__

import realistikgdps.usecases.user_accounts
from realistikgdps import logger
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.usecases.authentication import authenticate_dependency
from realistikgdps.usecases.gd_obj import into_gd_obj
from realistikgdps.usecases.user_accounts import UserAccount


async def view_user_info(
    target_acc_id: int = Form(..., alias="targetAccountID"),
    user: UserAccount = Depends(authenticate_dependency()),
) -> str:
    if target_acc_id == user.account.id:
        target_ua = user
    else:
        target_ua = await realistikgdps.usecases.user_accounts.from_id(target_acc_id)

    if target_ua is None:
        logger.info(f"Requested to view info of non-existent account {target_acc_id}.")
        return str(GenericResponse.FAIL)

    return into_gd_obj(
        realistikgdps.usecases.user_accounts.create_gd_profile_object(target_ua),
    )
