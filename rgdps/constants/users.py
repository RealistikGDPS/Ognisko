from __future__ import annotations

from enum import IntEnum
from enum import IntFlag

from rgdps.common.mixins import IntEnumStringMixin


# 128-bit integer
class UserPrivileges(IntFlag):
    USER_AUTHENTICATE = 1 << 0
    USER_PROFILE_PUBLIC = 1 << 1
    USER_STAR_LEADERBOARD_PUBLIC = 1 << 2
    USER_CREATOR_LEADERBOARD_PUBLIC = 1 << 3
    USER_DISPLAY_ELDER_BADGE = 1 << 4
    USER_DISPLAY_MOD_BADGE = 1 << 5
    USER_REQUEST_ELDER = 1 << 6
    USER_REQUEST_MODERATOR = 1 << 7
    USER_CREATE_USER_COMMENTS = 1 << 8
    USER_MODIFY_PRIVILEGES = 1 << 9
    USER_CHANGE_CREDENTIALS_OWN = 1 << 10
    USER_CHANGE_CREDENTIALS_OTHER = 1 << 11

    LEVEL_UPLOAD = 1 << 12
    LEVEL_UPDATE = 1 << 13
    LEVEL_DELETE_OWN = 1 << 14
    LEVEL_DELETE_OTHER = 1 << 15
    LEVEL_RATE_STARS = 1 << 16
    LEVEL_ENQUEUE_DAILY = 1 << 17
    LEVEL_ENQUEUE_WEEKLY = 1 << 18
    LEVEL_MODIFY_VISIBILITY = 1 << 19
    LEVEL_RENAME_OTHER = 1 << 20
    LEVEL_MARK_MAGIC = 1 << 21
    LEVEL_MARK_AWARDED = 1 << 22

    COMMENTS_POST = 1 << 23
    COMMENTS_DELETE_OWN = 1 << 24
    COMMENTS_DELETE_OTHER = 1 << 25
    COMMANDS_TRIGGER = 1 << 26
    COMMENTS_BYPASS_SPAM_FILTER = 1 << 27

    MESSAGES_SEND = 1 << 28
    MESSAGES_DELETE_OWN = 1 << 29

    FRIEND_REQUESTS_SEND = 1 << 30
    FRIEND_REQUESTS_ACCEPT = 1 << 31
    FRIEND_REQUESTS_DELETE_OWN = 1 << 32

    MAP_PACK_CREATE = 1 << 33

    GAUNTLET_CREATE = 1 << 34

    SERVER_RESYNC_SEARCH = 1 << 35
    SERVER_STOP = 1 << 36

    USER_VIEW_PRIVATE_PROFILE = 1 << 37
    COMMENTS_LIKE = 1 << 38

    def as_bytes(self) -> bytes:
        return self.to_bytes(16, "little", signed=False)

    @staticmethod
    def from_bytes(b: bytes) -> UserPrivileges:
        return UserPrivileges(int.from_bytes(b, "little", signed=False))


class UserPrivacySetting(IntEnum):
    PUBLIC = 0
    FRIENDS = 1
    PRIVATE = 2


class UserRelationshipType(IntEnum):
    FRIEND = 0
    BLOCKED = 1


class UserPrivilegeLevel(IntEnumStringMixin, IntEnum):
    """Enum for determining whether a user should be displayed as a
    moderator, elder moderator, or neither.
    """

    NONE = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2


STAR_PRIVILEGES = (
    UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC | UserPrivileges.USER_PROFILE_PUBLIC
)

CREATOR_PRIVILEGES = (
    UserPrivileges.USER_CREATOR_LEADERBOARD_PUBLIC | UserPrivileges.USER_PROFILE_PUBLIC
)

DEFAULT_PRIVILEGES = (
    UserPrivileges.USER_AUTHENTICATE
    | UserPrivileges.USER_PROFILE_PUBLIC
    | UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC
    | UserPrivileges.USER_CREATOR_LEADERBOARD_PUBLIC
    | UserPrivileges.USER_CREATE_USER_COMMENTS
    | UserPrivileges.USER_CHANGE_CREDENTIALS_OWN
    | UserPrivileges.LEVEL_UPLOAD
    | UserPrivileges.LEVEL_UPDATE
    | UserPrivileges.LEVEL_DELETE_OWN
    | UserPrivileges.COMMENTS_POST
    | UserPrivileges.COMMENTS_DELETE_OWN
    | UserPrivileges.COMMANDS_TRIGGER
    | UserPrivileges.MESSAGES_SEND
    | UserPrivileges.MESSAGES_DELETE_OWN
    | UserPrivileges.FRIEND_REQUESTS_SEND
    | UserPrivileges.FRIEND_REQUESTS_ACCEPT
    | UserPrivileges.FRIEND_REQUESTS_DELETE_OWN
    | UserPrivileges.COMMENTS_LIKE
)
