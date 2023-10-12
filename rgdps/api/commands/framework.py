from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import get_type_hints
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

from rgdps import logger
from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.users import UserPrivileges
from rgdps.models.level import Level
from rgdps.models.user import User

if TYPE_CHECKING:
    import httpx
    from meilisearch_python_async import Client as MeiliClient
    from redis.asyncio import Redis

    from rgdps.models.user import User
    from rgdps.common.cache.base import AbstractAsyncCache
    from rgdps.services.mysql import AbstractMySQLService
    from rgdps.services.storage import AbstractStorage


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


# TODO: Inject connection context (subclass of Context)
@dataclass
class CommandContext(Context):
    user: User
    # Cases for comment and message commands.
    level: Level | None
    target_user: User | None

    # Debugging details
    params: list[str]  # Prefix and name stripped.

    _base_context: Context

    @property
    def is_level(self) -> bool:
        return self.level is not None

    @property
    def is_message(self) -> bool:
        return self.target_user is not None

    # Implementation of context requirements
    @property
    def mysql(self) -> AbstractMySQLService:
        return self._base_context.mysql

    @property
    def redis(self) -> Redis:
        return self._base_context.redis

    @property
    def meili(self) -> MeiliClient:
        return self._base_context.meili

    @property
    def storage(self) -> AbstractStorage:
        return self._base_context.storage

    @property
    def user_cache(self) -> AbstractAsyncCache[User]:
        return self._base_context.user_cache

    @property
    def password_cache(self) -> AbstractAsyncCache[str]:
        return self._base_context.password_cache

    @property
    def http(self) -> httpx.AsyncClient:
        return self._base_context.http


def _parse_params(param_str: str) -> list[str]:
    # TODO: Implement multi-word strings surrounded by quotations marks.
    # TODO: maybe kwargs?
    return param_str.split(" ")


"""
def register(
        self,
        channel: str,
    ) -> Callable[[RedisHandler], RedisHandler]:
        def decorator(handler: RedisHandler) -> RedisHandler:
            self._routes[channel.encode()] = handler
            return handler

        return decorator
"""


class CommandRouter:
    def __init__(self) -> None:
        self._routes: dict[str, CommandRoutable] = {}

    def register_command(self, command: CommandRoutable) -> None:
        self._routes[command.name] = command

    # def register(self) ->

    async def execute(self, command: str, base_ctx: Context) -> str:
        try:
            parsed_params = _parse_params(command)
        except ValueError:
            return await self.on_invalid_format()

    # Events
    async def on_command_not_found(self, ctx: CommandContext, name: str) -> str:
        return "Could not find a command with the given name!"

    async def on_invalid_format(self) -> str:
        return "Incorrect command format! Could not parse the given input."


class CommandRoutable(ABC):
    name: str

    @abstractmethod
    async def execute(self, ctx: CommandContext) -> str:
        ...


class Command(CommandRoutable):
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
                "command_input": ctx.params,
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

    # TODO: Provide more information.
    async def on_argument_fail(self, ctx: CommandContext) -> str:
        return "Incorrect arguments provided!"

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        return "Insufficient conditions to run this command!"

    async def execute(self, ctx: CommandContext) -> str:
        """Called by the command router to perform command checks and execution."""

        if not self.__has_privileges(ctx):
            return await self.on_privilege_fail()

        if not await self.should_run(ctx):
            return await self.on_cannot_run(ctx)

        try:
            params = await self.__parse_params(ctx)
        except ValueError:
            return await self.on_argument_fail(ctx)

        try:
            return await self.handle(ctx, *params)
        except Exception as e:
            logger.exception(
                "Failed to run command handler!",
                extra={
                    "command_name": self.name,
                    "command_input": ctx.params,
                    "user_id": ctx.user.id,
                },
            )
            return await self.on_exception(ctx, e)

    # Private API
    def __has_privileges(self, ctx: CommandContext) -> bool:
        if self.required_privileges:
            return (
                ctx.user.privileges & self.required_privileges
            ) == self.required_privileges

        return True

    async def __parse_params(self, ctx: CommandContext) -> list[Any]:
        annotations = get_type_hints(self.execute)
        params = []

        if len(annotations) != len(ctx.params):
            raise ValueError("Insufficient number of command parametres provided.")

        for arg_type, value in zip(annotations.keys(), ctx.params):
            params.append(await _parse_to_type(ctx, value, arg_type))

        return params


class LevelCommand(Command):
    """Variant of command that may only be run on levels."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_level

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        return "This command can only be ran on levels!"


class MessageCommand(Command):
    """Variant of command that may only be run on messages."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_message

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        return "This command can only be ran in user messages!"
