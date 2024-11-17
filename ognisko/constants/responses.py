from __future__ import annotations

from enum import IntEnum

from ognisko.common.mixins import IntEnumStringMixin


class GenericResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1


class RegisterResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1
    USERNAME_EXISTS = -2
    EMAIL_EXISTS = -3
    USERNAME_INVALID = -4
    PASSWORD_DISALLOWED = -5
    EMAIL_INVALID = -6
    PASSWORD_MISMATCH = -7
    PASSWORD_LENGTH_INVALID = -8
    USERNAME_LENGTH_INVALID = -9
    ACCOUNT_DISABLED = -12
    EMAIL_MISMATCH = -99


class LoginResponse(IntEnumStringMixin, IntEnum):
    SUCCESS = 1
    FAIL = -1
    PASSWORD_LENGTH_INVALID = -8
    USERNAME_LENGTH_INVALID = -9
    INVALID_CREDENTIALS = -11
    ACCOUNT_DISABLED = -12
