from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import get_type_hints
from typing import Protocol
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


# Private parsing functions.
_CASTABLE = [
    str,
    int,
    float,
]
SupportedTypes = str | int | float | bool | Level | User


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
        raise ValueError("Could not find level from the given reference!")

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
        raise ValueError("Could not find user from the given reference!")

    return res


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
    data = data.lower()
    if data in ("true", "1"):
        return True
    elif data in ("false", "0"):
        return False

    raise ValueError("Incorrect bool type provided.")


def _parse_params(param_str: str) -> list[str]:
    # TODO cleanup.
    # TODO: maybe kwargs?
    if param_str.count('"') % 2 != 0:
        raise ValueError("Unbalanced quotes!")

    param_str = param_str.strip()
    if not param_str:
        raise ValueError("Could not parse parameters!")

    quote_detection = param_str.split('"')
    # Issue if the last character is a quote, it will be an empty string.
    if param_str[-1] == '"':
        quote_detection = quote_detection[:-1]

    # All even indexes are outside quotes, all odd indexes are inside quotes.
    params = []
    for idx, value in enumerate(quote_detection):
        value = value.strip()
        if idx % 2 == 0:
            # Outside quotes, split by spaces.
            params.extend(value.split(" "))
        else:
            # Inside quotes, do not split.
            params.append(value)

    return params


async def _cast_params(
    ctx: CommandContext,
    annotations: dict[str, Any],
) -> list[Any]:
    params = []

    if len(annotations) != len(ctx.params):
        raise ValueError("Insufficient number of command parametres provided.")

    for arg_type, value in zip(annotations.keys(), ctx.params):
        params.append(await _parse_to_type(ctx, value, arg_type))

    return params


@dataclass
class CommandContext(Context):
    """A context object for command handlers, implementing the common
    `Context` API."""

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


class CommandRoutable(ABC):
    """An abstract class defining interfaces that `CommandRouter` can use to
    execute commands."""

    name: str

    @abstractmethod
    async def execute(self, ctx: CommandContext) -> str:
        ...


class CommandRouter:
    """An (optionally) inheritable command router class, responible for
    registering and executing commands handlers. Supports nesting routers
    for command groups."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._routes: dict[str, CommandRoutable] = {}

    def register_command(self, command: CommandRoutable) -> None:
        self._routes[command.name] = command

    def merge(self, router: CommandRouter) -> None:
        """Combines the routes of two routers, overriding old entries
        with new ones (raises a warning)."""

        for key, value in router._routes.items():
            if key in self._routes:
                logger.warning(
                    "Command router merge has overwritten an existing command!",
                    extra={
                        "command": key,
                        "source": router.name,
                        "target": self.name,
                    },
                )
            self._routes[key] = value

    # def register(self) ->

    async def entrypoint(
        self,
        command: str,
        user: User,
        base_ctx: Context,
        level: Level | None = None,
        target_user: User | None = None,
    ) -> str:
        """Defines an entrypoint for command execution. This method is
        supposed to be the first one called when executing a command."""

        try:
            parsed_params = _parse_params(command)
        except ValueError:
            return await self.on_invalid_format()

        command_name = parsed_params[0]
        params = parsed_params[1:]

        ctx = CommandContext(
            user=user,
            level=level,
            target_user=target_user,
            params=params,
            _base_context=base_ctx,
        )

        command_handler = self._routes.get(command_name)
        if command_handler is None:
            return await self.on_command_not_found(ctx, command_name)

        return await command_handler.execute(ctx)

    async def execute(
        self,
        ctx: CommandContext,
    ) -> str:
        """Implements support for nesting routers."""

        command_name = ctx.params[0]
        ctx.params = ctx.params[1:]

        if not await self.should_run(ctx):
            return await self.on_cannot_run(ctx)

        command_handler = self._routes.get(command_name)
        if command_handler is None:
            return await self.on_command_not_found(ctx, command_name)

        return await command_handler.execute(ctx)

    async def should_run(self, ctx: CommandContext) -> bool:
        """Overridable function for custom definitions of execution criteria."""

        return True

    # Events
    async def on_command_not_found(self, ctx: CommandContext, name: str) -> str:
        return f"Could not find a command with the name {name!r}!"

    async def on_invalid_format(self) -> str:
        return "Incorrect command format! Could not parse the given input."

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        """An event called when the custom `should_run` function returns false."""

        return "Insufficient conditions to run this command!"


class Command(CommandRoutable):
    """Inheritable command structure for implementing custom commands."""

    def __init__(
        self,
        name: str,
        description: str,
        required_privileges: UserPrivileges | None = None,
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
        """An event called when an unhandled exception occurs while executing
        the command."""

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
        """An event called when the user does not have the required privileges
        to run the command, defined in the `required_privileges` attribute."""

        return "You have insufficient privileges to run this command."

    # TODO: Provide more information.
    async def on_argument_fail(self, ctx: CommandContext) -> str:
        """An event called when parsing the command arguments into the
        required format fails, usually due to user mis-input."""

        return "Incorrect arguments provided!"

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        """An event called when the custom `should_run` function returns false."""

        return "Insufficient conditions to run this command!"

    async def execute(self, ctx: CommandContext) -> str:
        """Called by the command router to perform command checks and execution.
        Do not override this method."""

        # Modify params to remove the command name.
        ctx.params = ctx.params[1:]

        if not self.__has_privileges(ctx):
            return await self.on_privilege_fail(ctx)

        if not await self.should_run(ctx):
            return await self.on_cannot_run(ctx)

        try:
            params = await self._parse_params(ctx)
        except ValueError:
            return await self.on_argument_fail(ctx)

        try:
            result = await self.handle(ctx, *params)
            logger.info(
                "Successfully executed command!",
                extra={
                    "command_name": self.name,
                    "user_id": ctx.user.id,
                },
            )
            return result
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

    async def _parse_params(self, ctx: CommandContext) -> list[Any]:
        annotations = get_type_hints(self.handle)
        return await _cast_params(ctx, annotations)


class LevelCommand(Command):
    """A child class of `Command` with a default `should_run` implementation
    that only allows the command to be ran on levels."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_level

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        return "This command can only be ran on levels!"


class MessageCommand(Command):
    """A child class of `Command` with a default `should_run` implementation
    that only allows the command to be ran on messages."""

    async def should_run(self, ctx: CommandContext) -> bool:
        return ctx.is_message

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        return "This command can only be ran in user messages!"


class HandlerFunctionProtocol(Protocol):
    """A protocol for defining a command handler function."""

    async def __call__(self, ctx: CommandContext, *args: SupportedTypes) -> str:
        ...


class CommandFunction(Command):
    """A child class of `Command` that allows for defining an entire command
    in a single function. Used for simple commands that do not require
    a lot of boilerplate or custom functionality."""

    def __init__(
        self,
        name: str,
        description: str,
        handler: HandlerFunctionProtocol,
        required_privileges: UserPrivileges | None = None,
    ) -> None:
        super().__init__(name, description, required_privileges)
        self._handler = handler

    async def handle(self, ctx: CommandContext, *args: SupportedTypes) -> str:
        return await self._handler(ctx, *args)

    async def _parse_params(self, ctx: CommandContext) -> list[Any]:
        annotations = get_type_hints(self._handler)
        return await _cast_params(ctx, annotations)


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


def make_command(
    name: str | None = None,
    description: str | None = None,
    required_privileges: UserPrivileges | None = None,
) -> Callable[[HandlerFunctionProtocol], CommandFunction]:
    """A decorator for defining a command in a single function.
    Creates an instance of `CommandFunction` with the provided arguments,
    or tries to work them out from the function name and docstring."""

    def decorator(handler: HandlerFunctionProtocol) -> CommandFunction:
        command_name = name or handler.__name__  # type: ignore
        command_description = description or handler.__doc__ or ""

        return CommandFunction(
            command_name,
            command_description,
            handler,
            required_privileges,
        )

    return decorator
