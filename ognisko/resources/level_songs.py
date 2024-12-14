from __future__ import annotations

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseModelNoId


class LevelSongAssignModel(BaseModelNoId):
    __tablename__ = "level_song_assign"

    level_id = Column(Integer, nullable=False)
    song_id = Column(Integer, nullable=False)
    is_primary = Column(Boolean, nullable=False)


class LevelSongAssignRepository:
    def __init__(self, mysql: ImplementsMySQL) -> None:
        self._mysql = mysql

    async def from_level_id(
        self,
        level_id: int,
    ) -> list[LevelSongAssignModel]:
        query = self._mysql.select(LevelSongAssignModel).where(
            LevelSongAssignModel.level_id == level_id,
        )
        return await query.fetch_all()

    async def from_level_id_and_primary(
        self,
        level_id: int,
    ) -> LevelSongAssignModel | None:
        query = self._mysql.select(LevelSongAssignModel).where(
            LevelSongAssignModel.level_id == level_id,
            LevelSongAssignModel.is_primary == True,
        )
        return await query.fetch_one()
