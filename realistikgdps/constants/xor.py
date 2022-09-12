from __future__ import annotations

from enum import Enum

# TODO: This shouldn't probably be a strenum since we use literally 0 of its
# features.
class XorKeys(str, Enum):
    LEVEL_PASSWORD = "26364"
    MESSAGE = "14251"
    GJP = "37526"
    QUESTS = "19847"
    CHESTS = "59182"
