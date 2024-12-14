from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class UserRelationshipType(StrEnum):
    FRIEND = "FRIEND"
    BLOCKED = "BLOCKED"


class UserRelationshipModel(DatabaseModel):
    __tablename__ = "user_relationships"

    relationship_type = Column(Enum(UserRelationshipType), nullable=False)
    user_id = Column(Integer, nullable=False)
    target_user_id = Column(Integer, nullable=False)
    posted_at = Column(DateTime, nullable=False, default=datetime.now)
    seen_at = Column(DateTime, nullable=True, default=None)


DEFAULT_PAGE_SIZE = 10


class UserRelationshipRepository(BaseRepository[UserRelationshipModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, UserRelationshipModel)

    async def from_user_id(
        self,
        user_id: int,
        *,
        include_deleted: bool = False,
    ) -> list[UserRelationshipModel]:
        query = self._mysql.select(UserRelationshipModel).where(
            UserRelationshipModel.user_id == user_id,
        )
        if not include_deleted:
            query = query.where(UserRelationshipModel.deleted_at.is_(None))
        return await query.fetch_all()
