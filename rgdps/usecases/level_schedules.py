from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import NamedTuple

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.level_schedules import LevelScheduleType
from rgdps.models.level import Level
from rgdps.models.level_schedule import LevelSchedule


async def schedule_next(
    ctx: Context,
    schedule_type: LevelScheduleType,
    level_id: int,
    scheduled_by_id: int | None = None,
) -> LevelSchedule | ServiceError:
    # Ensure the level works.
    level = await repositories.level.from_id(ctx, level_id)
    if level is None:
        return ServiceError.LEVELS_NOT_FOUND

    # Enqueue it after the next level of this type.
    prev_schedule = await repositories.level_schedule.get_last(
        ctx,
        schedule_type,
    )

    if prev_schedule is None:
        start_time = datetime.now()
    else:
        start_time = prev_schedule.end_time

    if schedule_type == LevelScheduleType.WEEKLY:
        end_time = start_time + timedelta(days=7)
    else:
        end_time = start_time + timedelta(days=1)

    schedule = await repositories.level_schedule.create(
        ctx,
        schedule_type,
        level_id,
        start_time,
        end_time,
        scheduled_by_id,
    )

    return schedule


class ScheduledLevel(NamedTuple):
    schedule: LevelSchedule
    level: Level


async def get_current(
    ctx: Context,
    schedule_type: LevelScheduleType,
) -> ScheduledLevel | ServiceError:
    schedule = await repositories.level_schedule.get_current(
        ctx,
        schedule_type,
    )

    if schedule is None:
        # TODO: Algorithm to automatically nominate a level. (should be implemented soon)
        return ServiceError.LEVEL_SCHEDULE_UNSET

    level = await repositories.level.from_id(
        ctx,
        schedule.level_id,
    )
