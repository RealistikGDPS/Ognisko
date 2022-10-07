from __future__ import annotations

import urllib.parse
from typing import Optional

from realistikgdps.common import gd_obj
from realistikgdps.constants.songs import SongSource
from realistikgdps.models.song import Song
from realistikgdps.state import services


async def from_db(song_id: int, allow_blocked: bool = False) -> Optional[Song]:
    song_db = await services.database.fetch_one(
        "SELECT id, name, author_id, author, author_youtube, size, "
        "download_url, source, blocked FROM songs WHERE id = :song_id"
        + " AND blocked = 0"
        if not allow_blocked
        else "",
        {
            "song_id": song_id,
        },
    )

    if song_db is None:
        return None

    return Song(
        id=song_db["id"],
        name=song_db["name"],
        author_id=song_db["author_id"],
        author=song_db["author"],
        author_youtube=song_db["author_youtube"],
        size=song_db["size"],
        download_url=song_db["download_url"],
        source=SongSource(song_db["source"]),
        blocked=song_db["blocked"],
    )


async def create(song: Song) -> int:
    return await services.database.execute(
        "INSERT INTO songs (name, author_id, author, author_youtube, size, "
        "download_url, source, blocked, id) VALUES "
        "(:name, :author_id, :author, :author_youtube, :size, "
        ":download_url, :source, :blocked, :id)",
        {
            "name": song.name,
            "author_id": song.author_id,
            "author": song.author,
            "author_youtube": song.author_youtube,
            "size": song.size,
            "download_url": song.download_url,
            "source": song.source.value,
            "blocked": song.blocked,
            "id": song.id,
        },
    )


async def from_boomlings(song_id: int) -> Optional[Song]:
    # May raise an exception in case of network issue.
    song_api = await services.http.post(
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
        download_url=song_data[10],
        source=SongSource.BOOMLINGS,
        blocked=False,
    )


async def from_id(song_id: int, allow_blocked: bool = False) -> Optional[Song]:
    # TODO: Implement song LRU Caching
    song_db = await from_db(song_id, allow_blocked)
    if song_db is not None:
        return song_db

    song_boomlings = await from_boomlings(song_id)
    if song_boomlings is not None:
        await create(song_boomlings)
        return song_boomlings

    return None
