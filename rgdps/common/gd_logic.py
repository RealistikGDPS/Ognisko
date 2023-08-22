from __future__ import annotations

import random
from typing import NamedTuple

from rgdps.constants.daily_chests import DailyChestRewardType
from rgdps.constants.levels import LevelSearchFlag
from rgdps.models.level import Level


def calculate_creator_points(level: Level) -> int:
    creator_points = 0

    # One for a rated level
    if level.stars > 0:
        creator_points += 1

    # One for a featured level
    if level.feature_order > 0:
        creator_points += 1

    # One for being rated epic
    if level.search_flags & LevelSearchFlag.EPIC:
        creator_points += 1

    return creator_points


class ChestReward(NamedTuple):
    type: DailyChestRewardType
    amount: int


# NOTE: Amounts have been estimated based on observation. May not be accurate.
SMALL_CHEST_MANA = [
    20,
    25,
    30,
    35,
    45,
    50,
]
SMALL_CHEST_DIAMONDS = [1, 2, 3, 4]


def get_small_chest() -> list[ChestReward]:
    mana = random.choice(SMALL_CHEST_MANA)
    diamonds = random.choice(SMALL_CHEST_DIAMONDS)

    return [
        ChestReward(DailyChestRewardType.MANA, mana),
        ChestReward(DailyChestRewardType.DIAMONDS, diamonds),
    ]


LARGE_CHEST_MANA = [
    100,
    150,
    200,
    300,
    400,
]
POSSIBLE_SHARDS = [
    DailyChestRewardType.FIRE_SHARD,
    DailyChestRewardType.ICE_SHARD,
    DailyChestRewardType.POISON_SHARD,
    DailyChestRewardType.SHADOW_SHARD,
    DailyChestRewardType.LAVA_SHARD,
]
MORE_DIAMONDS_CHANCE = 20
SHARD_CHANCE = 50
MAX_SHARDS = 2


def get_large_chest() -> list[ChestReward]:
    rewards = [ChestReward(DailyChestRewardType.MANA, random.choice(LARGE_CHEST_MANA))]

    diamonds = 4
    if random.randint(0, 100) < MORE_DIAMONDS_CHANCE:
        diamonds = 10

    rewards.append(ChestReward(DailyChestRewardType.DIAMONDS, diamonds))

    for _ in range(MAX_SHARDS):
        if random.randint(0, 100) < SHARD_CHANCE:
            rewards.append(ChestReward(random.choice(POSSIBLE_SHARDS), 1))

    return rewards
