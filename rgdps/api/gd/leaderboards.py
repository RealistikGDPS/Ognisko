from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.api.context import HTTPContext
from rgdps.common import gd_obj
from rgdps.constants.errors import ServiceError
from rgdps.constants.leaderboards import LeaderboardType
from rgdps.constants.responses import GenericResponse
from rgdps.usecases import leaderboards


async def get_leaderboard(
    ctx: HTTPContext = Depends(),
    leaderboard_type: LeaderboardType = Form(..., alias="type"),
) -> str:

    if leaderboard_type == LeaderboardType.STAR:
        leaderboard = await leaderboards.get_top_stars(ctx)
    else:
        raise NotImplementedError

    if isinstance(leaderboard, ServiceError):
        logger.info(f"Failed to get with error {leaderboard!r}")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully fetched leaderboard {leaderboard_type!r}")

    return "|".join(
        gd_obj.dumps(gd_obj.create_profile(user, rank=idx + 1))
        for idx, user in enumerate(leaderboard)
    )
