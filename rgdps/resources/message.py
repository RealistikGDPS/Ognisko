from __future__ import annotations

from datetime import datetime
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from rgdps.adapters import AbstractMySQLService
from rgdps.common import modelling
from rgdps.resources._common import DatabaseModel
from rgdps.utilities.enum import StrEnum


class MessageDirection(StrEnum):
    # NOTE: message direction is relative to the user who is
    # making the request.
    SENT = "sent"
    RECEIVED = "received"


class Message(DatabaseModel):
    id: int
    sender_user_id: int
    recipient_user_id: int
    subject: str
    content: str
    post_ts: datetime
    seen_ts: datetime | None


class _MessageUpdatePartial(TypedDict):
    seen_ts: NotRequired[datetime]
    sender_deleted: NotRequired[bool]
    recipient_deleted: NotRequired[bool]
    deleted: NotRequired[bool]


class MessageRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: AbstractMySQLService) -> None:
        self._mysql = mysql

    async def from_id(self, message_id: int) -> Message | None:
        message_db = await self._mysql.fetch_one(
            "SELECT * FROM messages WHERE id = :message_id",
            {
                "message_id": message_id,
            },
        )

        if message_db is None:
            return None

        return Message(**message_db)

    async def from_recipient_user_id_paginated(
        self,
        recipient_user_id: int,
        page: int,
        page_size: int,
        include_deleted: bool = False,
    ) -> list[Message]:
        condition = ""
        if not include_deleted:
            condition = "AND deleted = 0 AND recipient_deleted = 0"

        messages_db = self._mysql.iterate(
            f"SELECT * FROM messages WHERE recipient_user_id = :recipient_user_id {condition} "
            "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
            {
                "recipient_user_id": recipient_user_id,
                "limit": page_size,
                "offset": page * page_size,
            },
        )

        return [Message(**message_db) async for message_db in messages_db]

    async def from_sender_user_id_paginated(
        self,
        sender_user_id: int,
        page: int,
        page_size: int,
        include_deleted: bool = False,
    ) -> list[Message]:
        condition = ""
        if not include_deleted:
            condition = "AND deleted = 0 AND sender_deleted = 0"

        messages_db = self._mysql.iterate(
            f"SELECT * FROM messages WHERE sender_user_id = :sender_user_id {condition} "
            "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
            {
                "sender_user_id": sender_user_id,
                "limit": page_size,
                "offset": page * page_size,
            },
        )

        return [Message(**message_db) async for message_db in messages_db]

    async def count_from_recipient_user_id(
        self,
        recipient_user_id: int,
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

    async def create(
        self,
        sender_user_id: int,
        recipient_user_id: int,
        subject: str,
        content: str,
    ) -> int:
        message_id = await self._mysql.execute(
            "INSERT INTO messages (sender_user_id, recipient_user_id, subject, content) "
            "VALUES (:sender_user_id, :recipient_user_id, :subject, :content)",
            {
                "sender_user_id": sender_user_id,
                "recipient_user_id": recipient_user_id,
                "subject": subject,
                "content": content,
            },
        )

        return message_id

    async def update_partial(
        self,
        message_id: int,
        **kwargs: Unpack[_MessageUpdatePartial],
    ) -> Message | None:
        changed_fields = modelling.unpack_enum_types(kwargs)

        await self._mysql.execute(
            modelling.update_from_partial_dict("messages", message_id, changed_fields),
            changed_fields,
        )
        return await self.from_id(message_id)

    async def count_all(self) -> int:
        return (await self._mysql.fetch_val("SELECT COUNT(*) FROM messages")) or 0
