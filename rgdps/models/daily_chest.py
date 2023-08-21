from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Mapping

from rgdps.constants.daily_chests import DailyChestType


@dataclass
class DailyChest:
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
    keys: int
    claimed_ts: datetime

    @staticmethod
    def from_mapping(mapping: Mapping[str, Any]) -> DailyChest:
        return DailyChest(
            id=mapping["id"],
            user_id=mapping["user_id"],
            type=DailyChestType(mapping["type"]),
            mana=mapping["mana"],
            diamonds=mapping["diamonds"],
            fire_shards=mapping["fire_shards"],
            ice_shards=mapping["ice_shards"],
            poison_shards=mapping["poison_shards"],
            shadow_shards=mapping["shadow_shards"],
            lava_shards=mapping["lava_shards"],
            keys=mapping["keys"],
            claimed_ts=mapping["claimed_ts"],
        )

    def as_dict(self, *, include_id: bool = True) -> dict[str, Any]:
        mapping = {
            "user_id": self.user_id,
            "type": self.type.value,
            "mana": self.mana,
            "diamonds": self.diamonds,
            "fire_shards": self.fire_shards,
            "ice_shards": self.ice_shards,
            "poison_shards": self.poison_shards,
            "shadow_shards": self.shadow_shards,
            "lava_shards": self.lava_shards,
            "keys": self.keys,
            "claimed_ts": self.claimed_ts,
        }

        if include_id:
            mapping["id"] = self.id or None

        return mapping
