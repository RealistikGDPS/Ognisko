from __future__ import annotations

from enum import IntEnum


class FriendStatus(IntEnum):
    NONE = 0
    FRIEND = 1
    INCOMING_REQUEST = 3
    OUTGOING_REQUEST = 4
