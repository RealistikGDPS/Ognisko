from __future__ import annotations

from rgdps.api.commands.framework import CommandContext
from rgdps.api.commands.framework import CommandRouter
from rgdps.api.commands.framework import LevelCommand
from rgdps.api.commands.framework import make_command
from rgdps.constants.errors import ServiceError
from rgdps.constants.users import UserPrivileges
from rgdps.usecases import levels

router = CommandRouter("levels_root")
level_group = CommandRouter("level")
router.register_command(level_group)


@level_group.register()
class AwardLevelCommand(LevelCommand):
    def __init__(self) -> None:
        super().__init__(
            name="award",
            description="Adds a level to the awarded search.",
            required_privileges=UserPrivileges.LEVEL_MARK_AWARDED,
        )

    async def execute(self, ctx: CommandContext) -> str:
        assert ctx.level is not None

        res = await levels.award(ctx, ctx.level.id)

        if isinstance(res, ServiceError):
            return f"Failed to award level with error {res!r}!"

        return f"The level {ctx.level.name!r} has been awarded."


@level_group.register()
class UnawardLevelCommand(LevelCommand):
    def __init__(self) -> None:
        super().__init__(
            name="unaward",
            description="Removes a level from the awarded search.",
            required_privileges=UserPrivileges.LEVEL_MARK_AWARDED,
        )

    async def execute(self, ctx: CommandContext) -> str:
        assert ctx.level is not None

        res = await levels.unaward(ctx, ctx.level.id)

        if isinstance(res, ServiceError):
            return f"Failed to unaward level with error {res!r}!"

        return f"The level {ctx.level.name!r} has been unawarded."
