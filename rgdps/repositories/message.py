from __future__ import annotations

from datetime import datetime

from rgdps.common.context import Context
from rgdps.common.typing import is_set
from rgdps.common.typing import UNSET
from rgdps.common.typing import Unset
from rgdps.models.message import Message


async def from_id(
    ctx: Context,
    message_id: int,
    include_deleted: bool = False,
) -> Message | None:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    message_db = await ctx.mysql.fetch_one(
        "SELECT id, sender_user_id, recipient_user_id, subject, content, post_ts, "
        "seen_ts, sender_deleted, recipient_deleted, deleted "
        f"FROM messages WHERE id = :message_id {condition}",
        {"message_id": message_id},
    )

    if not message_db:
        return None

    return Message.from_mapping(message_db)


async def from_recipient_user_id(
    ctx: Context,
    recipient_user_id: int,
    page: int,
    page_size: int,
    include_deleted: bool = False,
) -> list[Message]:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0 AND recipient_deleted = 0"

    messages_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, subject, content, post_ts, "
        "seen_ts, sender_deleted, recipient_deleted, deleted "
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
        condition = "AND deleted = 0 AND sender_deleted = 0"

    messages_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, subject, content, post_ts, "
        "seen_ts, sender_deleted, recipient_deleted, deleted "
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
        condition = "AND deleted = 0 AND recipient_deleted = 0"

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
        condition = "AND deleted = 0 AND sender_deleted = 0"

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
    post_ts: datetime = datetime.now(),
    seen_ts: None | datetime = None,
) -> Message:
    message = Message(
        id=0,
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        subject=subject,
        content=content,
        post_ts=post_ts,
        seen_ts=seen_ts,
    )

    message.id = await ctx.mysql.execute(
        "INSERT INTO messages (sender_user_id, recipient_user_id, subject, content, post_ts, seen_ts) "
        "VALUES (:sender_user_id, :recipient_user_id, :subject, :content, :post_ts, :seen_ts)",
        message.as_dict(include_id=False),
    )

    return message


async def update_partial(
    ctx: Context,
    message_id: int,
    seen_ts: Unset | datetime = UNSET,
    sender_deleted: Unset | bool = UNSET,
    recipient_deleted: Unset | bool = UNSET,
    deleted: Unset | bool = UNSET,
) -> Message | None:
    changed_data = {}

    if is_set(seen_ts):
        changed_data["seen_ts"] = seen_ts
    if is_set(deleted):
        changed_data["deleted"] = deleted
    if is_set(sender_deleted):
        changed_data["sender_deleted"] = sender_deleted
    if is_set(recipient_deleted):
        changed_data["recipient_deleted"] = recipient_deleted

    if not changed_data:
        return None

    query = "UPDATE messages SET "
    query += ", ".join(f"{key} = :{key}" for key in changed_data.keys())
    query += " WHERE id = :id"

    changed_data["id"] = message_id

    await ctx.mysql.execute(query, changed_data)

    return await from_id(ctx, message_id, include_deleted=True)


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM messages")
