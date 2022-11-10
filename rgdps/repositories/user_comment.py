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

    return UserComment.from_mapping(comment_db)


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

    return [UserComment.from_mapping(comment_db) for comment_db in comments_db]


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

    return [UserComment.from_mapping(comment_db) for comment_db in comments_db]


async def create(comment: UserComment) -> int:
    return await services.database.execute(
        "INSERT INTO user_comments (user_id, content, likes, post_ts, deleted) "
        "VALUES (:user_id, :content, :likes, :post_ts, :deleted)",
        comment.as_dict(),
    )


# TODO: Partial Update
async def update(comment: UserComment) -> None:
    await services.database.execute(
        "UPDATE user_comments SET user_id = :user_id, content = :content, "
        "likes = :likes, post_ts = :post_ts, deleted = :deleted WHERE id = :id",
        comment.as_dict(),
    )


async def count_from_user_id(user_id: int) -> int:
    return await services.database.fetch_val(
        "SELECT COUNT(*) FROM user_comments WHERE user_id = :user_id "
        "AND deleted = 0",
        {"user_id": user_id},
    )
