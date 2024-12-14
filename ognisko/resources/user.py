from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class UserPrivacySetting(StrEnum):
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


class UserDisplayBadge(StrEnum):
    """Enum for determining whether a user should be displayed as a
    moderator, elder moderator, or neither.
    """

    MODERATOR = "moderator"
    ELDER_MODERATOR = "elder_moderator"


class UserModel(DatabaseModel):
    __tablename__ = "users"

    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)

    displayed_badge = Column(
        Enum(UserDisplayBadge),
        nullable=True,
    )
    message_privacy = Column(
        Enum(UserPrivacySetting),
        nullable=False,
        default=UserPrivacySetting.PUBLIC,
    )
    friend_privacy = Column(
        Enum(UserPrivacySetting),
        nullable=False,
        default=UserPrivacySetting.PUBLIC,
    )
    comment_privacy = Column(
        Enum(UserPrivacySetting),
        nullable=False,
        default=UserPrivacySetting.PUBLIC,
    )

    registered_at = Column(DateTime, default=datetime.now)
    comment_colour = Column(String(7), nullable=False)


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, UserModel)

    async def from_username(self, username: str) -> UserModel | None:
        return (
            await self._mysql.select(UserModel)
            .where(UserModel.username == username)
            .fetch_one()
        )

    async def from_email(self, email: str) -> UserModel | None:
        return (
            await self._mysql.select(UserModel)
            .where(UserModel.email == email)
            .fetch_one()
        )
