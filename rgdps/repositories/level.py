from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import AsyncGenerator
from typing import NamedTuple
from typing import TypedDict
from typing import Unpack

from rgdps.common import data_utils
from rgdps.common import time as time_utils
from rgdps.common.context import Context
from rgdps.common import modelling
from rgdps.constants.levels import LevelDemonDifficulty
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlag
from rgdps.constants.levels import LevelSearchType
from rgdps.models.level import Level

import orjson


ALL_FIELDS = modelling.get_model_fields(Level)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)

async def from_id(
    ctx: Context,
    level_id: int,
    include_deleted: bool = False,
) -> Level | None:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"

    level_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM levels WHERE id = :id"
        + condition,
        {
            "id": level_id,
        },
    )

    if level_db is None:
        return None

    return Level.from_mapping(_from_mysql_dict(dict(level_db)))  # type: ignore


async def create(
    ctx: Context,
    name: str,
    user_id: int,
    description: str = "",
    custom_song_id: int | None = None,
    official_song_id: int | None = 1,
    version: int = 1,
    length: LevelLength = LevelLength.TINY,
    two_player: bool = False,
    publicity: LevelPublicity = LevelPublicity.PUBLIC,
    render_str: str = "",
    game_version: int = 22,
    binary_version: int = 34,
    upload_ts: datetime | None = None,
    update_ts: datetime | None = None,
    original_id: int | None = None,
    downloads: int = 0,
    likes: int = 0,
    stars: int = 0,
    difficulty: LevelDifficulty = LevelDifficulty.NA,
    demon_difficulty: LevelDemonDifficulty | None = None,
    coins: int = 0,
    coins_verified: bool = False,
    requested_stars: int = 0,
    feature_order: int = 0,
    search_flags: LevelSearchFlag = LevelSearchFlag.NONE,
    low_detail_mode: bool = False,
    object_count: int = 0,
    building_time: int = 0,
    update_locked: bool = False,
    song_ids: list[int] | None = None,
    sfx_ids: list[int] | None = None,
    deleted: bool = False,
    level_id: int = 0,
) -> Level:
    if upload_ts is None:
        upload_ts = datetime.now()
    if update_ts is None:
        update_ts = datetime.now()

    if sfx_ids is None:
        sfx_ids = []
    if song_ids is None:
        song_ids = []

    level = Level(
        id=level_id,
        name=name,
        user_id=user_id,
        description=description,
        custom_song_id=custom_song_id,
        official_song_id=official_song_id,
        version=version,
        length=length,
        two_player=two_player,
        publicity=publicity,
        render_str=render_str,
        game_version=game_version,
        binary_version=binary_version,
        upload_ts=upload_ts,
        update_ts=update_ts,
        original_id=original_id,
        downloads=downloads,
        likes=likes,
        stars=stars,
        difficulty=difficulty,
        demon_difficulty=demon_difficulty,
        coins=coins,
        coins_verified=coins_verified,
        requested_stars=requested_stars,
        feature_order=feature_order,
        search_flags=search_flags,
        low_detail_mode=low_detail_mode,
        object_count=object_count,
        building_time=building_time,
        update_locked=update_locked,
        deleted=deleted,
        song_ids=song_ids,
        sfx_ids=sfx_ids,
    )

    level.id = await create_sql(ctx, level)
    await create_meili(ctx, level)
    return level


async def create_sql(ctx: Context, level: Level) -> int:
    return await ctx.mysql.execute(
        f"INSERT INTO levels ({_ALL_FIELDS_COMMA}) VALUES ({_ALL_FIELDS_COLON})",
        _make_mysql_dict(level.as_dict(include_id=True)),
    )


def _make_meili_dict(level_dict: dict[str, Any]) -> dict[str, Any]:
    level_dict = level_dict.copy()
    if "upload_ts" in level_dict:
        level_dict["upload_ts"] = time_utils.into_unix_ts(level_dict["upload_ts"])

    if "update_ts" in level_dict:
        level_dict["update_ts"] = time_utils.into_unix_ts(level_dict["update_ts"])

    # Split up bitwise enums as meili does not support bitwise operations.
    if "search_flags" in level_dict:
        level_dict["epic"] = bool(level_dict["search_flags"] & LevelSearchFlag.EPIC)
        level_dict["magic"] = bool(level_dict["search_flags"] & LevelSearchFlag.MAGIC)
        level_dict["awarded"] = bool(
            level_dict["search_flags"] & LevelSearchFlag.AWARDED,
        )

    return level_dict


def _from_meili_dict(level_dict: dict[str, Any]) -> dict[str, Any]:
    level_dict = level_dict.copy()
    # Meili returns unix timestamps, so we need to convert them back to datetime.
    level_dict["upload_ts"] = time_utils.from_unix_ts(level_dict["upload_ts"])
    level_dict["update_ts"] = time_utils.from_unix_ts(level_dict["update_ts"])

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

    # FIXME: Temporary migration measure.
    if "song_ids" not in level_dict:
        level_dict["song_ids"] = [level_dict["custom_song_id"]]
        level_dict["sfx_ids"] = []

    return level_dict


# These are required due to Databases not working well with `JSON` field types.
def _make_mysql_dict(level_dict: dict[str, Any]) -> dict[str, Any]:
    level_dict = level_dict.copy()

    level_dict["song_ids"] = orjson.dumps(level_dict["song_ids"]).decode()
    level_dict["sfx_ids"] = orjson.dumps(level_dict["sfx_ids"]).decode()

    return level_dict


def _from_mysql_dict(level_dict: dict[str, Any]) -> dict[str, Any]:
    level_dict = level_dict.copy()

    level_dict["song_ids"] = orjson.loads(level_dict["song_ids"])
    level_dict["sfx_ids"] = orjson.loads(level_dict["sfx_ids"])

    return level_dict


async def create_meili(ctx: Context, level: Level) -> None:
    level_dict = _make_meili_dict(level.as_dict(include_id=True))

    index = ctx.meili.index("levels")
    await index.add_documents([level_dict])


async def multiple_create_meili(ctx: Context, levels: list[Level]) -> None:
    level_dicts = [_make_meili_dict(level.as_dict(include_id=True)) for level in levels]

    index = ctx.meili.index("levels")
    await index.add_documents(level_dicts)


class _LevelPartialUpdate(TypedDict):
    name: str
    user_id: int
    description: str
    custom_song_id: int | None
    official_song_id: int | None
    version: int
    length: LevelLength
    two_player: bool
    publicity: LevelPublicity
    render_str: str
    game_version: int
    binary_version: int
    upload_ts: datetime
    update_ts: datetime
    original_id: int | None
    downloads: int
    likes: int
    stars: int
    difficulty: LevelDifficulty
    demon_difficulty: LevelDemonDifficulty | None
    coins: int
    coins_verified: bool
    requested_stars: int
    feature_order: int
    search_flags: LevelSearchFlag
    low_detail_mode: bool
    object_count: int
    building_time: int
    update_locked: bool
    song_ids: list[int]
    sfx_ids: list[int]
    deleted: bool


async def update_sql_partial(
    ctx: Context,
    level_id: int,
    **kwargs: Unpack[_LevelPartialUpdate],
) -> Level | None:
    changed_fields = modelling.unpack_enum_types(kwargs)

    
    await ctx.mysql.execute(
        modelling.update_from_partial_dict("levels", level_id, changed_fields),
        changed_fields,
    )

    return await from_id(ctx, level_id, include_deleted=True)


async def update_meili_partial(
    ctx: Context,
    level_id: int,
    **kwargs: Unpack[_LevelPartialUpdate],
) -> None:
    changed_fields = modelling.unpack_enum_types(kwargs)
    # Meili primary key
    changed_fields["id"] = level_id
    changed_fields = _make_meili_dict(changed_fields)

    index = ctx.meili.index("levels")
    await index.update_documents([changed_fields])


async def update_partial(
    ctx: Context,
    level_id: int,
    **kwargs: Unpack[_LevelPartialUpdate],
) -> Level | None:
    level = await update_sql_partial(
        ctx,
        level_id=level_id,
        **kwargs,
    )

    if level is None:
        return None

    await update_meili_partial(
        ctx,
        level_id=level_id,
        **kwargs,
    )

    return level


async def delete_meili(ctx: Context, level_id: int) -> None:
    index = ctx.meili.index("levels")
    await index.delete_documents([str(level_id)])


class LevelSearchResults(NamedTuple):
    results: list[Level]
    total: int


async def search(
    ctx: Context,
    page: int,
    page_size: int,
    query: str | None = None,
    search_type: LevelSearchType | None = None,
    level_lengths: list[LevelLength] | None = None,
    completed_levels: list[int] | None = None,
    featured: bool = False,
    original: bool = False,
    two_player: bool = False,
    unrated: bool = False,
    rated: bool = False,
    song_id: int | None = None,
    custom_song_id: int | None = None,
    followed_list: list[int] | None = None,
) -> LevelSearchResults:
    # Create the filters.
    filters = []
    sort = []

    match search_type:
        case LevelSearchType.MOST_DOWNLOADED:
            sort.append("downloads:desc")

        case LevelSearchType.MOST_LIKED:
            sort.append("likes:desc")

        # TODO: Trending
        case LevelSearchType.RECENT:
            sort.append("upload_ts:desc")

        case LevelSearchType.USER_LEVELS:
            filters.append(f"user_id = {query}")
            sort.append("upload_ts:desc")

        case LevelSearchType.FEATURED:
            filters.append("feature_order > 0")
            sort.append("feature_order:desc")

        case LevelSearchType.MAGIC:
            filters.append("magic = true")

        case LevelSearchType.AWARDED:
            filters.append("awarded = true")

        case LevelSearchType.FOLLOWED if followed_list is not None:
            filters.append(f"user_id IN {followed_list}")

        case LevelSearchType.FRIENDS:
            raise NotImplementedError("Friends not implemented yet.")

        case LevelSearchType.EPIC:
            filters.append("epic = true")
            sort.append("feature_order:desc")

        case LevelSearchType.DAILY:
            raise NotImplementedError("Daily not implemented yet.")

        case LevelSearchType.WEEKLY:
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
        return LevelSearchResults([], 0)

    results = [
        Level.from_mapping(_from_meili_dict(result)) for result in results_db.hits
    ]
    return LevelSearchResults(results, results_db.estimated_total_hits)


async def all(
    ctx: Context,
    include_deleted: bool = False,
) -> AsyncGenerator[Level, None]:
    async for level_db in ctx.mysql.iterate(
        f"SELECT {_ALL_FIELDS_COMMA} FROM levels WHERE deleted IN :deleted",
        {
            "deleted": (0, 1) if include_deleted else (0,),
        },
    ):
        yield Level.from_mapping(_from_mysql_dict(dict(level_db)))


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM levels")


async def nuke_meili(ctx: Context) -> None:
    await ctx.meili.index("levels").delete_all_documents()


async def from_name_and_user_id(
    ctx: Context,
    level_name: str,
    user_id: int,
    include_deleted: bool = False,
) -> Level | None:
    result_id = await ctx.mysql.fetch_val(
        "SELECT id FROM levels WHERE name LIKE :name AND user_id = :user_id AND deleted = :deleted",
        {
            "name": level_name,
            "user_id": user_id,
            "deleted": (0, 1) if include_deleted else (0,),
        },
    )

    if result_id is None:
        return None

    return await from_id(ctx, result_id, include_deleted)


async def from_name(
    ctx: Context,
    level_name: str,
    include_deleted: bool = False,
) -> Level | None:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"

    result_id = await ctx.mysql.fetch_val(
        "SELECT id FROM levels WHERE name LIKE :name" + condition,
        {
            "name": level_name,
        },
    )

    if result_id is None:
        return None

    return await from_id(ctx, result_id, include_deleted)


# A function primarily used for some recommendation algorithms that returns a list of levels
# ordered by how well received they are, assessed using a formula..
async def get_well_received(
    ctx: Context,
    minimum_stars: int,
    minimum_length: LevelLength,
    maximum_stars: int = 0,
    maximum_demon_rating: LevelDemonDifficulty = LevelDemonDifficulty.EXTREME,
    excluded_level_ids: list[
        int
    ] = [],  # The list isnt mutable, so we can set it to an empty list.
    limit: int = 100,
) -> list[int]:
    # BOTCH! Avoiding a sql syntax error.
    if not excluded_level_ids:
        excluded_level_ids = [0]

    # The formula in the order clause is made to emphasis lower downloads, but still have a
    # significant impact on likes.
    values = await ctx.mysql.fetch_all(
        "SELECT id FROM levels WHERE stars >= :minimum_stars AND stars <= :maximum_stars "
        "AND demon_difficulty <= :maximum_demon_rating AND length >= :minimum_length "
        "AND id NOT IN :excluded_level_ids AND deleted = 0 ORDER BY (SQRT(downloads) / likes) DESC "
        "LIMIT :limit",
        {
            "minimum_stars": minimum_stars,
            "maximum_stars": maximum_stars,
            "maximum_demon_rating": maximum_demon_rating.value,
            "minimum_length": minimum_length.value,
            "excluded_level_ids": tuple(excluded_level_ids),
            "limit": limit,
        },
    )

    return [x["id"] for x in values]
