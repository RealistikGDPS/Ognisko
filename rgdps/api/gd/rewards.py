from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.api import responses
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common import gd_obj
from rgdps.constants.daily_chests import DailyChestView
from rgdps.constants.errors import ServiceError
from rgdps.models.user import User
from rgdps.usecases import daily_chests


async def daily_chest_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    view: DailyChestView = Form(..., alias="rewardType"),
    check_string: str = Form(..., alias="chk"),
    device_id: str = Form(..., alias="udid"),
):
    result = await daily_chests.view(
        ctx,
        user.id,
        view,
    )

    if isinstance(result, ServiceError):
        logger.info(f"Failed to fetch daily chest with error {result!r}.")
        return responses.fail()

    logger.info(f"Successfully fetched daily chest {result}.")
    result_check = gd_obj.decrypt_chest_check_string(check_string)
    result = gd_obj.create_chest_rewards_str(
        result.chest,
        user.id,
        result_check,
        device_id,
        int(result.small_chest_time_remaining.total_seconds()),
        result.small_chest_count,
        int(result.large_chest_time_remaining.total_seconds()),
        result.large_chest_count,
    )

    security_hash = gd_obj.create_chest_security_str(result)
    encrypted_result = gd_obj.encrypt_chest_response(result)

    return f"{encrypted_result}|{security_hash}"
