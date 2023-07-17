from __future__ import annotations

from datetime import datetime
from typing import NamedTuple
from typing import Optional
from typing import Union

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlag
from rgdps.constants.levels import LevelSearchType
from rgdps.constants.users import UserPrivileges
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
    original: int,
    official_song_id: int,
    game_version: int,
    binary_version: int,
    low_detail_mode: bool,
    building_time: int,
) -> Union[Level, ServiceError]:
    # TODO: Validation
    # TODO: Description validation
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
    if level_id and (old_level := await repositories.level.from_id(ctx, level_id)):
        # Update
        if old_level.user_id != user_id:
            return ServiceError.LEVELS_NO_UPDATE_PERMISSION
        if old_level.update_locked:
            return ServiceError.LEVELS_UPDATE_LOCKED

        # Apply new values to the old level.
        level = old_level
        level.name = name
        level.custom_song_id = song_id
        level.official_song_id = track_id
        level.two_player = two_player
        level.coins = coins
        level.publicity = publicity
        level.render_str = render_str
        level.requested_stars = requested_stars
        level.length = length
        level.version = version
        level.description = description
        level.original_id = original
        level.game_version = game_version
        level.binary_version = binary_version
        level.low_detail_mode = low_detail_mode
        level.building_time = building_time
        level.update_ts = datetime.utcnow()
        await repositories.level.update(ctx, level)
        repositories.level_data.create(ctx, level.id, level_data)
    else:
        level = Level(
            id=level_id,
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
            upload_ts=datetime.now(),
            update_ts=datetime.now(),
            original_id=original or None,
            downloads=0,
            likes=0,
            stars=0,
            difficulty=LevelDifficulty.NA,
            demon_difficulty=None,
            coins=coins,
            coins_verified=False,
            requested_stars=requested_stars,
            feature_order=0,
            search_flags=LevelSearchFlag.NONE,
            low_detail_mode=low_detail_mode,
            object_count=object_count,
            copy_password=copy_password,
            building_time=building_time,
            update_locked=False,
            deleted=False,
        )
        level.id = await repositories.level.create(ctx, level)
        repositories.level_data.create(ctx, level.id, level_data)

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
) -> Union[SearchResponse, ServiceError]:
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

    songs = []
    users = set()
    for level in levels_db.results:
        user = await repositories.user.from_id(ctx, level.user_id)
        assert user is not None, "User associated with level not found."
        users.add(user)
        if level.custom_song_id:
            songs.append(await repositories.song.from_id(ctx, level.custom_song_id))

    if lookup_level:
        # Move to the top.
        if lookup_level in levels_db.results:
            levels_db.results.remove(lookup_level)
        levels_db.results.insert(0, lookup_level)
        users.add(await repositories.user.from_id(ctx, lookup_level.user_id))

    return SearchResponse(
        levels=levels_db.results,
        total=levels_db.total + (1 if lookup_level else 0),
        songs=songs,
        users=list(users),
    )


# Fun fact, gd relies on the search endpoint for song and user data.
class LevelResponse(NamedTuple):
    level: Level
    data: str


async def get(ctx: Context, level_id: int) -> Union[LevelResponse, ServiceError]:
    level = await repositories.level.from_id(ctx, level_id)
    level_data = repositories.level_data.from_level_id(ctx, level_id)
    if not (level and level_data):
        return ServiceError.LEVELS_NOT_FOUND

    # Handle stats updates
    level.downloads += 1

    await repositories.level.update(ctx, level)

    return LevelResponse(
        level=level,
        data=level_data,
    )


async def delete(ctx: Context, level_id: int, user: User) -> Union[bool, ServiceError]:
    level = await repositories.level.from_id(ctx, level_id)
    if not level:
        return ServiceError.LEVELS_NOT_FOUND

    # TODO: Check if user has permission to delete.
    if level.user_id != user.id:
        return ServiceError.LEVELS_NO_DELETE_PERMISSION

    level.deleted = True
    await repositories.level.update(ctx, level)
    await repositories.level.delete_meili(ctx, level_id)
    return True


async def synchronise_search(ctx: Context) -> Union[bool, ServiceError]:
    """Synchronise the search index with the backing database.
    Should be rarely used as its demanding on resources.
    """

    levels = await repositories.level.all_ids(ctx)

    for level_id in levels:
        level = await repositories.level.from_id(ctx, level_id)
        # It got deleted while we were iterating.
        if (not level) or level.deleted:
            continue
        await repositories.level.update_meili(ctx, level)

    return True
