from __future__ import annotations

from datetime import datetime
from datetime import timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel


class FriendRequestModel(DatabaseModel):
    __tablename__ = "friend_requests"

    sender_user_id = Column(Integer, nullable=False)
    recipient_user_id = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    posted_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    seen_at = Column(DateTime, nullable=True)


class FriendRequestRepository(BaseRepository[FriendRequestModel]):

    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, FriendRequestModel)

    async def from_target_and_reciptient(
        self,
        sender_user_id: int,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> FriendRequestModel | None:
        query = self._mysql.select(FriendRequestModel).where(
            FriendRequestModel.sender_user_id == sender_user_id,
            FriendRequestModel.recipient_user_id == recipient_user_id,
        )

        if not include_deleted:
            query = query.where(FriendRequestModel.deleted_at.is_(None))

        return await query.fetch_one()

    async def from_sender_user_id(
        self,
        sender_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        query = self._mysql.select(FriendRequestModel).where(
            FriendRequestModel.sender_user_id == sender_user_id,
        )
        if not include_deleted:
            query = query.where(FriendRequestModel.deleted_at.is_(None))

        return await query.fetch_all()

    async def from_recipient_user_id(
        self,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        query = self._mysql.select(FriendRequestModel).where(
            FriendRequestModel.recipient_user_id == recipient_user_id,
        )
        if not include_deleted:
            query = query.where(FriendRequestModel.deleted_at.is_(None))

        return await query.fetch_all()

    async def from_sender_user_id_paginated(
        self,
        sender_user_id: int,
        page: int,
        page_size: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        query = self._mysql.select(FriendRequestModel).where(
            FriendRequestModel.sender_user_id == sender_user_id,
        )
        if not include_deleted:
            query = query.where(FriendRequestModel.deleted_at.is_(None))
        return await query.paginate(page, page_size)

    async def from_recipient_user_id_paginated(
        self,
        recipient_user_id: int,
        page: int,
        page_size: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        query = self._mysql.select(FriendRequestModel).where(
            FriendRequestModel.recipient_user_id == recipient_user_id,
        )
        if not include_deleted:
            query = query.where(FriendRequestModel.deleted_at.is_(None))
        return await query.paginate(page, page_size)

    async def count_incoming_requests(self, user_id: int) -> int:
        return await self._mysql.fetch_val(
            "SELECT COUNT(*) FROM friend_requests WHERE "
            "recipient_user_id = :user_id AND deleted = 0",
            {"user_id": user_id},
        )

    async def count_outgoing_requests(self, user_id: int) -> int:
        return await self._mysql.fetch_val(
            "SELECT COUNT(*) FROM friend_requests WHERE "
            "sender_user_id = :user_id AND deleted = 0",
            {"user_id": user_id},
        )

    async def exists_from_target_and_sender(
        self,
        sender_user_id: int,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        return (
            await self._mysql.fetch_val(
                "SELECT 1 FROM friend_requests WHERE sender_user_id = :sender_user_id"
                " AND recipient_user_id = :recipient_user_id AND deleted IN :include_deleted",
                {
                    "sender_user_id": sender_user_id,
                    "recipient_user_id": recipient_user_id,
                    "include_deleted": (0, 1) if include_deleted else (0,),
                },
            )
        ) is not None
