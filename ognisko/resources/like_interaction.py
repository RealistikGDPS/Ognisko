from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class LikedResource(StrEnum):
    LEVEL = "LEVEL"
    COMMENT = "COMMENT"
    USER_COMMENT = "USER_COMMENT"


class LikeInteractionModel(DatabaseModel):
    __tablename__ = "like_interactions"

    target_resource = Column(Enum(LikedResource), nullable=False)
    resource_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    value = Column(Integer, nullable=False)


class LikeInteractionRepository(BaseRepository[LikeInteractionModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, LikeInteractionModel)

    async def exists_from_target_and_user(
        self,
        resource_type: LikedResource,
        resource_id: int,
        user_id: int,
    ) -> bool:
        return (
            await self._mysql.fetch_val(
                "SELECT 1 FROM like_interactions WHERE target_type = :target_type AND "
                "target_id = :target_id AND user_id = :user_id",
                {
                    "target_type": resource_type.value,
                    "target_id": resource_id,
                    "user_id": user_id,
                },
            )
        ) is not None

    async def sum_from_target(
        self,
        resource_type: LikedResource,
        resource_id: int,
    ) -> int:
        return (
            await self._mysql.fetch_val(
                "SELECT SUM(value) FROM like_interactions WHERE target_type = :target_type AND target_id = :target_id",
                {
                    "target_type": resource_type.value,
                    "target_id": resource_id,
                },
            )
        ) or 0
