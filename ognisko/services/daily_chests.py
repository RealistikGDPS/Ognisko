from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import NamedTuple

from ognisko.helpers.chest import generate_large_chest
from ognisko.helpers.chest import generate_small_chest
from ognisko.resources import Context
from ognisko.resources import DailyChestModel
from ognisko.resources import DailyChestRewardType
from ognisko.resources import DailyChestTier
from ognisko.resources import DailyChestView
from ognisko.services._common import ServiceError


class DailyChestInformation(NamedTuple):
    small_chest_time_remaining: timedelta
    large_chest_time_remaining: timedelta

    small_chest_count: int
    large_chest_count: int

    chest: DailyChestModel | None


SMALL_CHEST_TIME = timedelta(hours=2)
LARGE_CHEST_TIME = timedelta(hours=24)


# NOTE: This handles both just viewing and claiming a chest as GD handles
# both in a single endpoint.
async def view(
    ctx: Context,
    user_id: int,
    view: DailyChestView,
) -> DailyChestInformation | ServiceError:
    last_small_chest = await ctx.daily_chests.from_user_id_and_type_latest(
        user_id,
        DailyChestTier.SMALL,
    )
    last_large_chest = await ctx.daily_chests.from_user_id_and_type_latest(
        user_id,
        DailyChestTier.LARGE,
    )

    small_chest_count = await ctx.daily_chests.count_of_type(
        user_id,
        DailyChestTier.SMALL,
    )
    large_chest_count = await ctx.daily_chests.count_of_type(
        user_id,
        DailyChestTier.LARGE,
    )

    # Calculate the delays.
    current_ts = datetime.now()
    if last_small_chest:
        small_chest_time_remaining = SMALL_CHEST_TIME - (
            current_ts - last_small_chest.claimed_at
        )
        if small_chest_time_remaining < timedelta():
            small_chest_time_remaining = timedelta()
    else:
        small_chest_time_remaining = timedelta()

    if last_large_chest:
        large_chest_time_remaining = LARGE_CHEST_TIME - (
            current_ts - last_large_chest.claimed_at
        )
        if large_chest_time_remaining < timedelta():
            large_chest_time_remaining = timedelta()
    else:
        large_chest_time_remaining = timedelta()

    if not view.is_claim:
        return DailyChestInformation(
            small_chest_time_remaining,
            large_chest_time_remaining,
            small_chest_count,
            large_chest_count,
            None,
        )

    # Rewards
    mana = 0
    diamonds = 0
    fire_shards = 0
    ice_shards = 0
    poison_shards = 0
    shadow_shards = 0
    lava_shards = 0
    demon_keys = 0

    if view is DailyChestView.CLAIM_LARGE:
        if large_chest_time_remaining > timedelta():
            return ServiceError.DAILY_CHESTS_ALREADY_CLAIMED

        loot_table = generate_large_chest
        chest_type = DailyChestTier.LARGE
        large_chest_count += 1
        large_chest_time_remaining = LARGE_CHEST_TIME

    else:
        if small_chest_time_remaining > timedelta():
            return ServiceError.DAILY_CHESTS_ALREADY_CLAIMED

        loot_table = generate_small_chest
        chest_type = DailyChestTier.SMALL
        small_chest_count += 1
        small_chest_time_remaining = SMALL_CHEST_TIME

    rewards = loot_table()

    for reward in rewards:
        match reward.type:
            case DailyChestRewardType.MANA:
                mana += reward.amount
            case DailyChestRewardType.DIAMONDS:
                diamonds += reward.amount
            case DailyChestRewardType.FIRE_SHARD:
                fire_shards += reward.amount
            case DailyChestRewardType.ICE_SHARD:
                ice_shards += reward.amount
            case DailyChestRewardType.POISON_SHARD:
                poison_shards += reward.amount
            case DailyChestRewardType.SHADOW_SHARD:
                shadow_shards += reward.amount
            case DailyChestRewardType.LAVA_SHARD:
                lava_shards += reward.amount
            case DailyChestRewardType.DEMON_KEY:
                demon_keys += reward.amount

    # Award a key for every 500 mana the player gets.
    total_mana = await ctx.daily_chests.sum_mana_from_user_id(user_id)
    total_keys = total_mana // 500

    new_total_keys = (total_mana + mana) // 500

    if new_total_keys > total_keys:
        demon_keys += new_total_keys - total_keys

    # Chest logging
    chest = await ctx.daily_chests.create(
        DailyChestModel.user_id << user_id,
        DailyChestModel.tier << chest_type,
        DailyChestModel.mana_count << mana,
        DailyChestModel.diamond_count << diamonds,
        DailyChestModel.fire_shard_count << fire_shards,
        DailyChestModel.ice_shard_count << ice_shards,
        DailyChestModel.poison_shard_count << poison_shards,
        DailyChestModel.shadow_shard_count << shadow_shards,
        DailyChestModel.lava_shard_count << lava_shards,
        DailyChestModel.demon_key_count << demon_keys,
        DailyChestModel.claimed_at << datetime.now(),
    )

    return DailyChestInformation(
        small_chest_time_remaining,
        large_chest_time_remaining,
        small_chest_count,
        large_chest_count,
        chest,
    )
