from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseModelNoId
from ognisko.utilities.enum import StrEnum


class UserPrivileges(StrEnum):
    # User related privileges
    USER_AUTHENTICATE = "user.authenticate"
    USER_PROFILE_PUBLIC = "user.profile_public"
    USER_STAR_LEADERBOARD_PUBLIC = "user.star_leaderboard_public"
    USER_CREATOR_LEADERBOARD_PUBLIC = "user.creator_leaderboard_public"
    USER_DISPLAY_ELDER_BADGE = "user.display_elder_badge"
    USER_DISPLAY_MOD_BADGE = "user.display_mod_badge"
    USER_REQUEST_ELDER = "user.request_elder"
    USER_REQUEST_MODERATOR = "user.request_moderator"
    USER_CREATE_USER_COMMENTS = "user.create_user_comments"
    USER_MODIFY_PRIVILEGES = "user.modify_privileges"
    USER_CHANGE_CREDENTIALS_OWN = "user.change_credentials_own"
    USER_CHANGE_CREDENTIALS_OTHER = "user.change_credentials_other"
    USER_VIEW_PRIVATE_PROFILE = "user.view_private_profile"

    # Level related privileges
    LEVEL_UPLOAD = "level.upload"
    LEVEL_UPDATE = "level.update"
    LEVEL_DELETE_OWN = "level.delete_own"
    LEVEL_DELETE_OTHER = "level.delete_other"
    LEVEL_RATE_STARS = "level.rate_stars"
    LEVEL_ENQUEUE_DAILY = "level.enqueue_daily"
    LEVEL_ENQUEUE_WEEKLY = "level.enqueue_weekly"
    LEVEL_MODIFY_VISIBILITY = "level.modify_visibility"
    LEVEL_RENAME_OTHER = "level.rename_other"
    LEVEL_MARK_MAGIC = "level.mark_magic"
    LEVEL_MARK_AWARDED = "level.mark_awarded"
    LEVEL_CHANGE_DESCRIPTION_OTHER = "level.change_description_other"
    LEVEL_MOVE_USER = "level.move_user"

    # Comments related privileges
    COMMENTS_POST = "comments.post"
    COMMENTS_DELETE_OWN = "comments.delete_own"
    COMMENTS_DELETE_OTHER = "comments.delete_other"
    COMMENTS_BYPASS_SPAM_FILTER = "comments.bypass_spam_filter"
    COMMENTS_LIKE = "comments.like"

    # Commands related privileges
    COMMANDS_TRIGGER = "commands.trigger"

    # Messages related privileges
    MESSAGES_SEND = "messages.send"
    MESSAGES_DELETE_OWN = "messages.delete_own"

    # Friend requests related privileges
    FRIEND_REQUESTS_SEND = "friend_requests.send"
    FRIEND_REQUESTS_ACCEPT = "friend_requests.accept"
    FRIEND_REQUESTS_DELETE_OWN = "friend_requests.delete_own"

    # Map pack related privileges
    MAP_PACK_CREATE = "map_pack.create"

    # Gauntlet related privileges
    GAUNTLET_CREATE = "gauntlet.create"

    # Server related privileges
    SERVER_RESYNC_SEARCH = "server.resync_search"
    SERVER_STOP = "server.stop"
    SERVER_RESYNC_LEADERBOARDS = "server.resync_leaderboards"


STAR_PRIVILEGES = [
    UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC,
    UserPrivileges.USER_PROFILE_PUBLIC,
]
"""A set of privileges required for a user to appear on the star leaderboards."""

CREATOR_PRIVILEGES = [
    UserPrivileges.USER_CREATOR_LEADERBOARD_PUBLIC,
    UserPrivileges.USER_PROFILE_PUBLIC,
]
"""A set of privileges required for a user to appear on the creator leaderboards."""

DEFAULT_PRIVILEGES = [
    UserPrivileges.USER_AUTHENTICATE,
    UserPrivileges.USER_PROFILE_PUBLIC,
    UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC,
    UserPrivileges.USER_CREATOR_LEADERBOARD_PUBLIC,
    UserPrivileges.USER_CREATE_USER_COMMENTS,
    UserPrivileges.USER_CHANGE_CREDENTIALS_OWN,
    UserPrivileges.LEVEL_UPLOAD,
    UserPrivileges.LEVEL_UPDATE,
    UserPrivileges.LEVEL_DELETE_OWN,
    UserPrivileges.COMMENTS_POST,
    UserPrivileges.COMMENTS_DELETE_OWN,
    UserPrivileges.COMMANDS_TRIGGER,
    UserPrivileges.MESSAGES_SEND,
    UserPrivileges.MESSAGES_DELETE_OWN,
    UserPrivileges.FRIEND_REQUESTS_SEND,
    UserPrivileges.FRIEND_REQUESTS_ACCEPT,
    UserPrivileges.FRIEND_REQUESTS_DELETE_OWN,
    UserPrivileges.COMMENTS_LIKE,
]
"""A set of default privileges to be assigned to users upon registration."""


class UserPrivilegeAssignModel(BaseModelNoId):
    __tablename__ = "user_privilege_assign"

    user_id = Column(Integer, nullable=False)
    privilege = Column(Enum(UserPrivileges), nullable=False)


# We don't use base repository to simplify access to privileges
class UserPrivilegeRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: ImplementsMySQL) -> None:
        self._mysql = mysql

    async def from_user_id(self, user_id: int) -> list[UserPrivileges]:
        query = self._mysql.select(UserPrivilegeAssignModel).where(
            UserPrivilegeAssignModel.user_id == user_id,
        )
        return [UserPrivileges(row.privilege) async for row in query.iterate()]

    async def assign(self, user_id: int, privilege: UserPrivileges) -> None:
        await self._mysql.insert(UserPrivilegeAssignModel).values(
            user_id=user_id,
            privilege=privilege.value,
        ).execute()

    async def revoke(self, user_id: int, privilege: UserPrivileges) -> None:
        await self._mysql.delete(UserPrivilegeAssignModel).where(
            UserPrivilegeAssignModel.user_id == user_id,
            UserPrivilegeAssignModel.privilege == privilege.value,
        ).execute()

    async def assign_many(self, user_id: int, *privileges: UserPrivileges) -> None:
        # TODO: Implement a bulk insert method
        for privilege in privileges:
            await self.assign(user_id, privilege)

    async def has_privilege(self, user_id: int, privilege: UserPrivileges) -> bool:
        return (
            await self._mysql.select(UserPrivilegeAssignModel)
            .where(
                UserPrivilegeAssignModel.user_id == user_id,
                UserPrivilegeAssignModel.privilege == privilege.value,
            )
            .fetch_one()
            is not None
        )
