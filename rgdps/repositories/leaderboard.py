from __future__ import annotations

from typing import Optional

from rgdps.constants.leaderboards import LeaderboardType
from rgdps.state import services


async def get_star_rank(user_id: int) -> int:
    redis_rank = await services.redis.zrevrank(
        "rgdps:leaderboards:stars",
        user_id,
    )

    if redis_rank is None:
        return 0

    return redis_rank + 1


async def set_star_count(user_id: int, stars: int) -> None:
    if stars <= 0:
        await services.redis.zrem(
            "rgdps:leaderboards:stars",
            user_id,
        )
        return
    await services.redis.zadd(
        "rgdps:leaderboards:stars",
        {str(user_id): stars},  # is str necessary?
    )


async def get_top_stars_paginated(
    page: int,
    page_size: int,
) -> list[int]:
    return await services.redis.zrevrange(
        "rgdps:leaderboards:stars",
        page * page_size,
        (page + 1) * page_size,
    )
