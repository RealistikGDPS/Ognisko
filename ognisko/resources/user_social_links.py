from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, UniqueConstraint, Index
from sqlmodel.ext.asyncio.session import AsyncSession

from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class SocialLinkType(StrEnum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    DISCORD = "discord"


class UserSocialLinkModel(DatabaseModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    link_type: SocialLinkType
    link: str
    linked_at: datetime

    class Meta:
        constraints = [
            UniqueConstraint("user_id", "link_type")
        ]
        indexes = [
            Index("user_id")
        ]


class UserSocialLinkRepository:
    __slots__ = ("_sql",)

    def __init__(self, sql: AsyncSession) -> None:
        self._sql = sql


    async def from_id(self, id: int) -> UserSocialLinkModel | None:
        return await self._sql.get(UserSocialLinkModel, id)
