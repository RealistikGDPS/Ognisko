from __future__ import annotations

from datetime import datetime
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from rgdps.common import modelling
from rgdps.common.context import Context
from rgdps.models.message import Message

ALL_FIELDS = modelling.get_model_fields(Message)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


async def from_id(
    ctx: Context,
    message_id: int,
    include_deleted: bool = False,
) -> Message | None:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    message_db = await ctx.mysql.fetch_one(
        f"SELECT {_ALL_FIELDS_COMMA} FROM messages WHERE id = :message_id {condition}",
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
        f"SELECT {_ALL_FIELDS_COMMA} FROM messages WHERE recipient_user_id = :recipient_user_id {condition} "
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
        f"SELECT {_ALL_FIELDS_COMMA} FROM messages WHERE sender_user_id = :sender_user_id {condition} "
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
        f"INSERT INTO messages ({_CUSTOMISABLE_FIELDS_COMMA}) "
        f"VALUES ({_CUSTOMISABLE_FIELDS_COLON})",
        message.as_dict(include_id=False),
    )

    return message


class _MessageUpdatePartial(TypedDict):
    seen_ts: NotRequired[datetime]
    sender_deleted: NotRequired[bool]
    recipient_deleted: NotRequired[bool]
    deleted: NotRequired[bool]


async def update_partial(
    ctx: Context,
    message_id: int,
    **kwargs: Unpack[_MessageUpdatePartial],
) -> Message | None:
    changed_fields = modelling.unpack_enum_types(kwargs)

    await ctx.mysql.execute(
        modelling.update_from_partial_dict("messages", message_id, changed_fields),
        changed_fields,
    )

    return await from_id(ctx, message_id, include_deleted=True)


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM messages")
