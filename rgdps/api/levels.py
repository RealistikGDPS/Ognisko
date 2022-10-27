from __future__ import annotations

from fastapi import Form

from rgdps import logger
from rgdps.common import gd_obj
from rgdps.constants.errors import ServiceError
from rgdps.constants.responses import GenericResponse
from rgdps.usecases import songs


async def get_song_info(
    song_id: int = Form(..., alias="songID"),
) -> str:

    song = await songs.get(song_id)
    if isinstance(song, ServiceError):
        logger.info(f"Failed to fetch song with error {song!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully fetched song {song}.")
    return gd_obj.dumps(gd_obj.create_song(song), sep="~|~")
