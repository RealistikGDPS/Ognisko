from __future__ import annotations

from datetime import datetime

from rgdps import repositories
from rgdps.constants.levels import LevelDifficulty
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelPublicity
from rgdps.constants.levels import LevelSearchFlags
from rgdps.models.level import Level
from rgdps.models.user import User


async def upload_level(
    user: User,
    name: str,
    description: str,
    custom_song_id: int,
    official_song_id: int,
    version: int,
    length: LevelLength,
    two_player: bool,
    publicity: LevelPublicity,
    render_str: str,
    game_version: int,
    binary_version: int,
    original_id: int,
    coins: int,
    requested_stars: int,
    low_detail_mode: bool,
    object_count: int,
    copy_password: int,
    building_time: int,
) -> Level:
    # TODO: Privilege checks.

    level = Level(
        id=0,
        name=name,
        user_id=user.id,
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
        upload_ts=datetime.now(),
        original_id=original_id,
        downloads=0,
        likes=0,
        stars=0,
        difficulty=LevelDifficulty.NA,
        demon_difficulty=None,
        coins=coins,
        coins_verified=False,
        requested_stars=requested_stars,
        feature_order=0,
        search_flags=LevelSearchFlags.NORMAL,
        low_detail_mode=low_detail_mode,
        object_count=object_count,
        copy_password=copy_password,
        building_time=building_time,
        update_locked=False,
        deleted=False,
    )

    level.id = await repositories.level.create(level)
    return level
