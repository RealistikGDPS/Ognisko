from __future__ import annotations

from typing import Optional

from realistikgdps.constants.songs import SongSource
from realistikgdps.models.song import Song
from realistikgdps.state import services


async def from_id(song_id: int) -> Optional[Song]:
    song_db = await services.database.fetch_one(
        "SELECT id, name, author_id, author, author_youtube, size, "
        "download_url, source, blocked FROM songs WHERE id = :song_id",
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
        "download_url, source, blocked) VALUES "
        "(:name, :author_id, :author, :author_youtube, :size, "
        ":download_url, :source, :blocked)",
        {
            "name": song.name,
            "author_id": song.author_id,
            "author": song.author,
            "author_youtube": song.author_youtube,
            "size": song.size,
            "download_url": song.download_url,
            "source": song.source.value,
            "blocked": song.blocked,
        },
    )
