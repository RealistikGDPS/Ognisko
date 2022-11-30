from __future__ import annotations

from typing import Union

from rgdps import repositories
from rgdps.constants.errors import ServiceError
from rgdps.constants.likes import LikeType
from rgdps.models.like import Like
from rgdps.models.level import Level
from rgdps.models.user import User
from rgdps.models.user_comment import UserComment


async def recalculate_likes(
    like_id: int,
    user: User,
) -> Union[Like, ServiceError]:
    # TODO: Privileges
    like = await repositories.like.from_id(like_id)

    if like is None:
        return ServiceError.LIKES_INVALID_TARGET

    calced_value = await repositories.like.sum_by_target(
        like.target_type,
        like.target_id,
    )

    like.value = calced_value
    await repositories.like.update_value(like.id, like.value)
    return like

async def like_comment(
    user: User,
    comment_id: int,
    value: int = 1,
) -> Union[UserComment, ServiceError]:
    # TODO: Privilege checks
    comment = await repositories.user_comment.from_id(comment_id)

    if comment is None:
        return ServiceError.LIKES_INVALID_TARGET

    if comment.user_id == user.id:
        return ServiceError.LIKES_OWN_TARGET

    if await repositories.like.exists_by_target_and_user(
        LikeType.USER_COMMENT,
        comment_id,
        user.id,
    ):
        return ServiceError.LIKES_ALREADY_LIKED

    comment.likes += value
    await repositories.user_comment.update(comment)

    return comment

async def like_level(
    user: User,
    comment_id: int,
    value: int = 1,
) -> Union[Level, ServiceError]:
    level = await repositories.level.from_id(comment_id)

    if level is None:
        return ServiceError.LIKES_INVALID_TARGET

    if level.user_id == user.id:
        return ServiceError.LIKES_OWN_TARGET

    if await repositories.like.exists_by_target_and_user(
        LikeType.USER_COMMENT,
        comment_id,
        user.id,
    ):
        return ServiceError.LIKES_ALREADY_LIKED

    if await repositories.like.exists_by_target_and_user(
        LikeType.USER_COMMENT,
        comment_id,
        user.id,
    ):
        return ServiceError.LIKES_ALREADY_LIKED
    
    level.likes += value
    await repositories.level.update(level)

    return level
