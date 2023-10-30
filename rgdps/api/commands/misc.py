from __future__ import annotations

from rgdps.api.commands.framework import CommandContext
from rgdps.api.commands.framework import CommandRouter

router = CommandRouter("misc_root")


@router.register_function()
async def ping(ctx: CommandContext) -> str:
    return "Pong!"


@router.register_function()
async def echo(ctx: CommandContext, phrase: str) -> str:
    return f"And the forest echoed: {phrase!r}"
