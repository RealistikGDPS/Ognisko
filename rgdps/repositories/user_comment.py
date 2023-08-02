from __future__ import annotations

from datetime import datetime

from rgdps.common.context import Context
from rgdps.common.typing import is_set
from rgdps.common.typing import UNSET
from rgdps.common.typing import Unset
from rgdps.models.user_comment import UserComment


async def from_id(
    ctx: Context,
    comment_id: int,
    include_deleted: bool = False,
) -> UserComment | None:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"
    comment_db = await ctx.mysql.fetch_one(
        "SELECT id, user_id, content, likes, post_ts, deleted "
        "FROM user_comments WHERE id = :id" + condition,
        {
            "id": comment_id,
        },
    )

    if comment_db is None:
        return None

    return UserComment.from_mapping(comment_db)


async def from_user_id(
    ctx: Context,
    user_id: int,
    include_deleted: bool = False,
) -> list[UserComment]:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"
    comments_db = await ctx.mysql.fetch_all(
        "SELECT id, user_id, content, likes, post_ts, deleted FROM "
        "user_comments WHERE user_id = :user_id" + condition,
        {"user_id": user_id},
    )

    return [UserComment.from_mapping(comment_db) for comment_db in comments_db]


async def from_user_id_paginated(
    ctx: Context,
    user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> list[UserComment]:
    condition = ""
    # FIXME: Unused
    if not include_deleted:
        condition = "AND NOT deleted"

    comments_db = await ctx.mysql.fetch_all(
        "SELECT id, user_id, content, likes, post_ts, deleted FROM "
        f"user_comments WHERE user_id = :user_id {condition} "
        "ORDER BY id DESC LIMIT :limit OFFSET :offset",
        {
            "user_id": user_id,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [UserComment.from_mapping(comment_db) for comment_db in comments_db]


async def get_user_comment_count(
    ctx: Context,
    user_id: int,
    include_deleted: bool = False,
) -> int:
    return await ctx.mysql.fetch_val(
        "SELECT COUNT(*) FROM user_comments WHERE user_id = :user_id " "AND deleted = 0"
        if not include_deleted
        else "",
        {"user_id": user_id},
    )


async def create(
    ctx: Context,
    user_id: int,
    content: str,
    likes: int = 0,
    post_ts: datetime | None = None,
    deleted: bool = False,
) -> UserComment:
    comment = UserComment(
        id=0,
        user_id=user_id,
        content=content,
        likes=likes,
        post_ts=post_ts or datetime.now(),
        deleted=deleted,
    )

    comment.id = await ctx.mysql.execute(
        "INSERT INTO user_comments (user_id, content, likes, post_ts, deleted) "
        "VALUES (:user_id, :content, :likes, :post_ts, :deleted)",
        comment.as_dict(include_id=False),
    )

    return comment


async def update(ctx: Context, comment: UserComment) -> None:
    await ctx.mysql.execute(
        "UPDATE user_comments SET user_id = :user_id, content = :content, "
        "likes = :likes, post_ts = :post_ts, deleted = :deleted WHERE id = :id",
        comment.as_dict(include_id=True),
    )


async def update_partial(
    ctx: Context,
    comment_id: int,
    user_id: Unset | int = UNSET,
    content: Unset | str = UNSET,
    likes: Unset | int = UNSET,
    post_ts: Unset | datetime = UNSET,
    deleted: Unset | bool = UNSET,
) -> UserComment | None:

    changed_data = {}

    if is_set(user_id):
        changed_data["user_id"] = user_id
    if is_set(content):
        changed_data["content"] = content
    if is_set(likes):
        changed_data["likes"] = likes
    if is_set(post_ts):
        changed_data["post_ts"] = post_ts
    if is_set(deleted):
        changed_data["deleted"] = deleted

    if not changed_data:
        return None

    query = "UPDATE user_comments SET "
    query += ", ".join(f"{key} = :{key}" for key in changed_data.keys())
    query += " WHERE id = :id"

    changed_data["id"] = comment_id

    await ctx.mysql.execute(query, changed_data)

    return await from_id(ctx, comment_id)
