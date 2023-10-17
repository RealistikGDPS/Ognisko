from __future__ import annotations

from rgdps.api.commands.framework import CommandContext
from rgdps.api.commands.framework import CommandRouter
from rgdps.api.commands.framework import make_command

router = CommandRouter("misc")


@router.register()
@make_command()
async def ping(ctx: CommandContext) -> str:
    return "Pong!"


@router.register()
@make_command()
async def echo(ctx: CommandContext, phrase: str) -> str:
    return f"And the forest echoed: {phrase!r}"
