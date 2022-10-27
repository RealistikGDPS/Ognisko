from __future__ import annotations

from typing import Optional

from rgdps.models.user_comment import UserComment
from rgdps.state import services


async def from_id(comment_id: int) -> Optional[UserComment]:
    comment_db = await services.database.fetch_one(
        "SELECT id, user_id, content, likes, post_ts, deleted "
        "FROM user_comments WHERE id = :id",
        {"id": comment_id},
    )

    if comment_db is None:
        return None

    return UserComment(
        id=comment_db["id"],
        user_id=comment_db["user_id"],
        content=comment_db["content"],
        likes=comment_db["likes"],
        post_ts=comment_db["post_ts"],
        deleted=comment_db["deleted"],
    )


# XXX: This bool might be bad design?
async def from_user_id(
    user_id: int,
    include_deleted: bool = False,
) -> list[UserComment]:
    comments_db = await services.database.fetch_all(
        "SELECT id, user_id, content, likes, post_ts, deleted FROM "
        "user_comments WHERE user_id = :user_id AND deleted = :deleted",
        {"user_id": user_id, "deleted": include_deleted},
    )

    return [
        UserComment(
            id=comment_db["id"],
            user_id=comment_db["user_id"],
            content=comment_db["content"],
            likes=comment_db["likes"],
            post_ts=comment_db["post_ts"],
            deleted=comment_db["deleted"],
        )
        for comment_db in comments_db
    ]


async def from_user_id_paginated(
    user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> list[UserComment]:
    comments_db = await services.database.fetch_all(
        "SELECT id, user_id, content, likes, post_ts, deleted FROM "
        "user_comments WHERE user_id = :user_id AND deleted = :deleted "
        "ORDER BY id DESC LIMIT :limit OFFSET :offset",
        {
            "user_id": user_id,
            "deleted": include_deleted,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [
        UserComment(
            id=comment_db["id"],
            user_id=comment_db["user_id"],
            content=comment_db["content"],
            likes=comment_db["likes"],
            post_ts=comment_db["post_ts"],
            deleted=comment_db["deleted"],
        )
        for comment_db in comments_db
    ]


async def create(comment: UserComment) -> int:
    return await services.database.execute(
        "INSERT INTO user_comments (user_id, content, likes, post_ts, deleted) "
        "VALUES (:user_id, :content, :likes, :post_ts, :deleted)",
        {
            "user_id": comment.user_id,
            "content": comment.content,
            "likes": comment.likes,
            "post_ts": comment.post_ts,
            "deleted": comment.deleted,
        },
    )


# TODO: Partial Update
async def update(comment: UserComment) -> None:
    await services.database.execute(
        "UPDATE user_comments SET user_id = :user_id, content = :content, "
        "likes = :likes, post_ts = :post_ts, deleted = :deleted WHERE id = :id",
        {
            "user_id": comment.user_id,
            "content": comment.content,
            "likes": comment.likes,
            "post_ts": comment.post_ts,
            "deleted": comment.deleted,
            "id": comment.id,
        },
    )


async def count_from_user_id(user_id: int) -> int:
    return await services.database.fetch_val(
        "SELECT COUNT(*) FROM user_comments WHERE user_id = :user_id "
        "AND deleted = 0",
        {"user_id": user_id},
    )
