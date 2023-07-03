from __future__ import annotations

from datetime import datetime
from typing import NamedTuple
from typing import Union

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.user import User
from rgdps.models.user_comment import UserComment


class UserCommentResponse(NamedTuple):
    comment: list[UserComment]
    user: User
    total: int


# Perspective variant is not necessary as the related endpoints don't support
# authentication.
async def get_user(
    ctx: Context,
    user_id: int,
    page: int = 0,
    page_size: int = 10,
) -> Union[UserCommentResponse, ServiceError]:
    target_user = await repositories.user.from_id(ctx, user_id)

    if target_user is None:
        return ServiceError.PROFILE_USER_NOT_FOUND

    comments = await repositories.user_comment.from_user_id_paginated(
        ctx,
        user_id,
        page,
        page_size,
        include_deleted=False,
    )

    return UserCommentResponse(comments.comments, target_user, comments.total)


async def create(
    ctx: Context,
    user: User,
    content: str,
) -> Union[UserComment, ServiceError]:
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
    comment.id = await repositories.user_comment.create(ctx, comment)

    return comment


async def delete(
    ctx: Context,
    user: User,
    comment_id: int,
) -> Union[UserComment, ServiceError]:
    comment = await repositories.user_comment.from_id(ctx, comment_id)

    if comment is None:
        return ServiceError.COMMENTS_NOT_FOUND

    if comment.user_id != user.id:
        return ServiceError.COMMENTS_INVALID_OWNER

    comment.deleted = True
    await repositories.user_comment.update(ctx, comment)

    return comment
