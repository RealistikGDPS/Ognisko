from __future__ import annotations

from typing import Optional

from rgdps.constants.levels import LevelDemonDifficulty
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlags
from rgdps.models.level import Level
from rgdps.state import services


async def from_id(level_id: int) -> Optional[Level]:
    # TODO: Replace with individual columns.
    level_db = await services.database.fetch_one(
        "SELECT name, user_id, description, custom_song_id, official_song_id, "
        "version, length, two_player, publicity, render_str, game_version, "
        "binary_version, upload_ts, original_id, downloads, likes, stars, difficulty, "
        "demon_difficulty, coins, coins_verified, requested_stars, feature_order, "
        "search_flags, low_detail_mode, object_count, copy_password, building_time, "
        "update_locked, deleted FROM levels WHERE id = :id",
        {
            "id": level_id,
        },
    )

    if level_db is None:
        return None

    return Level.from_mapping(level_db)


async def create(level: Level) -> int:
    return await create_sql(level)


async def create_sql(level: Level) -> int:
    return await services.database.execute(
        "INSERT INTO levels (name, user_id, description, custom_song_id, "
        "official_song_id, version, length, two_player, publicity, render_str, "
        "game_version, binary_version, upload_ts, original_id, downloads, likes, "
        "stars, difficulty, demon_difficulty, coins, coins_verified, requested_stars, "
        "feature_order, search_flags, low_detail_mode, object_count, copy_password, "
        "building_time, update_locked, deleted) VALUES (:name, :user_id, "
        ":description, :custom_song_id, :official_song_id, :version, :length, "
        ":two_player, :publicity, :render_str, :game_version, :binary_version, "
        ":upload_ts, :original_id, :downloads, :likes, :stars, :difficulty, "
        ":demon_difficulty, :coins, :coins_verified, :requested_stars, :feature_order, "
        ":search_flags, :low_detail_mode, :object_count, :copy_password, "
        ":building_time, :update_locked, :deleted)",
        level.as_dict(include_id=False),
    )


async def update(level: Level) -> int:
    return await update_sql(level)


async def update_sql(level: Level) -> int:
    return await services.database.execute(
        "UPDATE levels SET name = :name, user_id = :user_id, description = :description, "
        "custom_song_id = :custom_song_id, official_song_id = :official_song_id, "
        "version = :version, length = :length, two_player = :two_player, "
        "publicity = :publicity, render_str = :render_str, game_version = :game_version, "
        "binary_version = :binary_version, upload_ts = :upload_ts, original_id = :original_id, "
        "downloads = :downloads, likes = :likes, stars = :stars, difficulty = :difficulty, "
        "demon_difficulty = :demon_difficulty, coins = :coins, coins_verified = :coins_verified, "
        "requested_stars = :requested_stars, feature_order = :feature_order, "
        "search_flags = :search_flags, low_detail_mode = :low_detail_mode, "
        "object_count = :object_count, copy_password = :copy_password, "
        "building_time = :building_time, update_locked = :update_locked, "
        "deleted = :deleted WHERE id = :id",
        level.as_dict(include_id=True),
    )
