from __future__ import annotations

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.level_comment import LevelComment


async def get_level(
    ctx: Context,
    level_id: int,
    page: int = 0,
    page_size: int = 10,
) -> list[LevelComment]:
    return await repositories.level_comment.from_level_id_paginated(
        ctx,
        level_id,
        page,
        page_size,
        include_deleted=False,
    )


async def create(
    ctx: Context,
    user_id: int,
    level_id: int,
    content: str,
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
    )
