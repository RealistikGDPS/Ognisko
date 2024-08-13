from __future__ import annotations

from datetime import datetime
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from rgdps.adapters import AbstractMySQLService
from rgdps.common import modelling
from rgdps.resources._common import DatabaseModel


class UserComment(DatabaseModel):
    id: int
    user_id: int
    content: str
    likes: int
    post_ts: datetime
    deleted: bool


class _UserCommentUpdatePartial(TypedDict):
    user_id: NotRequired[int]
    content: NotRequired[str]
    likes: NotRequired[int]
    post_ts: NotRequired[datetime]
    deleted: NotRequired[bool]


ALL_FIELDS = modelling.get_model_fields(UserComment)
_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)


class UserCommentRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: AbstractMySQLService) -> None:
        self._mysql = mysql

    async def from_id(self, comment_id: int) -> UserComment | None:
        comment_db = await self._mysql.fetch_one(
            "SELECT * FROM user_comments WHERE id = :comment_id",
            {
                "comment_id": comment_id,
            },
        )

        if comment_db is None:
            return None

        return UserComment(**comment_db)

    async def from_user_id(
        self,
        user_id: int,
        *,
        include_deleted: bool = False,
    ) -> list[UserComment]:
        comments_db = self._mysql.iterate(
            "SELECT * FROM user_comments WHERE user_id = :user_id "
            "AND deleted IN :deleted",
            {
                "user_id": user_id,
                "deleted": (0, 1) if include_deleted else (0,),
            },
        )

        return [UserComment(**comment_db) async for comment_db in comments_db]

    async def from_user_id_paginated(
        self,
        user_id: int,
        *,
        page: int,
        page_size: int,
        include_deleted: bool = False,
    ) -> list[UserComment]:
        condition = ""
        if not include_deleted:
            condition = "AND NOT deleted"

        comments_db = await self._mysql.fetch_all(
            f"SELECT * FROM user_comments WHERE user_id = :user_id {condition} "
            "ORDER BY id DESC LIMIT :limit OFFSET :offset",
            {
                "user_id": user_id,
                "limit": page_size,
                "offset": page * page_size,
            },
        )

        return [UserComment(**comment_db) for comment_db in comments_db]

    async def count_from_user_id(
        self,
        user_id: int,
        *,
        include_deleted: bool = False,
    ) -> int:
        return (
            await self._mysql.fetch_val(
                "SELECT COUNT(*) FROM user_comments WHERE user_id = :user_id "
                "AND deleted IN :deleted",
                {
                    "user_id": user_id,
                    "deleted": (0, 1) if include_deleted else (0,),
                },
            )
        ) or 0

    async def create(
        self,
        user_id: int,
        content: str,
        likes: int = 0,
        post_ts: datetime | None = None,
        deleted: bool = False,
        *,
        comment_id: int | None = None,
    ) -> UserComment:
        model = UserComment(
            id=0,
            user_id=user_id,
            content=content,
            likes=likes,
            post_ts=post_ts or datetime.now(),
            deleted=deleted,
        )

        model_dump = model.model_dump()
        model_dump["id"] = comment_id

        model.id = await self._mysql.execute(
            f"INSERT INTO user_comments ({_ALL_FIELDS_COMMA}) VALUES "
            f"({_ALL_FIELDS_COLON})",
            model_dump,
        )
        return model

    async def update_partial(
        self,
        comment_id: int,
        **kwargs: Unpack[_UserCommentUpdatePartial],
    ) -> UserComment | None:
        changed_fields = modelling.unpack_enum_types(kwargs)

        await self._mysql.execute(
            modelling.update_from_partial_dict(
                "user_comments",
                comment_id,
                changed_fields,
            ),
            changed_fields,
        )
        return await self.from_id(comment_id)

    async def count_all(self) -> int:
        return (await self._mysql.fetch_val("SELECT COUNT(*) FROM user_comments")) or 0
