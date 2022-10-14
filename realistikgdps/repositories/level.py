from __future__ import annotations

from typing import Optional

from realistikgdps.constants.levels import LevelDemonDifficulty
from realistikgdps.constants.levels import LevelDifficulty
from realistikgdps.constants.levels import LevelLength
from realistikgdps.constants.levels import LevelPublicity
from realistikgdps.constants.levels import LevelSearchFlags
from realistikgdps.models.level import Level
from realistikgdps.state import services


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

    demon_difficulty = None
    if level_db["demon_difficulty"] is not None:
        demon_difficulty = LevelDemonDifficulty(level_db["demon_difficulty"])

    return Level(
        id=level_id,
        name=level_db["name"],
        user_id=level_db["user_id"],
        description=level_db["description"],
        custom_song_id=level_db["custom_song_id"],
        official_song_id=level_db["official_song_id"],
        version=level_db["version"],
        length=LevelLength(level_db["length"]),
        two_player=level_db["two_player"],
        publicity=LevelPublicity(level_db["publicity"]),
        render_str=level_db["render_str"],
        game_version=level_db["game_version"],
        binary_version=level_db["binary_version"],
        upload_ts=level_db["upload_ts"],
        original_id=level_db["original_id"],
        downloads=level_db["downloads"],
        likes=level_db["likes"],
        stars=level_db["stars"],
        difficulty=LevelDifficulty(level_db["difficulty"]),
        demon_difficulty=demon_difficulty,
        coins=level_db["coins"],
        coins_verified=level_db["coins_verified"],
        requested_stars=level_db["requested_stars"],
        feature_order=level_db["feature_order"],
        search_flags=LevelSearchFlags(level_db["search_flags"]),
        low_detail_mode=level_db["low_detail_mode"],
        object_count=level_db["object_count"],
        copy_password=level_db["copy_password"],
        building_time=level_db["building_time"],
        update_locked=level_db["update_locked"],
        deleted=level_db["deleted"],
    )


async def create(level: Level) -> int:
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
        {
            "name": level.name,
            "user_id": level.user_id,
            "description": level.description,
            "custom_song_id": level.custom_song_id,
            "official_song_id": level.official_song_id,
            "version": level.version,
            "length": level.length.value,
            "two_player": level.two_player,
            "publicity": level.publicity.value,
            "render_str": level.render_str,
            "game_version": level.game_version,
            "binary_version": level.binary_version,
            "upload_ts": level.upload_ts,
            "original_id": level.original_id,
            "downloads": level.downloads,
            "likes": level.likes,
            "stars": level.stars,
            "difficulty": level.difficulty.value,
            "demon_difficulty": level.demon_difficulty.value
            if level.demon_difficulty is not None
            else None,
            "coins": level.coins,
            "coins_verified": level.coins_verified,
            "requested_stars": level.requested_stars,
            "feature_order": level.feature_order,
            "search_flags": level.search_flags.value,
            "low_detail_mode": level.low_detail_mode,
            "object_count": level.object_count,
            "copy_password": level.copy_password,
            "building_time": level.building_time,
            "update_locked": level.update_locked,
            "deleted": level.deleted,
        },
    )
