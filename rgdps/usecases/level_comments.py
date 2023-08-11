from __future__ import annotations

from typing import NamedTuple

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.level_comment import LevelComment
from rgdps.models.user import User
from rgdps.usecases import users


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
        user_perspective = await users.get(
            ctx,
            comment.user_id,
            is_own=False,
        )
        if isinstance(user_perspective, ServiceError):
            return ServiceError.COMMENTS_INVALID_OWNER

        level_comment_responses.append(
            LevelCommentResponse(comment, user_perspective.user),
        )

    comment_count = await repositories.level_comment.get_count_from_level(
        ctx,
        level_id,
    )

    return PaginatedLevelCommentResponse(level_comment_responses, comment_count)


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
