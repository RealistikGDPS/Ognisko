from __future__ import annotations

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.message import Message


async def from_recipient_user_id(
    ctx: Context,
    recipient_user_id: int,
    include_deleted: bool = False,
) -> list[Message] | ServiceError:
    messages = await repositories.message.from_recipient_user_id(
        ctx,
        recipient_user_id=recipient_user_id,
        include_deleted=include_deleted,
    )
    return messages


async def from_sender_user_id(
    ctx: Context,
    sender_user_id: int,
    include_deleted: bool = False,
) -> list[Message] | ServiceError:
    messages = await repositories.message.from_sender_user_id(
        ctx,
        sender_user_id=sender_user_id,
        include_deleted=include_deleted,
    )
    return messages


async def create(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    subject: str,
    content: str,
) -> Message | ServiceError:
    recipient = await repositories.user.from_id(ctx, recipient_user_id)
    if recipient is None:
        return ServiceError.MESSAGES_INVALID_RECIPIENT

    message = await repositories.message.create(
        ctx,
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        recipient_username=recipient.username,
        subject=subject,
        content=content,
    )

    return message
