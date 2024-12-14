from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from ognisko.adapters import ImplementsMySQL
from ognisko.resources._common import BaseRepository
from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


# NOTE: message direction is relative to the user who is
# making the request.
class MessageDirection(StrEnum):
    SENT = "sent"
    RECEIVED = "received"


class UserMessageModel(DatabaseModel):
    __tablename__ = "messages"

    sender_user_id = Column(Integer, nullable=False)
    recipient_user_id = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    content = Column(String, nullable=False)
    posted_at = Column(DateTime, nullable=False)
    seen_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True, default=None)
    sender_deleted_at = Column(DateTime, nullable=True, default=None)


class MessageRepository(BaseRepository[UserMessageModel]):
    def __init__(self, mysql: ImplementsMySQL) -> None:
        super().__init__(mysql, UserMessageModel)

    async def from_recipient_user_id_paginated(
        self,
        recipient_user_id: int,
        page: int,
        page_size: int,
        *,
        include_deleted: bool = False,
    ) -> list[UserMessageModel]:
        query = self._mysql.select(UserMessageModel).where(
            UserMessageModel.recipient_user_id == recipient_user_id,
        )

        if not include_deleted:
            query = query.where(UserMessageModel.deleted_at.is_(None))

        return await query.paginate(page, page_size)

    async def from_sender_user_id_paginated(
        self,
        sender_user_id: int,
        page: int,
        page_size: int,
        *,
        include_deleted: bool = False,
    ) -> list[UserMessageModel]:
        query = self._mysql.select(UserMessageModel).where(
            UserMessageModel.sender_user_id == sender_user_id,
        )
        if not include_deleted:
            query = query.where(
                UserMessageModel.sender_deleted_at.is_(None),
            )

        return await query.paginate(page, page_size)

    async def count_from_recipient_user_id(
        self,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> int:
        condition = ""
        if not include_deleted:
            condition = "AND deleted = 0 AND recipient_deleted = 0"

        message_count = await self._mysql.fetch_val(
            f"SELECT COUNT(*) FROM messages WHERE recipient_user_id = :recipient_user_id {condition}",
            {
                "recipient_user_id": recipient_user_id,
            },
        )

        return message_count

    async def count_new_from_recipient_user_id(
        self,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> int:
        condition = ""
        if not include_deleted:
            condition = "AND deleted = 0 AND recipient_deleted = 0"

        message_count = await self._mysql.fetch_val(
            f"SELECT COUNT(*) FROM messages WHERE recipient_user_id = :recipient_user_id {condition} "
            "AND seen_ts IS NULL",
            {
                "recipient_user_id": recipient_user_id,
            },
        )

        return message_count

    async def count_from_sender_user_id(
        self,
        sender_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> int:
        condition = ""
        if not include_deleted:
            condition = "AND deleted = 0 AND sender_deleted = 0"

        message_count = await self._mysql.fetch_val(
            f"SELECT COUNT(*) FROM messages WHERE sender_user_id = :sender_user_id {condition}",
            {
                "sender_user_id": sender_user_id,
            },
        )

        return message_count

    async def count_new_from_sender_user_id(
        self,
        sender_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> int:
        condition = ""
        if not include_deleted:
            condition = "AND deleted = 0 AND sender_deleted = 0"

        message_count = await self._mysql.fetch_val(
            f"SELECT COUNT(*) FROM messages WHERE sender_user_id = :sender_user_id {condition} "
            "AND seen_ts IS NULL",
            {
                "sender_user_id": sender_user_id,
            },
        )

        return message_count
