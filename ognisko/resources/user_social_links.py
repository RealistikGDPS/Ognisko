from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
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


class UserSocialLinkRepository(BaseRepository[UserSocialLinkModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, UserSocialLinkModel)

    async def from_user_id(self, user_id: int) -> list[UserSocialLinkModel]:
        return (
            await self._mysql.select(UserSocialLinkModel)
            .where(UserSocialLinkModel.user_id == user_id)
            .fetch_all()
        )

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
