from __future__ import annotations

import urllib.parse

from rgdps import logger
from rgdps.common import gd_obj
from rgdps.common.context import Context
from rgdps.constants.songs import SongSource
from rgdps.models.song import Song


async def from_db(
    ctx: Context,
    song_id: int,
    allow_blocked: bool = False,
) -> Song | None:
    song_db = await ctx.mysql.fetch_one(
        "SELECT id, name, author_id, author, author_youtube, size, "
        "download_url, source, blocked FROM songs WHERE id = :song_id "
        "AND blocked IN :blocked",
        {
            "song_id": song_id,
            "blocked": (0, 1) if allow_blocked else (0,),
        },
    )

    if song_db is None:
        return None

    return Song.from_mapping(song_db)

async def multiple_from_db(
    ctx: Context,
    song_ids: list[int],
    allow_blocked: bool = False,
) -> list[Song]:
    songs_db = await ctx.mysql.fetch_all(
        "SELECT id, name, author_id, author, author_youtube, size, "
        "download_url, source, blocked FROM songs WHERE id IN :song_ids "
        "AND blocked IN :blocked",
        {
            "song_ids": tuple(song_ids),
            "blocked": (0, 1) if allow_blocked else (0,),
        },
    )

    return [Song.from_mapping(song_db) for song_db in songs_db]


async def _create_sql(ctx: Context, song: Song) -> int:
    return await ctx.mysql.execute(
        "INSERT INTO songs (name, author_id, author, author_youtube, size, "
        "download_url, source, blocked, id) VALUES "
        "(:name, :author_id, :author, :author_youtube, :size, "
        ":download_url, :source, :blocked, :id)",
        song.as_dict(include_id=True),
    )


async def create(
    ctx: Context,
    name: str,
    author_id: int,
    author: str,
    download_url: str,
    author_youtube: str | None = None,
    size: float = 0.0,
    source: SongSource = SongSource.CUSTOM,
    blocked: bool = False,
    song_id: int = 0,
) -> Song:

    song = Song(
        id=song_id,
        name=name,
        author_id=author_id,
        author=author,
        author_youtube=author_youtube,
        size=size,
        download_url=download_url,
        source=source,
        blocked=blocked,
    )

    song.id = await ctx.mysql.execute(
        "INSERT INTO songs (id, name, author_id, author, author_youtube, size, "
        "download_url, source, blocked) VALUES "
        "(:id, :name, :author_id, :author, :author_youtube, :size, "
        ":download_url, :source, :blocked)",
        song.as_dict(include_id=True),
    )

    return song


async def from_boomlings(ctx: Context, song_id: int) -> Song | None:
    # May raise an exception in case of network issue.
    song_api = await ctx.http.post(
        "http://www.boomlings.com/database/getGJSongInfo.php",
        data={
            "secret": "Wmfd2893gb7",
            "songID": song_id,
        },
        timeout=2,
        headers={
            "User-Agent": "",
        },
    )

    # Endpoint always returns a 200 HTTP code, result to checking the format.
    response_data = song_api.content.decode()

    logger.debug(
        "Crawled song data from Boomlings.",
        extra={
            "song_id": song_id,
            "response_data": response_data,
        },
    )

    if "~|~" not in response_data:
        return None

    song_data = gd_obj.loads(
        data=response_data,
        sep="~|~",
    )

    # TODO: maybe make a gd_obj.load_song
    return Song(
        id=int(song_data[1]),
        name=song_data[2],
        author_id=int(song_data[3]),
        author=song_data[4],
        author_youtube=song_data[7] or None,
        size=float(song_data[5]),
        download_url=urllib.parse.unquote(song_data[10]),
        source=SongSource.BOOMLINGS,
        blocked=False,
    )


async def from_id(
    ctx: Context,
    song_id: int,
    allow_blocked: bool = False,
) -> Song | None:
    # TODO: Implement song LRU Caching
    song_db = await from_db(ctx, song_id, allow_blocked)
    if song_db is not None:
        return song_db

    song_boomlings = await from_boomlings(ctx, song_id)
    if song_boomlings is not None:
        await _create_sql(ctx, song_boomlings)
        return song_boomlings

    return None

async def multiple_from_id(
    ctx: Context,
    song_ids: list[int],
    allow_blocked: bool = False,
) -> list[Song]:
    if not song_ids:
        return []

    songs: list[Song] = []

    db_songs = await multiple_from_db(ctx, song_ids, allow_blocked)
    songs.extend(db_songs)

    db_song_ids = [db_song.id for db_song in db_songs]
    unsaved_song_ids = [song_id for song_id in song_ids if song_id not in db_song_ids]
    for unsaved_song_id in unsaved_song_ids:
        song_boomlings = await from_boomlings(ctx, unsaved_song_id)
        if song_boomlings is not None:
            await _create_sql(ctx, song_boomlings)
            songs.append(song_boomlings)

    # since we fetch from cache first and db for the rest
    # songs may not be in the same order they were provided in
    songs.sort(key=lambda song: song_ids.index(song.id))

    return songs


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM songs")
