from __future__ import annotations

from rgdps import repositories
from rgdps.common.context import Context
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
