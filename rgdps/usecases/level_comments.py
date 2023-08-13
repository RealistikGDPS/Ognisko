from __future__ import annotations

from typing import NamedTuple

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.level_comment import LevelComment
from rgdps.models.user import User


class LevelCommentResponse(NamedTuple):
    comment: LevelComment
    user: User


class PaginatedLevelCommentResponse(NamedTuple):
    comments: list[LevelCommentResponse]
    total: int


async def get_level(
    ctx: Context,
    level_id: int,
    page: int = 0,
    page_size: int = 10,
) -> PaginatedLevelCommentResponse | ServiceError:
    comments = await repositories.level_comment.from_level_id_paginated(
        ctx,
        level_id,
        page,
        page_size,
        include_deleted=False,
    )

    level_comment_responses = []
    for comment in comments:
        user = await repositories.user.from_id(ctx, comment.user_id)

        if user is None:
            continue

        level_comment_responses.append(
            LevelCommentResponse(comment, user),
        )

    comment_count = await repositories.level_comment.get_count_from_level(
        ctx,
        level_id,
    )

    return PaginatedLevelCommentResponse(level_comment_responses, comment_count)


async def get_user(
    ctx: Context,
    user_id: int,
    page: int = 0,
    page_size: int = 10,
) -> PaginatedLevelCommentResponse | ServiceError:
    user = await repositories.user.from_id(ctx, user_id)

    if user is None:
        return ServiceError.USER_NOT_FOUND

    comments = await repositories.level_comment.from_user_id_paginated(
        ctx,
        user_id,
        page,
        page_size,
        include_deleted=False,
    )

    comment_count = await repositories.level_comment.get_count_from_user(
        ctx,
        user_id,
    )

    return PaginatedLevelCommentResponse(
        [LevelCommentResponse(comment, user) for comment in comments],
        comment_count,
    )


async def create(
    ctx: Context,
    user_id: int,
    level_id: int,
    content: str,
    percent: int,
) -> LevelComment | ServiceError:
    # TODO: Spam protection
    level = repositories.level.from_id(ctx, level_id=level_id)
    if level is None:
        return ServiceError.COMMENTS_TARGET_NOT_FOUND

    return await repositories.level_comment.create(
        ctx,
        user_id=user_id,
        level_id=level_id,
        content=content,
        percent=percent,
    )
