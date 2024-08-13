from __future__ import annotations

from enum import Enum

from rgdps.utilities.typing import HasIntValue


class StrEnum(str, Enum):
    pass


def list_enum_values(l: list[HasIntValue]) -> list[int]:
    return [x.value for x in l]
