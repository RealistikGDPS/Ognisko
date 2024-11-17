from __future__ import annotations

from ognisko.api.commands.framework import CommandContext
from ognisko.api.commands.framework import CommandRouter
from ognisko.api.commands.framework import unwrap_service
from ognisko.constants.level_schedules import LevelScheduleType
from ognisko.constants.users import UserPrivileges
from ognisko.services import level_schedules

router = CommandRouter("schedule_root")

# Main level command group.
schedule = CommandRouter("schedule")
router.register_command(schedule)


@schedule.register_function(required_privileges=UserPrivileges.LEVEL_ENQUEUE_WEEKLY)
async def weekly(ctx: CommandContext) -> str:
    """Enqueues the current level to be the next weekly level."""

    if ctx.level is None:
        return "Please run this command on a level."

    result = unwrap_service(
        await level_schedules.schedule_next(
            ctx,
            LevelScheduleType.WEEKLY,
            ctx.level.id,
            ctx.user.id,
        ),
    )

    return f"The level {ctx.level.name!r} has been scheduled for {result.start_time}."


@schedule.register_function(required_privileges=UserPrivileges.LEVEL_ENQUEUE_DAILY)
async def daily(ctx: CommandContext) -> str:
    """Enqueues the current level to be the next daily level."""

    if ctx.level is None:
        return "Please run this command on a level."

    result = unwrap_service(
        await level_schedules.schedule_next(
            ctx,
            LevelScheduleType.DAILY,
            ctx.level.id,
            ctx.user.id,
        ),
    )

    return f"The level {ctx.level.name!r} has been scheduled for {result.start_time}."
