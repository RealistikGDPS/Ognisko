from __future__ import annotations

import asyncio

from ognisko.api.commands.framework import CommandContext
from ognisko.api.commands.framework import CommandRouter
from ognisko.constants.users import UserPrivileges
from ognisko.services import leaderboards
from ognisko.services import levels
from ognisko.services import users

router = CommandRouter("sunc_root")

# Main level command group.
sync_group = CommandRouter("sync")
router.register_command(sync_group)


@sync_group.register_function(
    name="levels",
    required_privileges=UserPrivileges.SERVER_RESYNC_SEARCH,
)
async def level_search(ctx: CommandContext) -> str:
    asyncio.create_task(levels.synchronise_search(ctx))

    return "Search synchronisation scheduled."


@sync_group.register_function(
    name="leaderboards",
    required_privileges=UserPrivileges.SERVER_RESYNC_LEADERBOARDS,
)
async def leaderboard_search(ctx: CommandContext) -> str:
    asyncio.create_task(leaderboards.synchronise_top_stars(ctx))
    asyncio.create_task(leaderboards.synchronise_top_creators(ctx))

    return "Leaderboard synchronisation scheduled."


@sync_group.register_function(
    name="users",
    required_privileges=UserPrivileges.SERVER_RESYNC_SEARCH,
)
async def user_search(ctx: CommandContext) -> str:
    asyncio.create_task(users.synchronise_search(ctx))

    return "User search synchronisation scheduled."
