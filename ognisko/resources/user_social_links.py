from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class SocialLinkType(StrEnum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    DISCORD = "discord"


class UserSocialLinkModel(DatabaseModel):
    __tablename__ = "user_social_links"

    user_id = Column(Integer, nullable=False)
    link_type = Column(Enum(SocialLinkType), nullable=False)
    link = Column(String(255), nullable=False)

    __table_args__ = (
        Index("idx_user_id_link_type", "user_id", "link_type", unique=True),
        Index("idx_user_id", "user_id"),
    )


class UserSocialLinkRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: ImplementsMySQL) -> None:
        self._mysql = mysql

    async def from_id(self, id: int) -> UserSocialLinkModel | None:
        return (
            await self._mysql.select(UserSocialLinkModel)
            .where(UserSocialLinkModel.id == id)
            .fetch_one()
        )

    async def from_user_id(self, user_id: int) -> list[UserSocialLinkModel]:
        return (
            await self._mysql.select(UserSocialLinkModel)
            .where(UserSocialLinkModel.user_id == user_id)
            .fetch_all()
        )

    async def create(self, **kwargs) -> UserSocialLinkModel:
        link_id = (
            await self._mysql.insert(UserSocialLinkModel).values(**kwargs).execute()
        )
        return await self.from_id(link_id)

    async def delete_from_id(self, link_id: int) -> None:
        await self._mysql.delete(UserSocialLinkModel).where(
            UserSocialLinkModel.id == link_id,
        ).execute()

    async def from_user_id_and_type(
        self,
        user_id: int,
        link_type: SocialLinkType,
    ) -> UserSocialLinkModel | None:
        return (
            await self._mysql.select(UserSocialLinkModel)
            .where(
                UserSocialLinkModel.user_id == user_id,
                UserSocialLinkModel.link_type == link_type,
            )
            .fetch_one()
        )
