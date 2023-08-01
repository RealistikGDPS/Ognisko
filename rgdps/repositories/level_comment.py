from __future__ import annotations

from datetime import datetime

from rgdps.common.context import Context
from rgdps.models.level_comment import LevelComment


async def from_id(
    ctx: Context,
    comment_id: int,
    include_deleted: bool = False,
) -> LevelComment | None:

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


async def create(
    ctx: Context,
    user_id: int,
    level_id: int,
    content: str,
    likes: int = 0,
    post_ts: datetime | None = None,
    deleted: bool = False,
) -> LevelComment:
    comment = LevelComment(
        id=0,
        user_id=user_id,
        level_id=level_id,
        content=content,
        likes=likes,
        post_ts=post_ts or datetime.now(),
        deleted=deleted,
    )
    comment.id = await ctx.mysql.execute(
        "INSERT INTO level_comments (user_id, level_id, content, likes, post_ts, deleted) "
        "VALUES (:user_id, :level_id, :content, :likes, :post_ts, :deleted)",
        comment.as_dict(include_id=False),
    )
    return comment


async def update(ctx: Context, comment: LevelComment) -> None:
    await ctx.mysql.execute(
        "UPDATE level_comments SET user_id = :user_id, level_id = :level_id, content = :content, "
        "likes = :likes, post_ts = :post_ts, deleted = :deleted WHERE id = :id",
        comment.as_dict(),
    )
