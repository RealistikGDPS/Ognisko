from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class LevelScheduleType(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


class LevelScheduleModel(DatabaseModel):
    interval = Column(Enum(LevelScheduleType), nullable=False)
    level_id = Column(Integer, nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    scheduled_by_user_id = Column(Integer, nullable=True)


class LevelScheduleRepository(BaseRepository[LevelScheduleModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, LevelScheduleModel)

    async def current(
        self,
        schedule_type: LevelScheduleType,
    ) -> LevelScheduleModel | None:
        return (
            await self._mysql.select(LevelScheduleModel)
            .where(
                LevelScheduleModel.interval == schedule_type,
                LevelScheduleModel.starts_at <= datetime.now(),
                LevelScheduleModel.ends_at >= datetime.now(),
            )
            .fetch_one()
        )

    async def next(self, schedule_type: LevelScheduleType) -> LevelScheduleModel | None:
        return (
            await self._mysql.select(LevelScheduleModel)
            .where(
                LevelScheduleModel.interval == schedule_type,
                LevelScheduleModel.starts_at > datetime.now(),
            )
            .order_by(LevelScheduleModel.starts_at)
            .limit(1)
            .fetch_one()
        )

    async def previous(
        self,
        schedule_type: LevelScheduleType,
    ) -> LevelScheduleModel | None:
        return (
            await self._mysql.select(LevelScheduleModel)
            .where(
                LevelScheduleModel.interval == schedule_type,
                LevelScheduleModel.ends_at < datetime.now(),
            )
            .order_by(LevelScheduleModel.ends_at.desc())
            .limit(1)
            .fetch_one()
        )

    async def last_n(
        self,
        schedule_type: LevelScheduleType,
        n: int,
    ) -> list[LevelScheduleModel]:
        return (
            await self._mysql.select(LevelScheduleModel)
            .where(
                LevelScheduleModel.interval == schedule_type,
            )
            .order_by(LevelScheduleModel.starts_at.desc())
            .limit(n)
            .fetch_all()
        )
