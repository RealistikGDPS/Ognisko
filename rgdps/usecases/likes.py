from __future__ import annotations

from typing import Union

from rgdps import repositories
from rgdps.constants.errors import ServiceError
from rgdps.models.like import Like
from rgdps.models.user import User


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
