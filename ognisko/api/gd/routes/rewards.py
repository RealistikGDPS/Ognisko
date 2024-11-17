from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from ognisko import logger
from ognisko.api import responses
from ognisko.api.context import HTTPContext
from ognisko.api.gd.dependencies import authenticate_dependency
from ognisko.common import gd_obj
from ognisko.constants.daily_chests import DailyChestView
from ognisko.constants.errors import ServiceError
from ognisko.models.user import User
from ognisko.services import daily_chests


async def daily_chest_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    view: DailyChestView = Form(..., alias="rewardType"),
    check_string: str = Form(..., alias="chk"),
    device_id: str = Form(..., alias="udid"),
):
    result_check = gd_obj.decrypt_chest_check_string(check_string)

    result = await daily_chests.view(
        ctx,
        user.id,
        view,
    )

    if isinstance(result, ServiceError):
        logger.info(
            "Failed to fetch daily chest.",
            extra={
                "user_id": user.id,
                "view": view.value,
                "error": result.value,
            },
        )
        return responses.fail()

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

    encrypted_result = gd_obj.encrypt_chest_response(result)
    security_hash = gd_obj.create_chest_security_str(encrypted_result.response)

    logger.info(
        "Successfully fetched daily chest.",
        extra={
            "user_id": user.id,
            "view": view.value,
        },
    )

    return f"{encrypted_result.prefix}{encrypted_result.response}|{security_hash}"
