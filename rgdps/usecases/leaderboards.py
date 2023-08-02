from __future__ import annotations

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.user import User

LEADERBOARD_SIZE = 100


async def get_top_stars(ctx: Context) -> list[User] | ServiceError:
    top_user_ids = await repositories.leaderboard.get_top_stars_paginated(
        ctx,
        page=0,
        page_size=LEADERBOARD_SIZE,
    )
    res = []

    for user_id in top_user_ids:
        user = await repositories.user.from_id(ctx, user_id)
        if user is None:
            continue
        
        res.append(user)

    return res
