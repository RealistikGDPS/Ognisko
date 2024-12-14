from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel


class UserProfileCommentModel(DatabaseModel):
    __tablename__ = "user_profile_comments"

    user_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    likes = Column(Integer, nullable=False)
    posted_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)


class UserProfileCommentRepository(BaseRepository[UserProfileCommentModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, UserProfileCommentModel)

    async def from_user_id(
        self,
        user_id: int,
    ) -> list[UserProfileCommentModel]:
        query = self._mysql.select(UserProfileCommentModel).where(
            UserProfileCommentModel.user_id == user_id,
        )
        return await query.fetch_all()

    async def from_user_id_paginated(
        self,
        user_id: int,
        page: int,
        page_size: int,
        *,
        include_deleted: bool = False,
    ) -> list[UserProfileCommentModel]:
        query = self._mysql.select(UserProfileCommentModel).where(
            UserProfileCommentModel.user_id == user_id,
        )
        if not include_deleted:
            query = query.where(UserProfileCommentModel.deleted.is_(False))

        return await query.paginate(page, page_size)
