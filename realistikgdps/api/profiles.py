from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from realistikgdps import logger
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.models.user import User
from realistikgdps.usecases import gd_obj
from realistikgdps.usecases import users
from realistikgdps.usecases.users import authenticate_dependency


async def view_user_info(
    target_id: int = Form(..., alias="targetAccountID"),
    user: User = Depends(authenticate_dependency()),
) -> str:
    target = await users.get_user_perspective(target_id, user)

    if isinstance(target, GenericResponse):
        logger.info(f"Requested to view info of non-existent account {target_id}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully viewed the profile of {target.user}.")

    return gd_obj.into_gd_obj(
        gd_obj.create_gd_profile(target.user, target.friend_status),
    )
