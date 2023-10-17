from __future__ import annotations

from . import framework
from . import misc
from rgdps.config import config

router = framework.CommandRouter("root")
router.merge(misc.router)


def is_command(entry: str) -> bool:
    return entry.startswith(config.srv_command_prefix)


def strip_prefix(entry: str) -> str:
    return entry.removeprefix(config.srv_command_prefix)
