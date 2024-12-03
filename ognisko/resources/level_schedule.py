from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from ognisko.adapters import ImplementsMySQL
from ognisko.common import modelling
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class LevelScheduleModel(DatabaseModel):
    id: int
    type: LevelScheduleType
    level_id: int
    start_time: datetime
    end_time: datetime
    scheduled_by_id: int | None


class LevelScheduleType(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


ALL_FIELDS = modelling.get_model_fields(LevelScheduleModel)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)

_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)

_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


class LevelScheduleRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: ImplementsMySQL) -> None:
        self._mysql = mysql

    async def from_id(self, schedule_id: int) -> LevelScheduleModel | None:
        schedule_db = await self._mysql.fetch_one(
            f"SELECT * FROM level_schedule WHERE id = :schedule_id",
            {"schedule_id": schedule_id},
        )

        if schedule_db is None:
            return None

        return LevelScheduleModel(**schedule_db)

    async def create(
        self,
        schedule_type: LevelScheduleType,
        level_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        scheduled_by_id: int | None = None,
        schedule_id: int = 0,
    ) -> LevelScheduleModel:

        if start_time is None:
            start_time = datetime.now()

        # TODO: Move out scheduling logic to a service.
        if schedule_type == LevelScheduleType.WEEKLY:
            end_time = start_time + timedelta(days=7)
        else:
            end_time = start_time + timedelta(days=1)

        schedule = LevelScheduleModel(
            id=schedule_id,
            type=schedule_type,
            level_id=level_id,
            start_time=start_time,
            end_time=end_time,
            scheduled_by_id=scheduled_by_id,
        )

        schedule.id = await self._mysql.execute(
            f"INSERT INTO level_schedule ({_ALL_FIELDS_COMMA}) VALUES ({_ALL_FIELDS_COLON})",
            schedule.model_dump(),
        )

        return schedule

    async def current(
        self,
        schedule_type: LevelScheduleType,
    ) -> LevelScheduleModel | None:
        schedule_db = await self._mysql.fetch_one(
            "SELECT * FROM level_schedule WHERE type = :schedule_type "
            "AND start_time <= NOW() AND end_time >= NOW()",
            {"schedule_type": schedule_type.value},
        )

        if schedule_db is None:
            return None

        return LevelScheduleModel(**schedule_db)

    async def next(self, schedule_type: LevelScheduleType) -> LevelScheduleModel | None:
        schedule_db = await self._mysql.fetch_one(
            "SELECT * FROM level_schedule WHERE type = :schedule_type "
            "AND start_time > NOW() ORDER BY start_time ASC LIMIT 1",
            {"schedule_type": schedule_type.value},
        )

        if schedule_db is None:
            return None

        return LevelScheduleModel(**schedule_db)

    async def previous(
        self,
        schedule_type: LevelScheduleType,
    ) -> LevelScheduleModel | None:
        schedule_db = await self._mysql.fetch_one(
            "SELECT * FROM level_schedule WHERE type = :schedule_type "
            "AND end_time < NOW() ORDER BY end_time DESC LIMIT 1",
            {"schedule_type": schedule_type.value},
        )

        if schedule_db is None:
            return None

        return LevelScheduleModel(**schedule_db)

    async def last_n(
        self,
        schedule_type: LevelScheduleType,
        n: int,
    ) -> list[LevelScheduleModel]:
        schedules_db = await self._mysql.fetch_all(
            "SELECT * FROM level_schedule WHERE type = :schedule_type "
            "ORDER BY start_time DESC LIMIT :n",
            {"schedule_type": schedule_type.value, "n": n},
        )

        return [LevelScheduleModel(**schedule_db) for schedule_db in schedules_db]
