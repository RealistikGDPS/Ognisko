from __future__ import annotations

from datetime import datetime

from rgdps.common.context import Context
from rgdps.models.message import Message


async def from_recipient_user_id(
    ctx: Context,
    recipient_user_id: int,
    include_deleted: bool = False,
) -> list[Message]:
    condition = ""
    if not include_deleted:
        condition = "AND NOT deleted"

    messages_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, subject, content, post_ts "
        f"FROM messages WHERE id = :recipient_user_id {condition} "
        "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
        {"recipient_user_id": recipient_user_id},
    )

    return [Message.from_mapping(message_db) for message_db in messages_db]


async def from_sender_user_id(
    ctx: Context,
    sender_user_id: int,
    include_deleted: bool = False,
) -> list[Message]:
    condition = ""
    if not include_deleted:
        condition = "AND NOT deleted"

    messages_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, subject, content, post_ts "
        f"FROM messages WHERE id = :sender_user_id {condition} "
        "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
        {"sender_user_id": sender_user_id},
    )

    return [Message.from_mapping(message_db) for message_db in messages_db]


async def create(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    recipient_username: str,
    subject: str,
    content: str,
) -> Message:
    message = Message(
        id=0,
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        recipient_username=recipient_username,
        subject=subject,
        content=content,
        post_ts=datetime.now(),
        seen_ts=None,
        deleted=False,
    )

    message.id = await ctx.mysql.execute(
        "INSERT INTO messages (sender_user_id, recipient_user_id, recipient_username, subject, content, post_ts) "
        "VALUES (:sender_user_id, :recipient_user_id, :recipient_username, :subject, :content, :post_ts)",
        message.as_dict(include_id=False),
    )

    return message
