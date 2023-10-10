from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import get_type_hints
from typing import Type
from typing import TypeVar

from rgdps import logger
from rgdps import repositories
from rgdps.constants.users import UserPrivileges
from rgdps.models.level import Level
from rgdps.models.user import User


async def _level_by_ref(ctx: CommandContext, ref_value: str) -> Level:
    if ref_value.isnumeric():
        res = await repositories.level.from_id(
            ctx,
            int(ref_value),
        )
    else:
        res = await repositories.level.from_name(
            ctx,
            ref_value,
        )

    if res is None:
        raise ValueError(...)

    return res


async def _user_by_ref(ctx: CommandContext, ref_value: str) -> User:
    if ref_value.isnumeric():
        res = await repositories.user.from_id(
            ctx,
            int(ref_value),
        )

    else:
        res = await repositories.user.from_name(
            ctx,
            ref_value,
        )

    if res is None:
        raise ValueError(...)

    return res


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


_CASTABLE = [
    str,
    int,
    float,
]


T = TypeVar("T")


async def _parse_to_type(ctx: CommandContext, value: str, cast: Type[T]) -> T:
    if cast in _CASTABLE:
        return cast(value)
    elif issubclass(cast, bool):
        return _bool_parse(value)
    elif issubclass(cast, Level):
        return await _level_by_ref(ctx, value)
    elif issubclass(cast, User):
        return await _user_by_ref(ctx, value)

    logger.error(
        "Command parser tried to parse an unsupported type!",
        extra={
            "value": value,
            "type": repr(cast),
        },
    )
    raise ValueError("Unsupported type!")


def _bool_parse(data: str) -> bool:
    if data in ("true", "1"):
        return True
    elif data in ("false", "0"):
        return False

    raise ValueError("Incorrect bool type provided.")


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
        annotations = get_type_hints(self.execute)
        split_params = ctx.params_str.split(" ")
        params = []

        for arg_type, value in zip(annotations.keys(), split_params):
            params.append(await _parse_to_type(ctx, value, arg_type))

        return params


class LevelCommand(Command):
    """Variant of command that may only be run on levels."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_level


class MessageCommand(Command):
    """Variant of command that may only be run on messages."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_message
