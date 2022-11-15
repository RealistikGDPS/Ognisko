from __future__ import annotations

import time
from datetime import datetime
from typing import Any
from typing import NamedTuple
from typing import Optional

from rgdps.models.level import Level
from rgdps.state import services


async def from_id(level_id: int) -> Optional[Level]:
    # TODO: Replace with individual columns.
    level_db = await services.database.fetch_one(
        "SELECT id, name, user_id, description, custom_song_id, official_song_id, "
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
    level_id = await create_sql(level)
    await create_meili(level, level_id)
    return level_id


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


# Functions to assist with meili not liking datetime objects.
def _make_meili_dict(level: Level) -> dict[str, Any]:
    unix_ts = int(time.mktime(level.upload_ts.timetuple()))
    level_dict = level.as_dict(include_id=True)
    level_dict["upload_ts"] = unix_ts
    return level_dict


def _from_meili_dict(level_dict: dict[str, Any]) -> Level:
    # Meili returns unix timestamps, so we need to convert them back to datetime.
    level_dict["upload_ts"] = datetime.fromtimestamp(level_dict["upload_ts"])
    return Level.from_mapping(level_dict)


async def create_meili(level: Level, level_id: int) -> None:
    # This is a bit hacky as we do not have the level ID in the level object yet.
    level_dict = _make_meili_dict(level)
    level_dict["id"] = level_id

    index = services.meili.index("levels")
    await index.add_documents([level_dict])


async def update(level: Level) -> None:
    # In case sql fails, we do not want to update meili.
    await update_sql(level)
    await update_meili(level)


async def update_meili(level: Level) -> None:
    index = services.meili.index("levels")
    # Fun fact, this is EXACTLY the same as `add_documents`.
    await index.update_documents([_make_meili_dict(level)])


async def update_sql(level: Level) -> None:
    await services.database.execute(
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


class SearchResults(NamedTuple):
    results: list[Level]
    total: int


# Simple search, no filters for testing rn.
async def search_text(
    query: str,
    page: int,
    page_size: int,
) -> SearchResults:
    offset = page * page_size
    index = services.meili.index("levels")
    results_db = await index.search(query, offset=offset, limit=page_size)

    results = [_from_meili_dict(result) for result in results_db.hits]
    return SearchResults(results, results_db.estimated_total_hits)
