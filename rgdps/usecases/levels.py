from __future__ import annotations

import time
from datetime import datetime
from typing import NamedTuple

from rgdps import repositories
from rgdps.common import gd_logic
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlag
from rgdps.constants.levels import LevelSearchType
from rgdps.constants.users import CREATOR_PRIVILEGES
from rgdps.models.level import Level
from rgdps.models.song import Song
from rgdps.models.user import User


async def create_or_update(
    ctx: Context,
    user_id: int,
    level_id: int,
    name: str,
    custom_song_id: int,
    copy_password: int,
    two_player: bool,
    object_count: int,
    coins: int,
    unlisted: bool,
    render_str: str,
    requested_stars: int,
    level_data: str,
    length: LevelLength,
    version: int,
    description: str,
    original: int | None,
    official_song_id: int,
    game_version: int,
    binary_version: int,
    low_detail_mode: bool,
    building_time: int,
) -> Level | ServiceError:
    if custom_song_id:
        track_id = None
        song_id = custom_song_id

        if not await repositories.song.from_id(ctx, song_id):
            return ServiceError.LEVELS_INVALID_CUSTOM_SONG
    else:
        song_id = None
        track_id = official_song_id

    # TODO: Add more logic here.
    if unlisted:
        publicity = LevelPublicity.FRIENDS_UNLISTED
    else:
        publicity = LevelPublicity.PUBLIC

    # Check if we are updating or creating.
    old_level = await repositories.level.from_id(
        ctx,
        level_id,
        include_deleted=False,
    )

    if old_level is None:
        # Name overwrite test.
        old_level = await repositories.level.from_name_and_user_id(
            ctx,
            name,
            user_id,
            include_deleted=False,
        )

    if old_level:
        # Update
        if old_level.user_id != user_id:
            return ServiceError.LEVELS_NO_UPDATE_PERMISSION
        if old_level.update_locked:
            return ServiceError.LEVELS_UPDATE_LOCKED

        # Apply new values to the old level.
        level = await repositories.level.update_partial(
            ctx,
            level_id=level_id,
            name=name,
            custom_song_id=song_id,
            official_song_id=track_id,
            two_player=two_player,
            coins=coins,
            publicity=publicity,
            render_str=render_str,
            requested_stars=requested_stars,
            length=length,
            version=version,
            description=description,
            original_id=original,
            game_version=game_version,
            binary_version=binary_version,
            low_detail_mode=low_detail_mode,
            building_time=building_time,
            update_ts=datetime.now(),
        )

        # Should never happen.
        if level is None:
            return ServiceError.LEVELS_NOT_FOUND

        await repositories.level_data.create(ctx, level.id, level_data)
    else:
        level = await repositories.level.create(
            ctx,
            name=name,
            user_id=user_id,
            description=description,
            custom_song_id=song_id,
            official_song_id=track_id,
            version=version,
            length=length,
            two_player=two_player,
            publicity=publicity,
            render_str=render_str,
            game_version=game_version,
            binary_version=binary_version,
            original_id=original,
            requested_stars=requested_stars,
            low_detail_mode=low_detail_mode,
            object_count=object_count,
            coins=coins,
            copy_password=copy_password,
            building_time=building_time,
        )

        await repositories.level_data.create(ctx, level.id, level_data)

    return level


class SearchResponse(NamedTuple):
    levels: list[Level]
    total: int

    songs: list[Song]
    users: list[User]


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
) -> SearchResponse | ServiceError:
    # Allow for a level to be looked up by ID while
    # allowing level names consisting of numbers.
    lookup_level = None
    if (
        search_type is LevelSearchType.SEARCH_QUERY
        and query
        and query.isnumeric()
        and page == 0
    ):
        lookup_level = await repositories.level.from_id(ctx, int(query))
        if lookup_level:
            page_size -= 1

    levels_db = await repositories.level.search(
        ctx,
        page=page,
        page_size=page_size,
        query=query,
        search_type=search_type,
        level_lengths=level_lengths,
        completed_levels=completed_levels,
        featured=featured,
        original=original,
        two_player=two_player,
        unrated=unrated,
        rated=rated,
        song_id=song_id,
        custom_song_id=custom_song_id,
        followed_list=followed_list,
    )

    songs = set(
        await repositories.song.multiple_from_id(
            ctx,
            [level.custom_song_id for level in levels_db.results if level.custom_song_id is not None]
        )
    )
    users = set(await repositories.user.multiple_from_id(ctx, [level.user_id for level in levels_db.results]))

    if lookup_level:
        # Move to the top.
        if lookup_level in levels_db.results:
            levels_db.results.remove(lookup_level)
        levels_db.results.insert(0, lookup_level)

        lookup_user = await repositories.user.from_id(ctx, lookup_level.user_id)
        assert lookup_user is not None, "Lookup level user not found."
        users.add(lookup_user)

    return SearchResponse(
        levels=levels_db.results,
        total=levels_db.total + (1 if lookup_level else 0),
        songs=list(songs),
        users=list(users),
    )


# Fun fact, gd relies on the search endpoint for song and user data.
class LevelResponse(NamedTuple):
    level: Level
    data: str


async def get(ctx: Context, level_id: int) -> LevelResponse | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    level_data = await repositories.level_data.from_level_id(ctx, level_id)
    if not (level and level_data):
        return ServiceError.LEVELS_NOT_FOUND

    # Handle stats updates
    await repositories.level.update_partial(
        ctx,
        level.id,
        downloads=level.downloads + 1,
    )

    return LevelResponse(
        level=level,
        data=level_data,
    )


async def delete(
    ctx: Context,
    level_id: int,
    user_id: int,
    can_delete_other: bool = False,
) -> bool | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    if level.user_id != user_id and not can_delete_other:
        return ServiceError.LEVELS_NO_DELETE_PERMISSION

    await repositories.level.update_partial(
        ctx,
        level.id,
        deleted=True,
    )

    # TODO: Creator point recalculation.
    await repositories.level.delete_meili(ctx, level_id)
    return True


async def synchronise_search(ctx: Context) -> bool | ServiceError:
    """Synchronise the search index with the backing database.
    Should be rarely used as its demanding on resources.
    """
    levels = [level async for level in repositories.level.all(ctx)]
    await repositories.level.multiple_create_meili(ctx, levels)

    return True


async def suggest_stars(
    ctx: Context,
    level_id: int,
    stars: int,
    feature: bool,
) -> Level | ServiceError:
    existing_level = await repositories.level.from_id(ctx, level_id=level_id)

    if existing_level is None:
        return ServiceError.LEVELS_NOT_FOUND

    user = await repositories.user.from_id(ctx, user_id=existing_level.user_id)
    if user is None:
        return ServiceError.USER_NOT_FOUND

    creator_points = user.creator_points
    current_creator_points = gd_logic.calculate_creator_points(existing_level)

    feature_order = int(time.time()) if feature else 0

    difficulty = LevelDifficulty.from_stars(stars)

    level = await repositories.level.update_partial(
        ctx,
        level_id=level_id,
        stars=stars,
        feature_order=feature_order,
        difficulty=difficulty,
        coins_verified=True,
    )
    if level is None:
        return ServiceError.LEVELS_NOT_FOUND

    new_creator_points = gd_logic.calculate_creator_points(level)
    creator_points += new_creator_points - current_creator_points

    await repositories.user.update_partial(ctx, user.id, creator_points=creator_points)

    if user.privileges & CREATOR_PRIVILEGES == CREATOR_PRIVILEGES:
        await repositories.leaderboard.set_creator_count(ctx, user.id, creator_points)

    return level


async def set_description(
    ctx: Context,
    level_id: int,
    user_id: int,
    description: str,
    can_update_other: bool = False,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)

    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    if level.user_id != user_id and not can_update_other:
        return ServiceError.LEVELS_NO_UPDATE_PERMISSION

    result = await repositories.level.update_partial(
        ctx,
        level.id,
        description=description,
    )

    if result is None:
        return ServiceError.LEVELS_NOT_FOUND

    return result


async def nominate_awarded(
    ctx: Context,
    level_id: int,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    search_flags = level.search_flags | LevelSearchFlag.AWARDED

    result = await repositories.level.update_partial(
        ctx,
        level_id=level_id,
        search_flags=search_flags,
    )

    if result is None:
        return ServiceError.LEVELS_NOT_FOUND

    return result


async def revoke_awarded(
    ctx: Context,
    level_id: int,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    search_flags = level.search_flags & ~LevelSearchFlag.AWARDED

    result = await repositories.level.update_partial(
        ctx,
        level_id=level_id,
        search_flags=search_flags,
    )

    if result is None:
        return ServiceError.LEVELS_NOT_FOUND

    return result


async def set_unlisted(
    ctx: Context,
    level_id: int,
    user_id: int,
    friends_only: bool = False,
    can_unlist_other: bool = False,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    if level.user_id != user_id and not can_unlist_other:
        return ServiceError.LEVELS_NO_UPDATE_PERMISSION

    if friends_only:
        publicity = LevelPublicity.FRIENDS_UNLISTED
    else:
        publicity = LevelPublicity.GLOBAL_UNLISTED

    result = await repositories.level.update_partial(
        ctx,
        level_id=level_id,
        publicity=publicity,
    )

    if result is None:
        return ServiceError.LEVELS_NOT_FOUND

    return result


async def set_listed(
    ctx: Context,
    level_id: int,
    user_id: int,
    can_list_other: bool = False,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    if level.user_id != user_id and not can_list_other:
        return ServiceError.LEVELS_NO_UPDATE_PERMISSION

    result = await repositories.level.update_partial(
        ctx,
        level_id=level_id,
        publicity=LevelPublicity.PUBLIC,
    )

    if result is None:
        return ServiceError.LEVELS_NOT_FOUND

    return result


async def rate_level(
    ctx: Context,
    level_id: int,
    stars: int,
    difficulty: LevelDifficulty,
    coins_verified: bool,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)

    if level is None:
        return ServiceError.LEVELS_NOT_FOUND

    creator = await repositories.user.from_id(ctx, level.user_id)
    if creator is None:
        return ServiceError.USER_NOT_FOUND  # NOTE: Should never happen

    old_creator_points = gd_logic.calculate_creator_points(level)

    level = await repositories.level.update_partial(
        ctx,
        level_id,
        stars=stars,
        difficulty=difficulty,
        coins_verified=coins_verified,
    )

    if level is None:
        return ServiceError.LEVELS_NOT_FOUND

    creator_delta = gd_logic.calculate_creator_points(level) - old_creator_points

    await repositories.user.update_partial(
        ctx,
        creator.id,
        creator_points=creator.creator_points + creator_delta,
    )

    return level


async def nominate_magic(
    ctx: Context,
    level_id: int,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    search_flags = level.search_flags | LevelSearchFlag.MAGIC

    result = await repositories.level.update_partial(
        ctx,
        level_id=level_id,
        search_flags=search_flags,
    )

    if result is None:
        return ServiceError.LEVELS_NOT_FOUND

    return result


async def revoke_magic(
    ctx: Context,
    level_id: int,
) -> Level | ServiceError:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    search_flags = level.search_flags & ~LevelSearchFlag.MAGIC

    result = await repositories.level.update_partial(
        ctx,
        level_id=level_id,
        search_flags=search_flags,
    )

    if result is None:
        return ServiceError.LEVELS_NOT_FOUND

    return result
