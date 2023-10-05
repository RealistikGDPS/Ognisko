from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rgdps import logger
from rgdps.constants.users import UserPrivileges
from rgdps.models.level import Level
from rgdps.models.user import User


# TODO: Inject connection context (subclass of Context)
@dataclass
class CommandContext:
    user: User
    # Cases for comment and message commands.
    level: Level | None
    target_user: User | None

    # Debugging details
    params_str: str  # Prefix stripped.

    @property
    def is_level(self) -> bool:
        return self.level is not None

    @property
    def is_message(self) -> bool:
        return self.target_user is not None


class Command:
    """Inheritable command structure for implementing custom commands."""

    __slots__ = (
        "name",
        "description",
    )

    def __init__(
        self,
        name: str,
        description: str,
        required_privileges: UserPrivileges | None,
    ) -> None:
        self.name = name
        self.description = description
        self.required_privileges = required_privileges

    # Overridable definitions.
    async def handle(self, ctx: CommandContext) -> str:
        """Main command definition."""

        return "Hello, world!"

    async def should_run(self, ctx: CommandContext) -> bool:
        """Overridable function for custom definitions of execution criteria."""
        return True

    # Events
    async def on_exception(self, ctx: CommandContext, exception: Exception) -> str:
        logger.exception(
            "An exception has occurred while executing command!",
            extra={
                "command_name": self.name,
                "command_input": ctx.params_str,
                "user_id": ctx.user.id,
            },
            exc_info=exception,
        )
        return (
            "An exeption has occurred while executing this command! "
            "The developers have been notified."
        )

    async def on_privilege_fail(self, ctx: CommandContext) -> str:
        return "You have insufficient privileges to run this command."

    async def execute(self, ctx: CommandContext) -> str:
        """Called by the command router to perform command checks and execution."""

        # TODO: Parse `ctx.params_str`
        ...

    # Private API
    def __has_privileges(self, ctx: CommandContext) -> bool:
        if self.required_privileges:
            return (
                ctx.user.privileges & self.required_privileges
            ) == self.required_privileges

        return True

    async def __parse_params(self, ctx: CommandContext) -> list[Any]:
        # TODO: Parse the function signature of `self.handle`

        ...


class LevelCommand(Command):
    """Variant of command that may only be run on levels."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_level


class MessageCommand(Command):
    """Variant of command that may only be run on messages."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_message
