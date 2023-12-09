from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import NamedTuple

from rgdps.common import data_utils
from rgdps.common import time as time_utils
from rgdps.common.context import Context
from rgdps.common.typing import is_set
from rgdps.common.typing import UNSET
from rgdps.common.typing import Unset
from rgdps.constants.levels import LevelDemonDifficulty
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlag
from rgdps.constants.levels import LevelSearchType
from rgdps.models.level import Level


async def from_id(
    ctx: Context,
    level_id: int,
    include_deleted: bool = False,
) -> Level | None:
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"

    level_db = await ctx.mysql.fetch_one(
        "SELECT id, name, user_id, description, custom_song_id, official_song_id, "
        "version, length, two_player, publicity, render_str, game_version, "
        "binary_version, upload_ts, update_ts, original_id, downloads, likes, stars, difficulty, "
        "demon_difficulty, coins, coins_verified, requested_stars, feature_order, "
        "search_flags, low_detail_mode, object_count, copy_password, building_time, "
        "update_locked, deleted FROM levels WHERE id = :id" + condition,
        {
            "id": level_id,
        },
    )

    if level_db is None:
        return None

    return Level.from_mapping(level_db)


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
    copy_password: int = 0,
    building_time: int = 0,
    update_locked: bool = False,
    deleted: bool = False,
    level_id: int = 0,
) -> Level:
    if upload_ts is None:
        upload_ts = datetime.now()
    if update_ts is None:
        update_ts = datetime.now()

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
        copy_password=copy_password,
        building_time=building_time,
        update_locked=update_locked,
        deleted=deleted,
    )

    level.id = await create_sql(ctx, level)
    await create_meili(ctx, level)
    return level


async def create_sql(ctx: Context, level: Level) -> int:
    return await ctx.mysql.execute(
        "INSERT INTO levels (id, name, user_id, description, custom_song_id, "
        "official_song_id, version, length, two_player, publicity, render_str, "
        "game_version, binary_version, upload_ts, update_ts, original_id, downloads, likes, "
        "stars, difficulty, demon_difficulty, coins, coins_verified, requested_stars, "
        "feature_order, search_flags, low_detail_mode, object_count, copy_password, "
        "building_time, update_locked, deleted) VALUES (:id, :name, :user_id, "
        ":description, :custom_song_id, :official_song_id, :version, :length, "
        ":two_player, :publicity, :render_str, :game_version, :binary_version, "
        ":upload_ts, :update_ts, :original_id, :downloads, :likes, :stars, :difficulty, "
        ":demon_difficulty, :coins, :coins_verified, :requested_stars, :feature_order, "
        ":search_flags, :low_detail_mode, :object_count, :copy_password, "
        ":building_time, :update_locked, :deleted)",
        level.as_dict(include_id=True),
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

    return level_dict


async def create_meili(ctx: Context, level: Level) -> None:
    level_dict = _make_meili_dict(level.as_dict(include_id=True))

    index = ctx.meili.index("levels")
    await index.add_documents([level_dict])


async def update_sql_full(ctx: Context, level: Level) -> None:
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


async def update_sql_partial(
    ctx: Context,
    level_id: int,
    name: str | Unset = UNSET,
    user_id: int | Unset = UNSET,
    description: str | Unset = UNSET,
    custom_song_id: int | None | Unset = UNSET,
    official_song_id: int | None | Unset = UNSET,
    version: int | Unset = UNSET,
    length: LevelLength | Unset = UNSET,
    two_player: bool | Unset = UNSET,
    publicity: LevelPublicity | Unset = UNSET,
    render_str: str | Unset = UNSET,
    game_version: int | Unset = UNSET,
    binary_version: int | Unset = UNSET,
    upload_ts: datetime | Unset = UNSET,
    update_ts: datetime | Unset = UNSET,
    original_id: int | None | Unset = UNSET,
    downloads: int | Unset = UNSET,
    likes: int | Unset = UNSET,
    stars: int | Unset = UNSET,
    difficulty: LevelDifficulty | Unset = UNSET,
    demon_difficulty: LevelDemonDifficulty | None | Unset = UNSET,
    coins: int | Unset = UNSET,
    coins_verified: bool | Unset = UNSET,
    requested_stars: int | Unset = UNSET,
    feature_order: int | Unset = UNSET,
    search_flags: LevelSearchFlag | Unset = UNSET,
    low_detail_mode: bool | Unset = UNSET,
    object_count: int | Unset = UNSET,
    copy_password: int | Unset = UNSET,
    building_time: int | Unset = UNSET,
    update_locked: bool | Unset = UNSET,
    deleted: bool | Unset = UNSET,
) -> Level | None:
    changed_data = {}

    if is_set(name):
        changed_data["name"] = name
    if is_set(user_id):
        changed_data["user_id"]
    if is_set(description):
        changed_data["description"] = description
    if is_set(custom_song_id):
        changed_data["custom_song_id"] = custom_song_id
    if is_set(official_song_id):
        changed_data["official_song_id"] = official_song_id
    if is_set(version):
        changed_data["version"] = version
    if is_set(length):
        changed_data["length"] = length.value
    if is_set(two_player):
        changed_data["two_player"] = two_player
    if is_set(publicity):
        changed_data["publicity"] = publicity.value
    if is_set(render_str):
        changed_data["render_str"] = render_str
    if is_set(game_version):
        changed_data["game_version"] = game_version
    if is_set(binary_version):
        changed_data["binary_version"] = binary_version
    if is_set(upload_ts):
        changed_data["upload_ts"] = upload_ts
    if is_set(update_ts):
        changed_data["update_ts"] = update_ts
    if is_set(original_id):
        changed_data["original_id"] = original_id
    if is_set(downloads):
        changed_data["downloads"] = downloads
    if is_set(likes):
        changed_data["likes"] = likes
    if is_set(stars):
        changed_data["stars"] = stars
    if is_set(difficulty):
        changed_data["difficulty"] = difficulty.value
    if is_set(demon_difficulty):
        if demon_difficulty is None:
            changed_data["demon_difficulty"] = None
        else:
            changed_data["demon_difficulty"] = demon_difficulty.value
    if is_set(coins):
        changed_data["coins"] = coins
    if is_set(coins_verified):
        changed_data["coins_verified"] = coins_verified
    if is_set(requested_stars):
        changed_data["requested_stars"] = requested_stars
    if is_set(feature_order):
        changed_data["feature_order"] = feature_order
    if is_set(search_flags):
        changed_data["search_flags"] = search_flags.value
    if is_set(low_detail_mode):
        changed_data["low_detail_mode"] = low_detail_mode
    if is_set(object_count):
        changed_data["object_count"] = object_count
    if is_set(copy_password):
        changed_data["copy_password"] = copy_password
    if is_set(building_time):
        changed_data["building_time"] = building_time
    if is_set(update_locked):
        changed_data["update_locked"] = update_locked
    if is_set(deleted):
        changed_data["deleted"] = deleted

    if not changed_data:
        return await from_id(ctx, level_id)

    query = "UPDATE levels SET "
    query += ", ".join(f"{name} = :{name}" for name in changed_data.keys())
    query += " WHERE id = :id"

    changed_data["id"] = level_id
    await ctx.mysql.execute(query, changed_data)

    return await from_id(ctx, level_id, include_deleted=True)


async def update_meili_partial(
    ctx: Context,
    level_id: int,
    name: str | Unset = UNSET,
    user_id: int | Unset = UNSET,
    description: str | Unset = UNSET,
    custom_song_id: int | None | Unset = UNSET,
    official_song_id: int | None | Unset = UNSET,
    version: int | Unset = UNSET,
    length: LevelLength | Unset = UNSET,
    two_player: bool | Unset = UNSET,
    publicity: LevelPublicity | Unset = UNSET,
    render_str: str | Unset = UNSET,
    game_version: int | Unset = UNSET,
    binary_version: int | Unset = UNSET,
    upload_ts: datetime | Unset = UNSET,
    update_ts: datetime | Unset = UNSET,
    original_id: int | None | Unset = UNSET,
    downloads: int | Unset = UNSET,
    likes: int | Unset = UNSET,
    stars: int | Unset = UNSET,
    difficulty: LevelDifficulty | Unset = UNSET,
    demon_difficulty: LevelDemonDifficulty | None | Unset = UNSET,
    coins: int | Unset = UNSET,
    coins_verified: bool | Unset = UNSET,
    requested_stars: int | Unset = UNSET,
    feature_order: int | Unset = UNSET,
    search_flags: LevelSearchFlag | Unset = UNSET,
    low_detail_mode: bool | Unset = UNSET,
    object_count: int | Unset = UNSET,
    copy_password: int | Unset = UNSET,
    building_time: int | Unset = UNSET,
    update_locked: bool | Unset = UNSET,
    deleted: bool | Unset = UNSET,
) -> None:
    changed_data: dict[str, Any] = {
        "id": level_id,
    }

    if is_set(name):
        changed_data["name"] = name
    if is_set(user_id):
        changed_data["user_id"]
    if is_set(description):
        changed_data["description"] = description
    if is_set(custom_song_id):
        changed_data["custom_song_id"] = custom_song_id
    if is_set(official_song_id):
        changed_data["official_song_id"] = official_song_id
    if is_set(version):
        changed_data["version"] = version
    if is_set(length):
        changed_data["length"] = length.value
    if is_set(two_player):
        changed_data["two_player"] = two_player
    if is_set(publicity):
        changed_data["publicity"] = publicity.value
    if is_set(render_str):
        changed_data["render_str"] = render_str
    if is_set(game_version):
        changed_data["game_version"] = game_version
    if is_set(binary_version):
        changed_data["binary_version"] = binary_version
    if is_set(upload_ts):
        changed_data["upload_ts"] = upload_ts
    if is_set(update_ts):
        changed_data["update_ts"] = update_ts
    if is_set(original_id):
        changed_data["original_id"] = original_id
    if is_set(downloads):
        changed_data["downloads"] = downloads
    if is_set(likes):
        changed_data["likes"] = likes
    if is_set(stars):
        changed_data["stars"] = stars
    if is_set(difficulty):
        changed_data["difficulty"] = difficulty.value
    if is_set(demon_difficulty):
        if demon_difficulty is None:
            changed_data["demon_difficulty"] = None
        else:
            changed_data["demon_difficulty"] = demon_difficulty.value
    if is_set(coins):
        changed_data["coins"] = coins
    if is_set(coins_verified):
        changed_data["coins_verified"] = coins_verified
    if is_set(requested_stars):
        changed_data["requested_stars"] = requested_stars
    if is_set(feature_order):
        changed_data["feature_order"] = feature_order
    if is_set(search_flags):
        changed_data["search_flags"] = search_flags.value
    if is_set(low_detail_mode):
        changed_data["low_detail_mode"] = low_detail_mode
    if is_set(object_count):
        changed_data["object_count"] = object_count
    if is_set(copy_password):
        changed_data["copy_password"] = copy_password
    if is_set(building_time):
        changed_data["building_time"] = building_time
    if is_set(update_locked):
        changed_data["update_locked"] = update_locked
    if is_set(deleted):
        changed_data["deleted"] = deleted

    changed_data = _make_meili_dict(changed_data)

    index = ctx.meili.index("levels")
    await index.update_documents([changed_data])


async def update_partial(
    ctx: Context,
    level_id: int,
    name: str | Unset = UNSET,
    user_id: int | Unset = UNSET,
    description: str | Unset = UNSET,
    custom_song_id: int | None | Unset = UNSET,
    official_song_id: int | None | Unset = UNSET,
    version: int | Unset = UNSET,
    length: LevelLength | Unset = UNSET,
    two_player: bool | Unset = UNSET,
    publicity: LevelPublicity | Unset = UNSET,
    render_str: str | Unset = UNSET,
    game_version: int | Unset = UNSET,
    binary_version: int | Unset = UNSET,
    upload_ts: datetime | Unset = UNSET,
    update_ts: datetime | Unset = UNSET,
    original_id: int | None | Unset = UNSET,
    downloads: int | Unset = UNSET,
    likes: int | Unset = UNSET,
    stars: int | Unset = UNSET,
    difficulty: LevelDifficulty | Unset = UNSET,
    demon_difficulty: LevelDemonDifficulty | None | Unset = UNSET,
    coins: int | Unset = UNSET,
    coins_verified: bool | Unset = UNSET,
    requested_stars: int | Unset = UNSET,
    feature_order: int | Unset = UNSET,
    search_flags: LevelSearchFlag | Unset = UNSET,
    low_detail_mode: bool | Unset = UNSET,
    object_count: int | Unset = UNSET,
    copy_password: int | Unset = UNSET,
    building_time: int | Unset = UNSET,
    update_locked: bool | Unset = UNSET,
    deleted: bool | Unset = UNSET,
) -> Level | None:
    level = await update_sql_partial(
        ctx,
        level_id=level_id,
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
        copy_password=copy_password,
        building_time=building_time,
        update_locked=update_locked,
        deleted=deleted,
    )

    if level is None:
        return None

    await update_meili_partial(
        ctx,
        level_id=level_id,
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
        copy_password=copy_password,
        building_time=building_time,
        update_locked=update_locked,
        deleted=deleted,
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


async def all_ids(ctx: Context, include_deleted: bool = False) -> list[int]:
    condition = ""
    if not include_deleted:
        condition = " WHERE NOT deleted"

    return [
        x["id"] for x in await ctx.mysql.fetch_all("SELECT id FROM levels" + condition)
    ]


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
    condition = ""
    if not include_deleted:
        condition = " AND NOT deleted"

    result_id = await ctx.mysql.fetch_val(
        "SELECT id FROM levels WHERE name LIKE :name AND user_id = :user_id",
        {"name": level_name, "user_id": user_id},
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
