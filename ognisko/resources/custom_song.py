from __future__ import annotations

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class SongSource(StrEnum):
    BOOMLINGS = "boomlings"
    NEWGROUNDS = "newgrounds"
    CUSTOM = "custom"


class CustomSongModel(DatabaseModel):
    name = Column(String, nullable=False)
    author_id = Column(Integer, nullable=False)
    author_name = Column(String, nullable=False)
    author_youtube = Column(String, nullable=True)
    file_size = Column(Float, nullable=False)
    file_download_url = Column(String, nullable=False)
    sourced_from = Column(Enum(SongSource), nullable=False)
    is_blocked = Column(Boolean, nullable=False)


class CustomSongRepository(BaseRepository[CustomSongModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, CustomSongModel)
