from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseModelNoId


class LevelSoundEffectAssignModel(BaseModelNoId):
    __tablename__ = "level_sound_effect_assign"

    level_id = Column(Integer, nullable=False)
    sound_effect_id = Column(Integer, nullable=False)


class LevelSoundEffectRepository:
    def __init__(self, mysql: ImplementsMySQL) -> None:
        self._mysql = mysql

    async def from_level_id(
        self,
        level_id: int,
    ) -> list[LevelSoundEffectAssignModel]:
        query = self._mysql.select(LevelSoundEffectAssignModel).where(
            LevelSoundEffectAssignModel.level_id == level_id,
        )
        return await query.fetch_all()
