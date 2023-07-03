from __future__ import annotations

import time
from datetime import datetime
from typing import Any
from typing import NamedTuple
from typing import Optional

from rgdps.common import data_utils
from rgdps.common.context import Context
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlag
from rgdps.constants.levels import LevelSearchType
from rgdps.models.level import Level


async def from_id(
    ctx: Context,
    level_id: int,
    include_deleted: bool = False,
) -> Optional[Level]:
    level_db = await ctx.mysql.fetch_one(
        "SELECT id, name, user_id, description, custom_song_id, official_song_id, "
        "version, length, two_player, publicity, render_str, game_version, "
        "binary_version, upload_ts, update_ts, original_id, downloads, likes, stars, difficulty, "
        "demon_difficulty, coins, coins_verified, requested_stars, feature_order, "
        "search_flags, low_detail_mode, object_count, copy_password, building_time, "
        "update_locked, deleted FROM levels WHERE id = :id AND deleted = :deleted",
        {
            "id": level_id,
            "deleted": include_deleted,
        },
    )

    if level_db is None:
        return None

    return Level.from_mapping(level_db)


async def create(ctx: Context, level: Level) -> int:
    level_id = await create_sql(ctx, level)
    await create_meili(ctx, level, level_id)
    return level_id


async def create_sql(ctx: Context, level: Level) -> int:
    return await ctx.mysql.execute(
        "INSERT INTO levels (name, user_id, description, custom_song_id, "
        "official_song_id, version, length, two_player, publicity, render_str, "
        "game_version, binary_version, upload_ts, update_ts, original_id, downloads, likes, "
        "stars, difficulty, demon_difficulty, coins, coins_verified, requested_stars, "
        "feature_order, search_flags, low_detail_mode, object_count, copy_password, "
        "building_time, update_locked, deleted) VALUES (:name, :user_id, "
        ":description, :custom_song_id, :official_song_id, :version, :length, "
        ":two_player, :publicity, :render_str, :game_version, :binary_version, "
        ":upload_ts, :update_ts, :original_id, :downloads, :likes, :stars, :difficulty, "
        ":demon_difficulty, :coins, :coins_verified, :requested_stars, :feature_order, "
        ":search_flags, :low_detail_mode, :object_count, :copy_password, "
        ":building_time, :update_locked, :deleted)",
        level.as_dict(include_id=False),
    )


# Functions to assist with meili not liking datetime objects.
def _dt_as_unix_ts(dt: datetime) -> int:
    return int(time.mktime(dt.timetuple()))


def _unix_ts_as_dt(unix_ts: int) -> datetime:
    return datetime.fromtimestamp(unix_ts)


def _make_meili_dict(level: Level) -> dict[str, Any]:
    level_dict = level.as_dict(include_id=True)
    level_dict["upload_ts"] = _dt_as_unix_ts(level_dict["upload_ts"])
    level_dict["update_ts"] = _dt_as_unix_ts(level_dict["update_ts"])

    # Split up bitwise enums as meili does not support bitwise operations.
    level_dict["epic"] = bool(level_dict["search_flags"] & LevelSearchFlag.EPIC)
    level_dict["magic"] = bool(level_dict["search_flags"] & LevelSearchFlag.MAGIC)
    level_dict["awarded"] = bool(level_dict["search_flags"] & LevelSearchFlag.AWARDED)

    return level_dict


def _from_meili_dict(level_dict: dict[str, Any]) -> Level:
    # Meili returns unix timestamps, so we need to convert them back to datetime.
    level_dict["upload_ts"] = _unix_ts_as_dt(level_dict["upload_ts"])
    level_dict["update_ts"] = _unix_ts_as_dt(level_dict["update_ts"])

    search_flags = LevelSearchFlag.NONE

    if level_dict["epic"]:
        search_flags |= LevelSearchFlag.EPIC

    if level_dict["magic"]:
        search_flags |= LevelSearchFlag.MAGIC

    if level_dict["awarded"]:
        search_flags |= LevelSearchFlag.AWARDED

    level_dict["search_flags"] = search_flags

    del level_dict["epic"]
    del level_dict["magic"]
    del level_dict["awarded"]

    return Level.from_mapping(level_dict)


async def create_meili(ctx: Context, level: Level, level_id: int) -> None:
    # This is a bit hacky as we do not have the level ID in the level object yet.
    level_dict = _make_meili_dict(level)
    level_dict["id"] = level_id

    index = ctx.meili.index("levels")
    await index.add_documents([level_dict])


async def update(ctx: Context, level: Level) -> None:
    # In case sql fails, we do not want to update meili.
    await update_sql(ctx, level)
    await update_meili(ctx, level)


async def update_meili(ctx: Context, level: Level) -> None:
    index = ctx.meili.index("levels")
    # Fun fact, this is EXACTLY the same as `add_documents`.
    await index.update_documents([_make_meili_dict(level)])


async def update_sql(ctx: Context, level: Level) -> None:
    await ctx.mysql.execute(
        "UPDATE levels SET name = :name, user_id = :user_id, description = :description, "
        "custom_song_id = :custom_song_id, official_song_id = :official_song_id, "
        "version = :version, length = :length, two_player = :two_player, "
        "publicity = :publicity, render_str = :render_str, game_version = :game_version, "
        "binary_version = :binary_version, upload_ts = :upload_ts, update_ts = :update_ts, "
        "original_id = :original_id, downloads = :downloads, likes = :likes, stars = :stars, difficulty = :difficulty, "
        "demon_difficulty = :demon_difficulty, coins = :coins, coins_verified = :coins_verified, "
        "requested_stars = :requested_stars, feature_order = :feature_order, "
        "search_flags = :search_flags, low_detail_mode = :low_detail_mode, "
        "object_count = :object_count, copy_password = :copy_password, "
        "building_time = :building_time, update_locked = :update_locked, "
        "deleted = :deleted WHERE id = :id",
        level.as_dict(include_id=True),
    )


async def delete_meili(ctx: Context, level_id: int) -> None:
    index = ctx.meili.index("levels")
    await index.delete_documents([str(level_id)])


class SearchResults(NamedTuple):
    results: list[Level]
    total: int


async def search(
    ctx: Context,
    page: int,
    page_size: int,
    query: Optional[str] = None,
    search_type: Optional[LevelSearchType] = None,
    level_lengths: Optional[list[LevelLength]] = None,
    completed_levels: Optional[list[int]] = None,
    featured: bool = False,
    original: bool = False,
    two_player: bool = False,
    unrated: bool = False,
    rated: bool = False,
    song_id: Optional[int] = None,
    custom_song_id: Optional[int] = None,
    followed_list: Optional[list[int]] = None,
) -> SearchResults:
    # Create the filters.
    filters = []
    sort = []

    # TODO: Match statement if we ever get to python 3.11?
    if search_type is LevelSearchType.MOST_DOWNLOADED:
        sort.append("downloads:desc")

    elif search_type is LevelSearchType.MOST_LIKED:
        sort.append("likes:desc")

    # TODO: Trending
    elif search_type is LevelSearchType.RECENT:
        sort.append("upload_ts:desc")

    elif search_type is LevelSearchType.USER_LEVELS:
        filters.append(f"user_id = {query}")

    elif search_type is LevelSearchType.FEATURED:
        filters.append("feature_order > 0")
        sort.append("feature_order:desc")

    elif search_type is LevelSearchType.MAGIC:
        filters.append(f"magic = true")

    elif search_type is LevelSearchType.AWARDED:
        filters.append("awarded = true")

    elif search_type is LevelSearchType.FOLLOWED:
        assert followed_list is not None
        filters.append(f"user_id IN {followed_list}")

    elif search_type is LevelSearchType.FRIENDS:
        raise NotImplementedError("Friends not implemented yet.")

    elif search_type is LevelSearchType.EPIC:
        filters.append("epic = true")
        sort.append("feature_order:desc")

    elif search_type is LevelSearchType.DAILY:
        raise NotImplementedError("Daily not implemented yet.")

    elif search_type is LevelSearchType.WEEKLY:
        raise NotImplementedError("Weekly not implemented yet.")

    # Optional filters.
    if level_lengths is not None:
        # FIXME: Type ignore
        length_ints = data_utils.enum_int_list(level_lengths)  # type: ignore
        filters.append(f"length IN {length_ints}")

    if featured:
        filters.append("feature_order > 0")

    if original:
        filters.append("original_id IS NULL")

    if two_player:
        filters.append("two_player = true")

    if unrated:
        filters.append("stars = 0")

    if rated:
        filters.append("stars > 0")

    if song_id is not None:
        filters.append(f"official_song_id = {song_id}")

    if custom_song_id is not None:
        filters.append(f"custom_song_id = {custom_song_id}")

    if completed_levels is not None:
        filters.append(f"id NOT IN {completed_levels}")

    # TODO: More unlisted logic, such as friends
    filters.append(f"publicity = {LevelPublicity.PUBLIC.value}")

    offset = page * page_size
    index = ctx.meili.index("levels")
    results_db = await index.search(
        query,
        offset=offset,
        limit=page_size,
        filter=filters,
        sort=sort,
    )

    if (not results_db.hits) or (not results_db.estimated_total_hits):
        return SearchResults([], 0)

    results = [_from_meili_dict(result) for result in results_db.hits]
    return SearchResults(results, results_db.estimated_total_hits)


async def all_ids(ctx: Context, include_deleted: bool = False) -> list[int]:
    return [
        x["id"]
        for x in await ctx.mysql.fetch_all(
            "SELECT id FROM levels WHERE deleted = :deleted",
            {"deleted": include_deleted},
        )
    ]
