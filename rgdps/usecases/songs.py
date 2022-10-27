from __future__ import annotations

from typing import Optional
from typing import Union

from rgdps import repositories
from rgdps.constants.errors import ServiceError
from rgdps.models.song import Song


async def get(song_id: int) -> Union[Song, ServiceError]:
    song = await repositories.song.from_id(song_id)
    if song is None:
        # This could mean req fail too
        return ServiceError.SONGS_NOT_FOUND

    return song
