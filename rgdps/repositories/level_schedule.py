from __future__ import annotations

from datetime import datetime
from datetime import timedelta

from rgdps.common.context import Context
from rgdps.constants.level_schedules import LevelScheduleType
from rgdps.models.level_schedule import LevelSchedule


async def create(
    ctx: Context,
    schedule_type: LevelScheduleType,
    level_id: int,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    scheduled_by_id: int | None = None,
    schedule_id: int = 0,
) -> LevelSchedule:

    if start_time is None:
        start_time = datetime.now()

    # Not sure how I feel about having this sort of logic here.
    if schedule_type == LevelScheduleType.WEEKLY:
        end_time = start_time + timedelta(days=7)
    else:
        end_time = start_time + timedelta(days=1)

    schedule = LevelSchedule(
        id=schedule_id,
        type=schedule_type,
        level_id=level_id,
        start_time=start_time,
        end_time=end_time,
        scheduled_by_id=scheduled_by_id,
    )

    schedule.id = await ctx.mysql.execute(
        "INSERT INTO level_schedules (id, type, level_id, start_time, end_time, scheduled_by_id) "
        "VALUES (:id, :type, :level_id, :start_time, :end_time, :scheduled_by_id)",
        schedule.as_dict(include_id=True),
    )

    return schedule


async def from_id(
    ctx: Context,
    schedule_id: int,
) -> LevelSchedule | None:
    schedule_db = await ctx.mysql.fetch_one(
        "SELECT id, type, level_id, start_time, end_time, scheduled_by_id, deleted "
        "FROM level_schedules WHERE id = :schedule_id",
        {
            "schedule_id": schedule_id,
        },
    )

    if schedule_db is None:
        return None

    return LevelSchedule.from_mapping(schedule_db)


async def get_current(
    ctx: Context,
    schedule_type: LevelScheduleType,
) -> LevelSchedule | None:
    schedule_db = await ctx.mysql.fetch_one(
        "SELECT id, type, level_id, start_time, end_time, scheduled_by_id, deleted "
        "FROM level_schedules WHERE type = :schedule_type AND start_time <= NOW() AND end_time >= NOW()",
        {
            "schedule_type": schedule_type.value,
        },
    )

    if schedule_db is None:
        return None

    return LevelSchedule.from_mapping(schedule_db)


async def get_next(
    ctx: Context,
    schedule_type: LevelScheduleType,
) -> LevelSchedule | None:
    schedule_db = await ctx.mysql.fetch_one(
        "SELECT id, type, level_id, start_time, end_time, scheduled_by_id, deleted "
        "FROM level_schedules WHERE type = :schedule_type AND start_time >= NOW() ORDER BY start_time ASC LIMIT 1",
        {
            "schedule_type": schedule_type.value,
        },
    )

    if schedule_db is None:
        return None

    return LevelSchedule.from_mapping(schedule_db)


async def get_last(
    ctx: Context,
    schedule_type: LevelScheduleType,
) -> LevelSchedule | None:
    schedule_db = await ctx.mysql.fetch_one(
        "SELECT id, type, level_id, start_time, end_time, scheduled_by_id, deleted "
        "FROM level_schedules WHERE type = :schedule_type AND end_time <= NOW() ORDER BY end_time DESC LIMIT 1",
        {
            "schedule_type": schedule_type.value,
        },
    )

    if schedule_db is None:
        return None

    return LevelSchedule.from_mapping(schedule_db)
