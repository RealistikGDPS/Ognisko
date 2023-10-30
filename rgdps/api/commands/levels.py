from __future__ import annotations

from rgdps.api.commands.framework import CommandContext
from rgdps.api.commands.framework import CommandRouter
from rgdps.api.commands.framework import unwrap_service
from rgdps.constants.errors import ServiceError
from rgdps.constants.levels import LevelDifficultyName
from rgdps.constants.users import UserPrivileges
from rgdps.models.level import Level
from rgdps.usecases import levels

router = CommandRouter("levels_root")
level_group = CommandRouter("level")
router.register_command(level_group)


@level_group.register_function(required_privileges=UserPrivileges.LEVEL_MARK_AWARDED)
async def award(ctx: CommandContext, level: Level | None = None) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to award."

    res = unwrap_service(await levels.nominate_awarded(ctx, level.id))

    return f"The level {level.name!r} has been awarded."


@level_group.register_function(required_privileges=UserPrivileges.LEVEL_MARK_AWARDED)
async def unaward(ctx: CommandContext, level: Level | None = None) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to unaward."

    res = unwrap_service(await levels.revoke_awarded(ctx, level.id))

    return f"The level {level.name!r} has been unawarded."


@level_group.register_function()
async def delete(ctx: CommandContext, level: Level | None = None) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to delete."

    res = unwrap_service(
        await levels.delete(
            ctx,
            level.id,
            ctx.user.id,
            ctx.user.privileges & UserPrivileges.LEVEL_DELETE_OTHER > 0,
        ),
    )

    return f"The level {level.name!r} has been deleted."


@level_group.register_function()
async def unlist(
    ctx: CommandContext,
    friends_only: bool = False,
    level: Level | None = None,
) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to unlist."

    res = unwrap_service(
        await levels.set_unlisted(
            ctx,
            level.id,
            ctx.user.id,
            friends_only,
            ctx.user.privileges & UserPrivileges.LEVEL_MODIFY_VISIBILITY > 0,
        ),
    )

    return f"The level {level.name!r} has been unlisted."


@level_group.register_function()
async def relist(
    ctx: CommandContext,
    level: Level | None = None,
) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to relist."

    res = unwrap_service(
        await levels.set_listed(
            ctx,
            level.id,
            ctx.user.id,
            ctx.user.privileges & UserPrivileges.LEVEL_MODIFY_VISIBILITY > 0,
        ),
    )

    return f"The level {level.name!r} has been re-listed."


@level_group.register_function()
async def description(
    ctx: CommandContext,
    description: str,
    level: Level | None = None,
) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to set the description of."

    res = unwrap_service(
        await levels.set_description(
            ctx,
            level.id,
            ctx.user.id,
            description,
            ctx.user.privileges & UserPrivileges.LEVEL_CHANGE_DESCRIPTION_OTHER > 0,
        ),
    )

    return f"The level {level.name!r} has had its description set."


@level_group.register_function(required_privileges=UserPrivileges.LEVEL_RATE_STARS)
async def rate(
    ctx: CommandContext,
    difficulty: LevelDifficultyName,
    stars: int = 0,
    coins_verified: bool = False,
) -> str:
    if ctx.level is None:
        return "This command can only be ran on levels."

    res = unwrap_service(
        await levels.rate_level(
            ctx,
            ctx.level.id,
            stars,
            difficulty.as_difficulty(),
            coins_verified,
        ),
    )

    return f"The level {ctx.level.name} has been rated!"


@level_group.register_function(required_privileges=UserPrivileges.LEVEL_MARK_MAGIC)
async def magic(
    ctx: CommandContext,
    level: Level | None = None,
) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to nominate as magic."

    res = unwrap_service(await levels.nominate_magic(ctx, level.id))

    return f"The level {level.name!r} has been nominated as magic."


@level_group.register_function(required_privileges=UserPrivileges.LEVEL_MARK_MAGIC)
async def unmagic(ctx: CommandContext, level: Level | None = None) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to revoke magic status."

    res = unwrap_service(await levels.revoke_magic(ctx, level.id))

    return f"The level {level.name!r}'s magic status has been revoked."
