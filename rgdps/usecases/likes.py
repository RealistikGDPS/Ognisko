from __future__ import annotations

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.likes import LikeType
from rgdps.models.level import Level
from rgdps.models.like import Like
from rgdps.models.user_comment import UserComment


async def recalculate(
    ctx: Context,
    like_id: int,
) -> Like | ServiceError:
    like = await repositories.like.from_id(ctx, like_id)

    if like is None:
        return ServiceError.LIKES_INVALID_TARGET

    calced_value = await repositories.like.sum_by_target(
        ctx,
        like.target_type,
        like.target_id,
    )

    like.value = calced_value
    await repositories.like.update_value(ctx, like.id, like.value)
    return like


async def like_user_comment(
    ctx: Context,
    user_id: int,
    comment_id: int,
    value: int = 1,
) -> UserComment | ServiceError:
    comment = await repositories.user_comment.from_id(ctx, comment_id)

    if comment is None:
        return ServiceError.LIKES_INVALID_TARGET

    if comment.user_id == user_id:
        return ServiceError.LIKES_OWN_TARGET

    if await repositories.like.exists_by_target_and_user(
        ctx,
        LikeType.USER_COMMENT,
        comment_id,
        user_id,
    ):
        return ServiceError.LIKES_ALREADY_LIKED

    await repositories.like.create(
        ctx,
        LikeType.USER_COMMENT,
        comment_id,
        user_id,
        value,
    )
    comment.likes += value
    await repositories.user_comment.update(ctx, comment)

    return comment


async def like_level(
    ctx: Context,
    user_id: int,
    comment_id: int,
    value: int = 1,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, comment_id)

    if level is None:
        return ServiceError.LIKES_INVALID_TARGET

    if level.user_id == user_id:
        return ServiceError.LIKES_OWN_TARGET

    if await repositories.like.exists_by_target_and_user(
        ctx,
        LikeType.USER_COMMENT,
        comment_id,
        user_id,
    ):
        return ServiceError.LIKES_ALREADY_LIKED

    if await repositories.like.exists_by_target_and_user(
        ctx,
        LikeType.USER_COMMENT,
        comment_id,
        user_id,
    ):
        return ServiceError.LIKES_ALREADY_LIKED

    await repositories.like.create(
        ctx,
        LikeType.LEVEL,
        level.id,
        user_id,
        value,
    )
    level.likes += value
    level = await repositories.level.update_partial(
        ctx,
        level.id,
        likes=level.likes,
    )

    if level is None:
        return ServiceError.LIKES_INVALID_TARGET

    return level
