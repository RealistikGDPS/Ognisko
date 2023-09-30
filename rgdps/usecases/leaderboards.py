from __future__ import annotations

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.leaderboards import LeaderboardType
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User

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

    res = []

    for user_id in top_user_ids:
        user = await repositories.user.from_id(ctx, user_id)
        if user is None:
            continue

        res.append(user)

    return res


STAR_PRIVILEGES = (
    UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC | UserPrivileges.USER_PROFILE_PUBLIC
)


async def synchronise_top_stars(ctx: Context) -> bool | ServiceError:
    user_ids = await repositories.user.all_ids(ctx)

    for user_id in user_ids:
        user = await repositories.user.from_id(ctx, user_id)
        if user is None:
            continue

        if not (user.privileges & STAR_PRIVILEGES == STAR_PRIVILEGES):
            continue

        await repositories.leaderboard.set_star_count(ctx, user_id, user.stars)

    return True


CREATOR_PRIVILEGES = (
    UserPrivileges.USER_CREATOR_LEADERBOARD_PUBLIC | UserPrivileges.USER_PROFILE_PUBLIC
)


async def synchronise_top_creators(ctx: Context) -> bool | ServiceError:
    user_ids = await repositories.user.all_ids(ctx)

    for user_id in user_ids:
        user = await repositories.user.from_id(ctx, user_id)
        if user is None:
            continue

        if not (user.privileges & CREATOR_PRIVILEGES == CREATOR_PRIVILEGES):
            continue

        await repositories.leaderboard.set_creator_count(
            ctx,
            user_id,
            user.creator_points,
        )

    return True
