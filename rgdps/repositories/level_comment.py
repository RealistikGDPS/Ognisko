from __future__ import annotations

from typing import Optional

from rgdps.common.context import Context
from rgdps.models.level_comment import LevelComment


async def from_id(
    ctx: Context,
    comment_id: int,
    include_deleted: bool = False,
) -> Optional[LevelComment]:

    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"

    level_db = await ctx.mysql.fetch_one(
        "SELECT id, user_id, level_id, content, likes, post_ts, deleted "
        "FROM level_comments WHERE id = :comment_id" + condition,
        {
            "comment_id": comment_id,
        },
    )

    if level_db is None:
        return None

    return LevelComment.from_mapping(level_db)


async def create(ctx: Context, comment: LevelComment) -> int:
    return await ctx.mysql.execute(
        "INSERT INTO level_comments (user_id, level_id, content, likes, post_ts, deleted) "
        "VALUES (:user_id, :level_id, :content, :likes, :post_ts, :deleted)",
        comment.as_dict(include_id=False),
    )


async def update(ctx: Context, comment: LevelComment) -> None:
    await ctx.mysql.execute(
        "UPDATE level_comments SET user_id = :user_id, level_id = :level_id, content = :content, "
        "likes = :likes, post_ts = :post_ts, deleted = :deleted WHERE id = :id",
        comment.as_dict(),
    )
