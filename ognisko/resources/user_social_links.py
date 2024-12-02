from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import delete

from ognisko.utilities.enum import StrEnum
from ognisko.resources._common import DatabaseModel


class SocialLinkType(StrEnum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    DISCORD = "discord"


class UserSocialLinkBase(DatabaseModel):
    user_id: int
    link_type: SocialLinkType
    link: str


class UserSocialLinkModel(UserSocialLinkBase, table=True):
    __tablename__: str = "user_social_links" # str is required or else pylance will be angerey

    id: int = Field(primary_key=True)
    linked_at: datetime = Field(default_factory=datetime.now)

    __table_args__ = (
        UniqueConstraint("user_id", "link_type"),
        Index("user_id"),
    )


class UserSocialLinkCreateModel(UserSocialLinkBase):
    pass


class UserSocialLinkUpdateModel(SQLModel):
    link: str
    linked_at: datetime = Field(default_factory=datetime.now)


class UserSocialLinkRepository:
    __slots__ = ("_session",)
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def from_id(self, id: int) -> UserSocialLinkModel | None:
        return await self._session.get(UserSocialLinkModel, id)

    async def from_user_id(self, user_id: int) -> Sequence[UserSocialLinkModel]:
        result = await self._session.exec(
            select(UserSocialLinkModel).where(UserSocialLinkModel.user_id == user_id)
        )
        return result.all()
    
    async def create(self, data: UserSocialLinkCreateModel) -> UserSocialLinkModel:
        link = UserSocialLinkModel(**data.model_dump())
        self._session.add(link)

        return link
    

    async def delete_from_id(self, link_id: int) -> None:
        await self._session.exec(
            delete(UserSocialLinkModel).where(UserSocialLinkModel.id == link_id)
        )


    async def from_user_id_and_type(self, user_id: int, link_type: SocialLinkType) -> UserSocialLinkModel | None:
        query = await self._session.exec(
            select(UserSocialLinkModel).where(
                (UserSocialLinkModel.user_id == user_id) & (UserSocialLinkModel.link_type == link_type)
            )
        )
        return query.first()
