from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Callable
from typing import get_args
from typing import get_origin
from typing import get_type_hints
from typing import Protocol
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

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
SupportedTypes = str | int | float | bool | Level | User | Enum
T = TypeVar("T")


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


def _unwrap_cast(cast: type[T]) -> type[T]:
    origin_type = get_origin(cast)
    origin_args = get_args(cast)

    # Handling for `T | None` types.
    if origin_type is Union and len(origin_args) == 2 and None in origin_args:
        return origin_args[1 - origin_args.index(None)]

    return cast


async def _resolve_from_type(ctx: CommandContext, value: str, cast: type[T]) -> T:
    cast = _unwrap_cast(cast)

    if cast in _CASTABLE:
        return cast(value)
    elif issubclass(cast, bool):
        return _bool_parse(value)
    elif issubclass(cast, Level):
        return await _level_by_ref(ctx, value)
    elif issubclass(cast, User):
        return await _user_by_ref(ctx, value)
    elif issubclass(cast, Enum):
        return cast(value)

    logger.error(
        "Command parser tried to parse an unsupported type!",
        extra={
            "value": value,
            "type": repr(cast),
        },
    )
    raise ValueError(
        f"A resolver for the defined type {cast!r} has not been implemented!",
    )


def _bool_parse(data: str) -> bool:
    data = data.lower()
    if data in ("true", "1", "t"):
        return True
    elif data in ("false", "0", "f"):
        return False

    raise ValueError(f"Could not parse {data!r} as a boolean (true/false) value!")


def _parse_params(param_str: str) -> list[str]:
    # TODO: maybe kwargs?
    if param_str.count('"') % 2 != 0:
        raise ValueError("Unclosed quotes in command parameters!")

    param_str = param_str.strip()
    if not param_str:
        raise ValueError("No command parameters provided!")

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
    defaults: tuple[Any],
) -> list[Any]:
    params = []

    required_len = len(annotations) - len(defaults)
    max_len = len(annotations)
    provided_len = len(ctx.params)
    if provided_len < required_len or provided_len > max_len:
        raise ValueError(
            "Invalid number of parameters provided! Expected between "
            f"{required_len} and {max_len}, got {provided_len}!",
        )

    for arg_type, value in zip(annotations.values(), ctx.params):
        params.append(await _resolve_from_type(ctx, value, arg_type))

    return params


def _get_command_types(func: HandlerFunctionProtocol) -> dict[str, Any]:
    annotations = get_type_hints(func)

    return {
        key: value
        for key, value in annotations.items()
        if value is not CommandContext and key != "return"
    }


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

    def register(self) -> Callable[[CommandRoutable], CommandRoutable]:
        """A decorator version of `register_command`."""

        def decorator(command: CommandRoutable) -> CommandRoutable:
            self.register_command(command)
            return command

        return decorator

    async def entrypoint(
        self,
        command: str,
        user: User,
        base_ctx: Context,
        level_id: int | None = None,
        target_user_id: int | None = None,
    ) -> str:
        """Defines an entrypoint for command execution. This method is
        supposed to be the first one called when executing a command."""

        try:
            parsed_params = _parse_params(command)
        except ValueError as e:
            return await self.on_invalid_format(e)

        command_name = parsed_params[0]

        # Resolve context details
        level = None
        if level_id is not None:
            level = await repositories.level.from_id(base_ctx, level_id)
            if level is None:
                logger.error(
                    "Failed to resolve the command level!",
                    extra={"level_id": level_id},
                )
                return await self.on_misc_error()

        target_user = None
        if target_user_id is not None:
            target_user = await repositories.user.from_id(base_ctx, target_user_id)
            if target_user is None:
                logger.error(
                    "Failed to resolve the command target user!",
                    extra={"target_user_id": target_user_id},
                )
                return await self.on_misc_error()

        ctx = CommandContext(
            user=user,
            level=level,
            target_user=target_user,
            params=parsed_params,
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

    async def on_invalid_format(self, exception: Exception) -> str:
        return (
            "Incorrect command format! Could not parse the given "
            f"input with error {exception}."
        )

    async def on_cannot_run(self, ctx: CommandContext) -> str:
        """An event called when the custom `should_run` function returns false."""

        return "Insufficient conditions to run this command!"

    async def on_misc_error(self) -> str:
        """An event called when an internal logic error occurs. Used for
        errors where the user does not need to know the specifics."""

        return "An internal error has occurred while executing this command!"


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

        if self.required_privileges:
            self.required_privileges |= UserPrivileges.COMMANDS_TRIGGER

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

    async def on_argument_fail(self, ctx: CommandContext, exception: Exception) -> str:
        """An event called when parsing the command arguments into the
        required format fails, usually due to user mis-input."""

        return "Matching the given command arguments has failed with error " + str(
            exception,
        )

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
        except ValueError as e:
            return await self.on_argument_fail(ctx, e)

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
        annotations = _get_command_types(self.handle)
        default_params = self.handle.__defaults__ or ()
        return await _cast_params(ctx, annotations, default_params)


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

    __name__: str
    __defaults__: tuple[Any, ...] | None

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
        annotations = _get_command_types(self._handler)
        default_params = self._handler.__defaults__ or ()
        return await _cast_params(ctx, annotations, default_params)


class UnparsedCommand(Command):
    """A child class of `Command` that bypasses the annotation-based
    command parsing and passes the raw string arguments to the command handler
    as a single string."""

    async def _parse_params(self, ctx: CommandContext) -> list[Any]:
        return [" ".join(ctx.params)]


def make_command(
    name: str | None = None,
    description: str | None = None,
    required_privileges: UserPrivileges | None = None,
) -> Callable[[HandlerFunctionProtocol], CommandFunction]:
    """A decorator for defining a command in a single function.
    Creates an instance of `CommandFunction` with the provided arguments,
    or tries to work them out from the function name and docstring."""

    def decorator(handler: HandlerFunctionProtocol) -> CommandFunction:
        command_name = name or handler.__name__
        command_description = description or handler.__doc__ or ""

        return CommandFunction(
            command_name,
            command_description,
            handler,
            required_privileges,
        )

    return decorator
