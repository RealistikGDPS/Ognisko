from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.adapters.mysql import _SelectWrapper
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class LevelCommentModel(DatabaseModel):
    user_id = Column(Integer, nullable=False)
    level_id = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    percent_achieved = Column(Integer, nullable=True)
    likes = Column(Integer, nullable=False, default=0)
    posted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


class LevelCommentSorting(StrEnum):
    NEWEST = "newest"
    MOST_LIKED = "most_liked"


def _sort_query_by_sorting(
    query: _SelectWrapper,
    sorting: LevelCommentSorting,
) -> _SelectWrapper:
    if sorting == LevelCommentSorting.MOST_LIKED:
        return query.order_by(LevelCommentModel.likes.desc())

    return query.order_by(LevelCommentModel.posted_at.desc())


class LevelCommentRepository(BaseRepository[LevelCommentModel]):
    __slots__ = ("_mysql",)

    def __init__(self, mysql: ImplementsMySQL) -> None:
        self._mysql = mysql

    async def from_level_id_paginated(
        self,
        level_id: int,
        page: int,
        page_size: int,
        *,
        sorting: LevelCommentSorting = LevelCommentSorting.NEWEST,
        include_deleted: bool = False,
    ) -> list[LevelCommentModel]:
        query = self._mysql.select(LevelCommentModel).where(
            LevelCommentModel.level_id == level_id,
        )
        if not include_deleted:
            query = query.where(LevelCommentModel.deleted_at.is_(None))

        _sort_query_by_sorting(query, sorting)

        return await query.paginate(page, page_size)

    async def from_user_id_paginated(
        self,
        user_id: int,
        page: int,
        page_size: int,
        *,
        sorting: LevelCommentSorting = LevelCommentSorting.NEWEST,
        include_deleted: bool = False,
    ) -> list[LevelCommentModel]:
        query = self._mysql.select(LevelCommentModel).where(
            LevelCommentModel.user_id == user_id,
        )

        if not include_deleted:
            query = query.where(LevelCommentModel.deleted_at.is_(None))

        _sort_query_by_sorting(query, sorting)

        return await query.paginate(page, page_size)

    async def count_from_level_id(self, level_id: int) -> int:
        return await self._mysql.fetch_val(
            "SELECT COUNT(*) FROM level_comments WHERE level_id = :level_id "
            "AND deleted = 0",
            {"level_id": level_id},
        )

    async def count_from_user_id(self, user_id: int) -> int:
        return await self._mysql.fetch_val(
            "SELECT COUNT(*) FROM level_comments WHERE user_id = :user_id "
            "AND deleted = 0",
            {"user_id": user_id},
        )
