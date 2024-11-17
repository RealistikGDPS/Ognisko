from __future__ import annotations

from ognisko import repositories
from ognisko.common.context import Context
from ognisko.constants.errors import ServiceError
from ognisko.constants.leaderboards import LeaderboardType
from ognisko.constants.users import CREATOR_PRIVILEGES
from ognisko.constants.users import STAR_PRIVILEGES
from ognisko.models.user import User

LEADERBOARD_SIZE = 100


async def get(ctx: Context, lb_type: LeaderboardType) -> list[User] | ServiceError:
    match lb_type:
        case LeaderboardType.STAR:
            top_user_ids = await repositories.leaderboard.get_top_stars_paginated(
                ctx,
                page=0,
                page_size=LEADERBOARD_SIZE,
            )
        case LeaderboardType.CREATOR:
            top_user_ids = await repositories.leaderboard.get_top_creators_paginated(
                ctx,
                page=0,
                page_size=LEADERBOARD_SIZE,
            )
        case _:
            raise NotImplementedError

    users = await repositories.user.multiple_from_id(ctx, top_user_ids)
    return users


async def synchronise_top_stars(ctx: Context) -> bool | ServiceError:
    async for user in repositories.user.all(ctx):
        if not (user.privileges & STAR_PRIVILEGES == STAR_PRIVILEGES):
            continue

        await repositories.leaderboard.set_star_count(ctx, user.id, user.stars)

    return True


async def synchronise_top_creators(ctx: Context) -> bool | ServiceError:
    async for user in repositories.user.all(ctx):
        if not (user.privileges & CREATOR_PRIVILEGES == CREATOR_PRIVILEGES):
            continue

        await repositories.leaderboard.set_creator_count(
            ctx,
            user.id,
            user.creator_points,
        )

    return True
