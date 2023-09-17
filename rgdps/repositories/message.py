from __future__ import annotations

from datetime import datetime

from rgdps.common.context import Context
from rgdps.models.message import Message


async def from_recipient_user_id(
    ctx: Context,
    recipient_user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> list[Message]:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    messages_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, subject, content, post_ts, seen_ts "
        f"FROM messages WHERE recipient_user_id = :recipient_user_id {condition} "
        "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
        {
            "recipient_user_id": recipient_user_id,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [Message.from_mapping(message_db) for message_db in messages_db]


async def from_sender_user_id(
    ctx: Context,
    sender_user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> list[Message]:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    messages_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, subject, content, post_ts, seen_ts "
        f"FROM messages WHERE sender_user_id = :sender_user_id {condition} "
        "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
        {
            "sender_user_id": sender_user_id,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [Message.from_mapping(message_db) for message_db in messages_db]

async def from_recipient_user_id_count(
    ctx: Context,
    recipient_user_id: int,
    is_new: bool = False,
    include_deleted: bool = False, 
) -> int:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    if is_new:
        condition += " AND seen_ts IS NULL"

    messages_count = await ctx.mysql.fetch_val(
        f"SELECT COUNT(*) FROM messages WHERE recipient_user_id = :recipient_user_id {condition}",
        {
            "recipient_user_id": recipient_user_id,
        },
    )

    return messages_count


async def from_sender_user_id_count(
    ctx: Context,
    sender_user_id: int,
    is_new: bool = False,
    include_deleted: bool = False, 
) -> int:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    if is_new:
        condition += " AND seen_ts IS NULL"

    messages_count = await ctx.mysql.fetch_val(
        f"SELECT COUNT(*) FROM messages WHERE sender_user_id = :sender_user_id {condition}",
        {
            "sender_user_id": sender_user_id,
        },
    )

    return messages_count


async def create(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    subject: str,
    content: str,
) -> Message:
    message = Message(
        id=0,
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        subject=subject,
        content=content,
        post_ts=datetime.now(),
        seen_ts=None,
    )

    message.id = await ctx.mysql.execute(
        "INSERT INTO messages (sender_user_id, recipient_user_id, subject, content, post_ts, seen_ts) "
        "VALUES (:sender_user_id, :recipient_user_id, :subject, :content, :post_ts, :seen_ts)",
        message.as_dict(include_id=False),
    )

    return message
