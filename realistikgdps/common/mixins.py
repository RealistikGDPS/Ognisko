from __future__ import annotations

from realistikgdps.common.protocols import HasIntValue


class IntEnumStringMixin:
    def __str__(self: HasIntValue) -> str:
        return str(self.value)
