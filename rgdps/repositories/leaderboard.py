from __future__ import annotations

from rgdps.common.context import Context


async def get_star_rank(ctx: Context, user_id: int) -> int:
    redis_rank = await ctx.redis.zrevrank(
        "rgdps:leaderboards:stars",
        user_id,
    )

    if redis_rank is None:
        return 0

    return redis_rank + 1


async def set_star_count(ctx: Context, user_id: int, stars: int) -> None:
    if stars <= 0:
        await ctx.redis.zrem(
            "rgdps:leaderboards:stars",
            user_id,
        )
        return
    await ctx.redis.zadd(
        "rgdps:leaderboards:stars",
        {str(user_id): stars},  # is str necessary?
    )


async def get_top_stars_paginated(
    ctx: Context,
    page: int,
    page_size: int,
) -> list[int]:
    return await ctx.redis.zrevrange(
        "rgdps:leaderboards:stars",
        page * page_size,
        (page + 1) * page_size,
    )


async def remove_star_count(ctx: Context, user_id: int) -> None:
    await ctx.redis.zrem(
        "rgdps:leaderboards:stars",
        user_id,
    )


async def get_creator_rank(ctx: Context, user_id: int) -> int:
    redis_rank = await ctx.redis.zrevrank(
        "rgdps:leaderboards:creators",
        user_id,
    )

    if redis_rank is None:
        return 0

    return redis_rank + 1


async def set_creator_count(ctx: Context, user_id: int, points: int) -> None:
    if points <= 0:
        await ctx.redis.zrem(
            "rgdps:leaderboards:creators",
            user_id,
        )
        return

    await ctx.redis.zadd(
        "rgdps:leaderboards:creators",
        {str(user_id): points},
    )


async def get_top_creators_paginated(
    ctx: Context,
    page: int,
    page_size: int,
) -> list[int]:
    return await ctx.redis.zrevrange(
        "rgdps:leaderboards:creators",
        page * page_size,
        (page + 1) * page_size,
    )


async def remove_creator_count(ctx: Context, user_id: int) -> None:
    await ctx.redis.zrem(
        "rgdps:leaderboards:creators",
        user_id,
    )
