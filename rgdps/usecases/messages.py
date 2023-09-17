from __future__ import annotations

from typing import NamedTuple

from rgdps import repositories
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.models.message import Message
from rgdps.models.user import User

class MessageResponse(NamedTuple):
    message: Message
    user: User

class PaginatedMessagesResponse(NamedTuple):
    messages: list[MessageResponse]
    total: int

async def from_recipient_user_id(
    ctx: Context,
    recipient_user_id: int,
    page: int = 0,
    page_size: int = 50,
    include_deleted: bool = False,
) -> PaginatedMessagesResponse | ServiceError:
    messages = await repositories.message.from_recipient_user_id(
        ctx,
        recipient_user_id=recipient_user_id,
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
    )

    messages_resp = []
    for message in messages:
        user = await repositories.user.from_id(ctx, message.sender_user_id)

        if user is None:
            continue 

        messages_resp.append(
            MessageResponse(message=message, user=user)
        )

    messages_count = await repositories.message.from_recipient_user_id_count(
        ctx,
        recipient_user_id=recipient_user_id,
        include_deleted=include_deleted,
    )

    return PaginatedMessagesResponse(
        messages=messages_resp,
        total=messages_count,
    )


async def from_sender_user_id(
    ctx: Context,
    sender_user_id: int,
    page: int = 0,
    page_size: int = 50,
    include_deleted: bool = False,
) -> PaginatedMessagesResponse | ServiceError:
    messages = await repositories.message.from_sender_user_id(
        ctx,
        sender_user_id=sender_user_id,
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
    )

    messages_resp = []
    for message in messages:
        user = await repositories.user.from_id(ctx, message.recipient_user_id)

        if user is None:
            continue 

        messages_resp.append(
            MessageResponse(message=message, user=user)
        )

    messages_count = await repositories.message.from_sender_user_id_count(
        ctx,
        sender_user_id=sender_user_id,
        include_deleted=include_deleted,
    )

    return PaginatedMessagesResponse(
        messages=messages_resp,
        total=messages_count,
    )


async def create(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    subject: str,
    content: str,
) -> Message | ServiceError:

    if recipient_user_id == sender_user_id:
        return ServiceError.MESSAGES_INVALID_RECIPIENT_ID

    recipient = await repositories.user.from_id(ctx, recipient_user_id)
    if recipient is None:
        return ServiceError.MESSAGES_INVALID_RECIPIENT

    message = await repositories.message.create(
        ctx,
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        subject=subject,
        content=content,
    )

    return message
