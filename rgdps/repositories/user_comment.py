from __future__ import annotations

from typing import NamedTuple
from typing import Optional

from rgdps.common.context import Context
from rgdps.models.user_comment import UserComment


async def from_id(
    ctx: Context,
    comment_id: int,
    include_deleted: bool = False,
) -> Optional[UserComment]:
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


class CommentPage(NamedTuple):
    comments: list[UserComment]
    total: int


async def from_user_id_paginated(
    ctx: Context,
    user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> CommentPage:
    condition = ""
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

    comments = [UserComment.from_mapping(comment_db) for comment_db in comments_db]

    total = await ctx.mysql.fetch_val(
        "SELECT COUNT(*) FROM user_comments WHERE user_id = :user_id "
        "AND deleted = 0",
        {"user_id": user_id},
    )

    return CommentPage(
        comments=comments,
        total=total,
    )


async def create(ctx: Context, comment: UserComment) -> int:
    return await ctx.mysql.execute(
        "INSERT INTO user_comments (user_id, content, likes, post_ts, deleted) "
        "VALUES (:user_id, :content, :likes, :post_ts, :deleted)",
        comment.as_dict(include_id=False),
    )


# TODO: Partial Update
async def update(ctx: Context, comment: UserComment) -> None:
    await ctx.mysql.execute(
        "UPDATE user_comments SET user_id = :user_id, content = :content, "
        "likes = :likes, post_ts = :post_ts, deleted = :deleted WHERE id = :id",
        comment.as_dict(include_id=True),
    )
