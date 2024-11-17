from __future__ import annotations

from enum import IntEnum


class CredentialVersion(IntEnum):
    PLAIN_BCRYPT = 1
    GJP2_BCRYPT = 2  # 2.2 + GJP2
