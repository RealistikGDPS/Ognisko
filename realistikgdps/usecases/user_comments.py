from __future__ import annotations

from datetime import datetime
from typing import NamedTuple
from typing import Union

from realistikgdps import repositories
from realistikgdps.constants.errors import ServiceError
from realistikgdps.models.user import User
from realistikgdps.models.user_comment import UserComment


class UserCommentResponse(NamedTuple):
    comment: list[UserComment]
    user: User
    total: int


# Perspective variant is not necessary as the related endpoints don't support
# authentication.
async def get_user(
    user_id: int,
    page: int = 0,
    page_size: int = 10,
) -> Union[UserCommentResponse, ServiceError]:
    target_user = await repositories.user.from_id(user_id)

    if target_user is None:
        return ServiceError.PROFILE_USER_NOT_FOUND

    comments = await repositories.user_comment.from_user_id_paginated(
        user_id,
        page,
        page_size,
    )
    total = 0
    if comments:
        total = await repositories.user_comment.count_from_user_id(user_id)

    return UserCommentResponse(comments, target_user, total)


async def create(
    user: User,
    content: str,
) -> Union[UserComment, ServiceError]:
    # TODO: Privilege checks

    if len(content) > 255:
        return ServiceError.COMMENTS_INVALID_CONTENT

    # TODO: Charset check
    comment = UserComment(
        id=0,
        user_id=user.id,
        content=content,
        likes=0,
        post_ts=datetime.now(),
        deleted=False,
    )
    comment.id = await repositories.user_comment.create(comment)

    return comment
