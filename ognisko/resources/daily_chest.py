from __future__ import annotations

from datetime import datetime
from enum import IntEnum

from ognisko.adapters import AbstractMySQLService
from ognisko.common import modelling
from ognisko.resources._common import DatabaseModel


class DailyChestView(IntEnum):
    VIEW = 0
    CLAIM_SMALL = 1
    CLAIM_LARGE = 2

    @property
    def is_claim(self) -> bool:
        return self in (DailyChestView.CLAIM_SMALL, DailyChestView.CLAIM_LARGE)


class DailyChestType(IntEnum):
    SMALL = 0
    LARGE = 1


class DailyChestShardType(IntEnum):
    FIRE = 0
    ICE = 1
    POISON = 2
    SHADOW = 3
    LAVA = 4


class DailyChestRewardType(IntEnum):
    MANA = 0
    DIAMONDS = 1
    FIRE_SHARD = 2
    ICE_SHARD = 3
    POISON_SHARD = 4
    SHADOW_SHARD = 5
    LAVA_SHARD = 6
    DEMON_KEY = 7


class DailyChest(DatabaseModel):
    id: int
    user_id: int
    type: DailyChestType
    mana: int
    diamonds: int
    fire_shards: int
    ice_shards: int
    poison_shards: int
    shadow_shards: int
    lava_shards: int
    demon_keys: int
    claimed_ts: datetime


ALL_FIELDS = modelling.get_model_fields(DailyChest)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


class DailyChestRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: AbstractMySQLService) -> None:
        self._mysql = mysql

    async def from_id(self, chest_id: int) -> DailyChest | None:
        chest_db = await self._mysql.fetch_one(
            "SELECT * FROM daily_chests WHERE id = :chest_id",
            {"chest_id": chest_id},
        )

        if chest_db is None:
            return None

        return DailyChest(**chest_db)

    async def from_user_id_and_type_latest(
        self,
        user_id: int,
        chest_type: DailyChestType,
    ) -> DailyChest | None:
        chest_db = await self._mysql.fetch_one(
            "SELECT * FROM daily_chests WHERE user_id = :user_id AND "
            "type = :chest_type ORDER BY claimed_ts DESC LIMIT 1",
            {"user_id": user_id, "chest_type": chest_type.value},
        )

        if chest_db is None:
            return None

        return DailyChest(**chest_db)

    async def create(
        self,
        user_id: int,
        chest_type: DailyChestType,
        *,
        mana: int = 0,
        diamonds: int = 0,
        fire_shards: int = 0,
        ice_shards: int = 0,
        poison_shards: int = 0,
        shadow_shards: int = 0,
        lava_shards: int = 0,
        demon_keys: int = 0,
        claimed_ts: datetime | None = None,
    ) -> DailyChest:
        if claimed_ts is None:
            claimed_ts = datetime.now()

        model = DailyChest(
            id=0,
            user_id=user_id,
            type=chest_type,
            mana=mana,
            diamonds=diamonds,
            fire_shards=fire_shards,
            ice_shards=ice_shards,
            poison_shards=poison_shards,
            shadow_shards=shadow_shards,
            lava_shards=lava_shards,
            demon_keys=demon_keys,
            claimed_ts=claimed_ts,
        )
        model.id = await self._mysql.execute(
            f"INSERT INTO daily_chests ({_CUSTOMISABLE_FIELDS_COMMA}) "
            f"VALUES ({_CUSTOMISABLE_FIELDS_COLON})",
            model.model_dump(exclude={"id"}),
        )
        return model

    async def sum_mana_from_user_id(
        self,
        user_id: int,
    ) -> int:
        return int(
            await self._mysql.fetch_val(
                "SELECT SUM(mana) FROM daily_chests WHERE user_id = :user_id",
                {"user_id": user_id},
            )
            or 0,
        )

    async def count_of_type(
        self,
        user_id: int,
        chest_type: DailyChestType,
    ) -> int:
        return (
            await self._mysql.fetch_val(
                "SELECT COUNT(*) FROM daily_chests WHERE user_id = :user_id AND type = :chest_type",
                {"user_id": user_id, "chest_type": chest_type.value},
            )
            or 0
        )
