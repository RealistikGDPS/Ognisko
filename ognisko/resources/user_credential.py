from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class CredentialVersion(StrEnum):
    PLAIN_BCRYPT = "PLAIN_BCRYPT"
    GJP2_BCRYPT = "GJP2_BCRYPT"  # 2.2 + GJP2


class UserCredentialModel(DatabaseModel):
    __tablename__ = "user_credentials"

    user_id = Column(Integer, nullable=False)
    version = Column(Enum(CredentialVersion), nullable=False)
    value = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_user_id_version", "user_id", "version", unique=True),
    )


class UserCredentialRepository(BaseRepository[UserCredentialModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, UserCredentialModel)

    async def from_user_id(
        self,
        user_id: int,
    ) -> list[UserCredentialModel]:
        query = self._mysql.select(UserCredentialModel).where(
            UserCredentialModel.user_id == user_id,
        )
        return await query.fetch_all()

    async def from_user_id_and_version(
        self,
        user_id: int,
        version: CredentialVersion,
    ) -> UserCredentialModel | None:
        return (
            await self._mysql.select(UserCredentialModel)
            .where(
                UserCredentialModel.user_id == user_id,
                UserCredentialModel.version == version,
            )
            .fetch_one()
        )
