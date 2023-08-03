from __future__ import annotations

from datetime import datetime

from rgdps.common.context import Context
from rgdps.common.typing import is_set
from rgdps.common.typing import UNSET
from rgdps.common.typing import Unset
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


async def update_full(ctx: Context, comment: LevelComment) -> None:
    await ctx.mysql.execute(
        "UPDATE level_comments SET user_id = :user_id, level_id = :level_id, content = :content, "
        "likes = :likes, post_ts = :post_ts, deleted = :deleted WHERE id = :id",
        comment.as_dict(),
    )


async def update_partial(
    ctx: Context,
    comment_id: int,
    user_id: int | Unset = UNSET,
    level_id: int | Unset = UNSET,
    content: str | Unset = UNSET,
    likes: int | Unset = UNSET,
    post_ts: datetime | Unset = UNSET,
    deleted: bool | Unset = UNSET,
) -> LevelComment | None:
    changed_data = {}

    if is_set(user_id):
        changed_data["user_id"] = user_id
    if is_set(level_id):
        changed_data["level_id"] = level_id
    if is_set(content):
        changed_data["content"] = content
    if is_set(likes):
        changed_data["likes"] = likes
    if is_set(post_ts):
        changed_data["post_ts"] = post_ts
    if is_set(likes):
        changed_data["likes"] = likes
    if is_set(deleted):
        changed_data["deleted"] = deleted

    if not changed_data:
        return await from_id(ctx, comment_id)

    # Query construction from dict
    query = "UPDATE level_comments SET "
    query += ", ".join(f"{name} = :{name}" for name in changed_data.keys())
    query += " WHERE id = :id"

    changed_data["id"] = comment_id

    await ctx.mysql.execute(query, changed_data)

    return await from_id(ctx, comment_id)
