from __future__ import annotations

from . import framework
from . import levels
from . import misc
from . import schedule
from . import sync
from . import users

from rgdps import settings

router = framework.CommandRouter("root")
router.merge(misc.router)
router.merge(levels.router)
router.merge(users.router)
router.merge(sync.router)
router.merge(schedule.router)


def is_command(entry: str) -> bool:
    return entry.startswith(settings.SERVER_COMMAND_PREFIX)


def strip_prefix(entry: str) -> str:
    return entry.removeprefix(settings.SERVER_COMMAND_PREFIX)
