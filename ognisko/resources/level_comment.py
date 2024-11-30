from __future__ import annotations

from datetime import datetime
from typing import NotRequired
from typing import TypedDict

from ognisko.adapters import AbstractMySQLService
from ognisko.common import modelling
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class LevelCommentModel(DatabaseModel):
    id: int
    user_id: int
    level_id: int
    content: str
    percent_achieved: int | None
    likes: int
    posted_ts: datetime
    deleted: bool


class _LevelCommentUpdatePartial(TypedDict):
    user_id: NotRequired[int]
    level_id: NotRequired[int]
    content: NotRequired[str]
    percent: NotRequired[int]
    likes: NotRequired[int]
    post_ts: NotRequired[datetime]
    deleted: NotRequired[bool]


class LevelCommentSorting(StrEnum):
    NEWEST = "newest"
    MOST_LIKED = "most_liked"


ALL_FIELDS = modelling.get_model_fields(LevelCommentModel)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)

_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)

_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


class LevelCommentRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: AbstractMySQLService) -> None:
        self._mysql = mysql

    async def from_id(self, comment_id: int) -> LevelCommentModel | None:
        comment_db = await self._mysql.fetch_one(
            f"SELECT * FROM level_comments WHERE id = :comment_id",
            {"comment_id": comment_id},
        )

        if comment_db is None:
            return None

        return LevelCommentModel(**comment_db)

    async def from_level_id_paginated(
        self,
        level_id: int,
        page: int,
        page_size: int,
        *,
        sorting: LevelCommentSorting = LevelCommentSorting.NEWEST,
        include_deleted: bool = False,
    ) -> list[LevelCommentModel]:
        ordering = "post_ts DESC"
        if sorting == LevelCommentSorting.MOST_LIKED:
            ordering = "likes DESC"
        elif sorting == LevelCommentSorting.NEWEST:
            ordering = "post_ts DESC"

        comments_db = await self._mysql.fetch_all(
            f"SELECT * FROM level_comments WHERE level_id = :level_id "
            f"AND deleted IN :deleted ORDER BY {ordering} LIMIT :page_size "
            "OFFSET :offset",
            {
                "level_id": level_id,
                "page_size": page_size,
                "offset": page * page_size,
                "deleted": (0, 1) if include_deleted else (0,),
            },
        )

        return [LevelCommentModel(**comment_db) for comment_db in comments_db]

    async def from_user_id_paginated(
        self,
        user_id: int,
        page: int,
        page_size: int,
        *,
        sorting: LevelCommentSorting = LevelCommentSorting.NEWEST,
        include_deleted: bool = False,
    ) -> list[LevelCommentModel]:
        ordering = "post_ts DESC"
        if sorting == LevelCommentSorting.MOST_LIKED:
            ordering = "likes DESC"
        elif sorting == LevelCommentSorting.NEWEST:
            ordering = "post_ts DESC"

        comments_db = await self._mysql.fetch_all(
            f"SELECT * FROM level_comments WHERE user_id = :user_id "
            f"AND deleted IN :deleted ORDER BY {ordering} LIMIT :page_size "
            "OFFSET :offset",
            {
                "user_id": user_id,
                "page_size": page_size,
                "offset": page * page_size,
                "deleted": (0, 1) if include_deleted else (0,),
            },
        )

        return [LevelCommentModel(**comment_db) for comment_db in comments_db]

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

    async def create(
        self,
        user_id: int,
        level_id: int,
        content: str,
        percent: int,
        post_ts: datetime | None = None,
    ) -> LevelCommentModel:
        if post_ts is None:
            post_ts = datetime.now()

        comment = LevelCommentModel(
            id=0,
            user_id=user_id,
            level_id=level_id,
            content=content,
            percent_achieved=percent,
            likes=0,
            posted_ts=post_ts,
            deleted=False,
        )

        comment.id = await self._mysql.execute(
            f"INSERT INTO level_comments ({_CUSTOMISABLE_FIELDS_COMMA}) "
            f"VALUES ({_CUSTOMISABLE_FIELDS_COLON})",
            comment.model_dump(exclude={"id"}),
        )

        return comment
