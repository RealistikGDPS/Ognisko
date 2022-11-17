from __future__ import annotations

from datetime import datetime
from typing import NamedTuple
from typing import Union

from rgdps import repositories
from rgdps.constants.errors import ServiceError
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlags
from rgdps.models.level import Level
from rgdps.models.song import Song
from rgdps.models.user import User


async def create_or_update(
    user: User,
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
    # TODO: Permission checks
    # TODO: Description validation
    if custom_song_id:
        track_id = None
        song_id = custom_song_id

        if not await repositories.song.from_id(song_id):
            return ServiceError.LEVELS_INVALID_CUSTOM_SONG
    else:
        song_id = None
        track_id = official_song_id

    # TODO: Add more logic here.
    if unlisted:
        publicity = LevelPublicity.FRIENDS_UNLISTED
    else:
        publicity = LevelPublicity.PUBLIC

    level = Level(
        id=level_id,
        name=name,
        user_id=user.id,
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
        search_flags=LevelSearchFlags.NONE,
        low_detail_mode=low_detail_mode,
        object_count=object_count,
        copy_password=copy_password,
        building_time=building_time,
        update_locked=False,
        deleted=False,
    )

    # Check if we are updating or creating.
    if level_id and (old_level := await repositories.level.from_id(level_id)):
        # Update
        if old_level.user_id != user.id:
            return ServiceError.LEVELS_NO_UPDATE_PERMISSION
        if old_level.update_locked:
            return ServiceError.LEVELS_UPDATE_LOCKED
        await repositories.level.update(level)
        repositories.level_data.create(level.id, level_data)
    else:
        level.id = await repositories.level.create(level)
        repositories.level_data.create(level.id, level_data)

    return level


class SearchResponse(NamedTuple):
    levels: list[Level]
    total: int

    songs: list[Song]
    users: list[User]


async def search(
    query: str,
    page: int,
    page_size: int,
) -> Union[SearchResponse, ServiceError]:
    levels_db = await repositories.level.search_text(query, page, page_size)

    songs = []
    users = []
    for level in levels_db.results:
        users.append(await repositories.user.from_id(level.user_id))
        if level.custom_song_id:
            songs.append(await repositories.song.from_id(level.custom_song_id))

    return SearchResponse(
        levels=levels_db.results,
        total=levels_db.total,
        songs=songs,
        users=users,
    )


# Fun fact, gd relies on the search endpoint for song and user data.
class LevelResponse(NamedTuple):
    level: Level
    data: str


async def get(level_id: int) -> Union[LevelResponse, ServiceError]:
    level = await repositories.level.from_id(level_id)
    level_data = repositories.level_data.from_level_id(level_id)
    if not (level and level_data):
        return ServiceError.LEVELS_NOT_FOUND

    # Handle stats updates
    level.downloads += 1

    await repositories.level.update(level)

    return LevelResponse(
        level=level,
        data=level_data,
    )
