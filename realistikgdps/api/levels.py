from __future__ import annotations

from fastapi import Form

from realistikgdps import logger
from realistikgdps.common import gd_obj
from realistikgdps.constants.errors import ServiceError
from realistikgdps.constants.responses import GenericResponse
from realistikgdps.usecases import songs


async def get_song_info(
    song_id: int = Form(..., alias="songID"),
) -> str:

    song = await songs.get(song_id)
    if isinstance(song, ServiceError):
        logger.info(f"Failed to fetch song with error {song!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully fetched song {song}.")
    return gd_obj.dumps(gd_obj.create_song(song), sep="~|~")
