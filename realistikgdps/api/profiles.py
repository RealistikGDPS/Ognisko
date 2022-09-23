from __future__ import annotations

from fastapi import Depends
from fastapi import Form

import realistikgdps.usecases.users
from realistikgdps import logger
from realistikgdps import repositories
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.models.user import User
from realistikgdps.usecases import gd_obj
from realistikgdps.usecases.users import authenticate_dependency

# TODO: Maybe most logic should be moved to a `request_profile` usecase?
# The usecase would handle the logic of checking if the user is allowed to
# view the profile, friendship status, etc.
async def view_user_info(
    target_acc_id: int = Form(..., alias="targetAccountID"),
    user: User = Depends(authenticate_dependency()),
) -> str:
    if target_acc_id == user.id:
        target_ua = user
    else:
        target_ua = await repositories.user.from_id(target_acc_id)

    if target_ua is None:
        logger.info(f"Requested to view info of non-existent account {target_acc_id}.")
        return str(GenericResponse.FAIL)

    return gd_obj.into_gd_obj(
        realistikgdps.usecases.users.create_gd_profile_object(target_ua),
    )
