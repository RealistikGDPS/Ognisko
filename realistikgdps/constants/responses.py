from __future__ import annotations

from enum import IntEnum

from realistikgdps.mixins.enum_str import IntEnumStringMixin


class GenericResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1


class LoginResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1
    ACCOUNT_DISABLED = -12
