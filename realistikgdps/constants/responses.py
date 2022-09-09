from __future__ import annotations

from enum import IntEnum

from realistikgdps.mixins.enum_str import IntEnumStringMixin


class GenericResponse(IntEnum, IntEnumStringMixin):
    SUCCESS = 1
    FAIL = -1
