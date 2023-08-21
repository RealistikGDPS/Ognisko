from __future__ import annotations

from enum import IntEnum


class DailyChestView(IntEnum):
    VIEW = 0
    CLAIM_SMALL = 1
    CLAIM_LARGE = 2


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
    KEY = 7
