from __future__ import annotations

import random
import base64
from typing import NamedTuple

from rgdps.utilities import cryptography
from rgdps.resources import DailyChestRewardType


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
MORE_DIAMONDS_CHANCE = 10
SHARD_CHANCE = 50
MAX_SHARDS = 2
LOW_DIAMONDS_ROLL = [4, 5]

def generate_small_chest() -> list[ChestReward]:
    mana = random.choice(SMALL_CHEST_MANA)
    diamonds = random.choice(SMALL_CHEST_DIAMONDS)

    return [
        ChestReward(DailyChestRewardType.MANA, mana),
        ChestReward(DailyChestRewardType.DIAMONDS, diamonds),
    ]

def generate_large_chest() -> list[ChestReward]:
    rewards = [ChestReward(DailyChestRewardType.MANA, random.choice(LARGE_CHEST_MANA))]

    diamonds = random.choice(LOW_DIAMONDS_ROLL)
    if random.randint(0, 100) < MORE_DIAMONDS_CHANCE:
        diamonds = 10

    rewards.append(ChestReward(DailyChestRewardType.DIAMONDS, diamonds))

    for _ in range(MAX_SHARDS):
        if random.randint(0, 100) < SHARD_CHANCE:
            rewards.append(ChestReward(random.choice(POSSIBLE_SHARDS), 1))

    return rewards


CHEST_XOR_KEY = b"59182"

def encrypt_chests(response: str) -> str:
    return base64.urlsafe_b64encode(
        xor_cipher.cyclic_xor_unsafe(
            data=response.encode(),
            key=CHEST_XOR_KEY,
        ),
    ).decode()


def decrypt_chest_check(check_string: str) -> str:
    valid_check = check_string[5:]
    de_b64 = cryptography.decode_base64(valid_check)

    return xor_cipher.cyclic_xor_unsafe(
        data=de_b64.encode(),
        key=CHEST_XOR_KEY,
    ).decode()
