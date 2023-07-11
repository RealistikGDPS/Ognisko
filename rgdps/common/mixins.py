from __future__ import annotations

from rgdps.common.typing import HasIntValue


class IntEnumStringMixin:
    def __str__(self: HasIntValue) -> str:
        return str(self.value)
