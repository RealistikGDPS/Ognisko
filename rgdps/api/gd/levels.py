from __future__ import annotations

from typing import Optional

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common import gd_obj
from rgdps.common.validators import Base64String
from rgdps.constants.errors import ServiceError
from rgdps.constants.levels import LevelLength
from rgdps.constants.levels import LevelSearchType
from rgdps.constants.responses import GenericResponse
from rgdps.models.user import User
from rgdps.usecases import levels
from rgdps.usecases import songs


async def get_song_info(
    ctx: HTTPContext = Depends(),
    song_id: int = Form(..., alias="songID"),
) -> str:

    song = await songs.get(ctx, song_id)
    if isinstance(song, ServiceError):
        logger.info(f"Failed to fetch song with error {song!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully fetched song {song}.")
    return gd_obj.dumps(gd_obj.create_song(song), sep="~|~")


async def upload_level(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    level_id: int = Form(..., alias="levelID"),
    name: str = Form(..., alias="levelName", max_length=32),  # TODO: Verify
    custom_song_id: int = Form(..., alias="songID"),
    copy_password: int = Form(..., alias="password"),
    two_player: bool = Form(..., alias="twoPlayer"),
    object_count: int = Form(..., alias="objects"),
    coins: int = Form(...),
    unlisted: bool = Form(..., alias="unlisted"),
    render_str: str = Form(..., alias="extraString"),
    requested_stars: int = Form(..., alias="requestedStars", ge=0, le=10),
    level_data: str = Form(..., alias="levelString"),
    length: LevelLength = Form(..., alias="levelLength"),
    version: int = Form(..., alias="levelVersion"),
    description: Base64String = Form("", alias="levelDesc"),
    original: int = Form(..., alias="original"),
    official_song_id: int = Form(..., alias="audioTrack"),
    game_version: int = Form(..., alias="gameVersion"),
    binary_version: int = Form(..., alias="binaryVersion"),
    low_detail_mode: bool = Form(..., alias="ldm"),
    building_time: int = Form(..., alias="wt2"),
) -> str:

    level = await levels.create_or_update(
        ctx,
        user=user,
        level_id=level_id,
        name=name,
        custom_song_id=custom_song_id,
        copy_password=copy_password,
        two_player=two_player,
        object_count=object_count,
        coins=coins,
        unlisted=unlisted,
        render_str=render_str,
        requested_stars=requested_stars,
        level_data=level_data,
        length=length,
        version=version,
        description=description,
        original=original,
        official_song_id=official_song_id,
        game_version=game_version,
        binary_version=binary_version,
        low_detail_mode=low_detail_mode,
        building_time=building_time,
    )

    if isinstance(level, ServiceError):
        logger.info(f"Failed to upload level with error {level!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully uploaded level {level}.")
    return str(level.id)


PAGE_SIZE = 10


async def search_levels(
    ctx: HTTPContext = Depends(),
    query: str = Form("", alias="str"),
    page: int = Form(0, alias="page", ge=0),
    search_type: LevelSearchType = Form(LevelSearchType.MOST_LIKED, alias="type"),
    level_lengths: str = Form(..., alias="len"),
    completed_levels: Optional[str] = Form(None, alias="completedLevels"),
    featured: bool = Form(...),
    original: bool = Form(...),
    two_player: bool = Form(..., alias="twoPlayer"),
    unrated: bool = Form(False, alias="noStar"),
    rated: bool = Form(False, alias="star"),
    song_id: Optional[int] = Form(None, alias="song"),
    custom_song_id: Optional[int] = Form(None, alias="customSong"),
    followed_list: Optional[str] = Form(None, alias="followed"),
) -> str:

    if level_lengths != "-":
        level_length_list = [
            LevelLength(x) for x in gd_obj.comma_separated_ints(level_lengths)
        ]
    else:
        level_length_list = None

    if completed_levels is not None:
        completed_levels_list = gd_obj.comma_separated_ints(completed_levels)
    else:
        completed_levels_list = None

    if followed_list is not None:
        followed_list_list = gd_obj.comma_separated_ints(followed_list)
    else:
        followed_list_list = None

    level_res = await levels.search(
        ctx,
        page=page,
        page_size=PAGE_SIZE,
        query=query,
        search_type=search_type,
        level_lengths=level_length_list,
        completed_levels=completed_levels_list,
        featured=featured,
        original=original,
        two_player=two_player,
        unrated=unrated,
        rated=rated,
        song_id=song_id,
        custom_song_id=custom_song_id,
        followed_list=followed_list_list,
    )

    if isinstance(level_res, ServiceError):
        logger.info(f"Failed to search levels with error {level_res!r}.")
        return str(GenericResponse.FAIL)

    logger.info(
        f"Successfully fulfilled the search for query {query!r} with "
        f"{level_res.total} results.",
    )

    return "#".join(
        (
            "|".join(
                gd_obj.dumps(gd_obj.create_level_minimal(level))
                for level in level_res.levels
            ),
            "|".join(
                gd_obj.dumps(gd_obj.create_profile(user)) for user in level_res.users
            ),
            "~|~".join(
                gd_obj.dumps(gd_obj.create_song(song)) for song in level_res.songs
            ),
            gd_obj.create_pagination_info(level_res.total, page, PAGE_SIZE),
            gd_obj.create_search_security_str(level_res.levels),
        ),
    )


async def get_level(
    ctx: HTTPContext = Depends(),
    level_id: int = Form(..., alias="levelID"),
) -> str:

    level_res = await levels.get(ctx, level_id)

    if isinstance(level_res, ServiceError):
        logger.info(f"Failed to fetch level with error {level_res!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully fetched level {level_res.level}.")

    return "#".join(
        (
            gd_obj.dumps(gd_obj.create_level(level_res.level, level_res.data)),
            gd_obj.create_level_data_security_str(level_res.data),
            gd_obj.create_level_metadata_security_str_hashed(level_res.level),
            gd_obj.create_level_metadata_security_str(level_res.level),
        ),
    )
