from __future__ import annotations

from datetime import datetime
from enum import IntEnum

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class DailyChestView(IntEnum):
    VIEW = 0
    CLAIM_SMALL = 1
    CLAIM_LARGE = 2

    @property
    def is_claim(self) -> bool:
        return self in (DailyChestView.CLAIM_SMALL, DailyChestView.CLAIM_LARGE)


class DailyChestTier(StrEnum):
    SMALL = "small"
    LARGE = "large"


class DailyChestShardType(StrEnum):
    FIRE = "fire"
    ICE = "ice"
    POISON = "poison"
    SHADOW = "shadow"
    LAVA = "lava"


class DailyChestRewardType(StrEnum):
    MANA = "mana"
    DIAMONDS = "diamonds"
    FIRE_SHARD = "fire_shard"
    ICE_SHARD = "ice_shard"
    POISON_SHARD = "poison_shard"
    SHADOW_SHARD = "shadow_shard"
    LAVA_SHARD = "lava_shard"
    DEMON_KEY = "demon_key"


class DailyChestModel(DatabaseModel):
    __tablename__ = "daily_chests"

    user_id = Column(Integer, nullable=False)
    tier = Column(Enum(DailyChestTier), nullable=False)

    mana_count = Column(Integer, nullable=False)
    diamond_count = Column(Integer, nullable=False)
    fire_shard_count = Column(Integer, nullable=False)
    ice_shard_count = Column(Integer, nullable=False)
    poison_shard_count = Column(Integer, nullable=False)
    shadow_shard_count = Column(Integer, nullable=False)
    lava_shard_count = Column(Integer, nullable=False)
    demon_key_count = Column(Integer, nullable=False)

    claimed_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DailyChestRepository(BaseRepository[DailyChestModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, DailyChestModel)

    async def from_user_id_and_type_latest(
        self,
        user_id: int,
        chest_type: DailyChestTier,
    ) -> DailyChestModel | None:
        return (
            await self._mysql.select(DailyChestModel)
            .where(
                DailyChestModel.user_id == user_id,
                DailyChestModel.tier == chest_type,
            )
            .order_by(DailyChestModel.claimed_at.desc())
            .fetch_one()
        )

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
        chest_type: DailyChestTier,
    ) -> int:
        return (
            await self._mysql.fetch_val(
                "SELECT COUNT(*) FROM daily_chests WHERE user_id = :user_id AND type = :chest_type",
                {"user_id": user_id, "chest_type": chest_type.value},
            )
            or 0
        )
