from __future__ import annotations

from typing import Optional

from rgdps.constants.likes import LikeType
from rgdps.models.like import Like
from rgdps.state import services


async def from_id(id: int) -> Optional[Like]:
    like_db = await services.database.fetch_one(
        "SELECT target_type, target_id, user_id, value FROM likes WHERE id = :id",
        {
            "id": id,
        },
    )

    if like_db is None:
        return None

    return Like.from_mapping(like_db)


async def create(like: Like) -> int:
    return await services.database.execute(
        "INSERT INTO likes (target_type, target_id, user_id, value) VALUES "
        "(:target_type, :target_id, :user_id, :value)",
        like.as_dict(),
    )


async def exists_by_target_and_user(
    target_type: LikeType,
    target_id: int,
    user_id: int,
) -> bool:
    return (
        await services.database.fetch_one(
            "SELECT id FROM likes WHERE target_type = :target_type AND target_id = :target_id AND user_id = :user_id",
            {
                "target_type": target_type.value,
                "target_id": target_id,
                "user_id": user_id,
            },
        )
        is not None
    )


async def sum_by_target(
    target_type: LikeType,
    target_id: int,
) -> int:
    like_db = await services.database.fetch_one(
        "SELECT SUM(value) AS sum FROM likes WHERE target_type = :target_type "
        "AND target_id = :target_id",
        {
            "target_type": target_type.value,
            "target_id": target_id,
        },
    )

    if like_db is None:
        return 0

    return like_db["sum"]


async def update_value(
    like_id: int,
    value: int,
) -> None:
    await services.database.execute(
        "UPDATE likes SET value = :value WHERE id = :id",
        {
            "id": like_id,
            "value": value,
        },
    )
