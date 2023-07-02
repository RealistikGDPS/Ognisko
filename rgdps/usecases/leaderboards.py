from __future__ import annotations

from typing import Union

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.user import User

LEADERBOARD_SIZE = 100


async def get_top_stars(ctx: Context) -> Union[list[User], ServiceError]:
    top_user_ids = await repositories.leaderboard.get_top_stars_paginated(
        ctx,
        page=0,
        page_size=LEADERBOARD_SIZE,
    )
    res = []

    for user_id in top_user_ids:
        user = await repositories.user.from_id(ctx, user_id)
        assert user is not None, "Leaderboard user does not exist."
        res.append(user)

    return res
