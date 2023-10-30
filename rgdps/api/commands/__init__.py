from __future__ import annotations

from . import framework
from . import levels
from . import misc
from . import sync
from . import users
from rgdps.config import config

router = framework.CommandRouter("root")
router.merge(misc.router)
router.merge(levels.router)
router.merge(users.router)
router.merge(sync.router)


def is_command(entry: str) -> bool:
    return entry.startswith(config.srv_command_prefix)


def strip_prefix(entry: str) -> str:
    return entry.removeprefix(config.srv_command_prefix)
