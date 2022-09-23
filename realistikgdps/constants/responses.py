from __future__ import annotations

from enum import IntEnum

from realistikgdps.mixins.enum_str import IntEnumStringMixin


class GenericResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1


class RegisterResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1
    USERNAME_EXISTS = -2
    EMAIL_EXISTS = -3
    PASSWORD_DISALLOWED = -5
    EMAIL_INVALID = -6
    PASSWORD_LENGTH_INVALID = -8
    USERNAME_LENGTH_INVALID = -9
    ACCOUNT_DISABLED = -12


class LoginResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1
    ACCOUNT_DISABLED = -12
