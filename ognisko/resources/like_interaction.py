from __future__ import annotations

from enum import IntEnum

from ognisko.adapters import ImplementsMySQL
from ognisko.common import modelling
from ognisko.resources._common import DatabaseModel


class LikeType(IntEnum):
    LEVEL = 1
    COMMENT = 2
    USER_COMMENT = 3


class LikeInteractionModel(DatabaseModel):
    id: int
    target_type: LikeType
    target_id: int
    user_id: int
    value: int


ALL_FIELDS = modelling.get_model_fields(LikeInteractionModel)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)

_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


class LikeInteractionRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: ImplementsMySQL) -> None:
        self._mysql = mysql

    async def from_id(self, like_id: int) -> LikeInteractionModel | None:
        like_db = await self._mysql.fetch_one(
            "SELECT * FROM user_likes WHERE id = :like_id",
            {
                "like_id": like_id,
            },
        )

        if like_db is None:
            return None

        return LikeInteractionModel(**like_db)

    async def create(
        self,
        target_type: LikeType,
        target_id: int,
        user_id: int,
        value: int,
    ) -> LikeInteractionModel:
        like = LikeInteractionModel(
            id=0,
            target_type=target_type,
            target_id=target_id,
            user_id=user_id,
            value=value,
        )

        like.id = await self._mysql.execute(
            f"INSERT INTO user_likes ({_CUSTOMISABLE_FIELDS_COMMA}) VALUES "
            f"({_CUSTOMISABLE_FIELDS_COLON})",
            like.model_dump(exclude={"id"}),
        )

        return like

    async def exists_from_target_and_user(
        self,
        target_type: LikeType,
        target_id: int,
        user_id: int,
    ) -> bool:
        return (
            await self._mysql.fetch_val(
                "SELECT 1 FROM user_likes WHERE target_type = :target_type AND "
                "target_id = :target_id AND user_id = :user_id",
                {
                    "target_type": target_type.value,
                    "target_id": target_id,
                    "user_id": user_id,
                },
            )
        ) is not None

    async def sum_from_target(
        self,
        target_type: LikeType,
        target_id: int,
    ) -> int:
        return (
            await self._mysql.fetch_val(
                "SELECT SUM(value) FROM user_likes WHERE target_type = :target_type AND target_id = :target_id",
                {
                    "target_type": target_type.value,
                    "target_id": target_id,
                },
            )
        ) or 0
