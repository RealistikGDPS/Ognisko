from __future__ import annotations

from rgdps.api.commands.framework import CommandContext
from rgdps.api.commands.framework import CommandRouter
from rgdps.api.commands.framework import unwrap_service
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User
from rgdps.usecases import users

router = CommandRouter("users_root")

# Main level command group.
user_group = CommandRouter("user")
router.register_command(user_group)


@user_group.register_function(required_privileges=UserPrivileges.USER_MODIFY_PRIVILEGES)
async def restrict(ctx: CommandContext, user: User | None = None) -> str:
    if user is None:
        user = ctx.user

    if user is None:
        return "You need to specify a user to restrict."

    unwrap_service(await users.restrict(ctx, user.id))

    return f"The user {user!r} has been restricted."


@user_group.register_function(required_privileges=UserPrivileges.USER_MODIFY_PRIVILEGES)
async def unrestrict(ctx: CommandContext, user: User | None = None) -> str:
    if user is None:
        user = ctx.user

    if user is None:
        return "You need to specify a user to unrestrict."

    unwrap_service(await users.unrestrict(ctx, user.id))

    return f"The user {user!r} has been unrestricted."


privileges_group = CommandRouter("privileges")
user_group.register_command(privileges_group)


@privileges_group.register_function(
    name="view",
    required_privileges=UserPrivileges.USER_MODIFY_PRIVILEGES,
)
async def privileges_view(ctx: CommandContext, user: User | None = None) -> str:
    if user is None:
        user = ctx.user

    if user is None:
        return "You need to specify a user to list privileges for."

    return f"The user {user!r} has the following privileges: {user.privileges!r}"


@privileges_group.register_function(
    name="set",
    required_privileges=UserPrivileges.USER_MODIFY_PRIVILEGES,
)
async def privileges_set(
    ctx: CommandContext,
    privileges: UserPrivileges,
    user: User | None = None,
) -> str:
    if user is None:
        user = ctx.user

    if user is None:
        return "You need to specify a user to set privileges for."

    unwrap_service(await users.update_privileges(ctx, user.id, privileges))

    return f"The user {user!r} has been set to have the following privileges: {privileges!r}"
