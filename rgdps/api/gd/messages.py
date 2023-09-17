import base64

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.api import responses
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common import gd_obj
from rgdps.common.validators import Base64String
from rgdps.constants.errors import ServiceError
from rgdps.constants.users import UserPrivileges
from rgdps.models.message import MessageDirection
from rgdps.models.user import User
from rgdps.usecases import messages

PAGE_SIZE = 10


async def message_post(
    ctx: HTTPContext = Depends(),
    user: User = Depends(
        authenticate_dependency(
            required_privileges=UserPrivileges.MESSAGES_SEND,
        ),
    ),
    recipient_user_id: int = Form(..., alias="toAccountID"),
    subject: Base64String = Form(...),
    content: str = Form(..., alias="body"),
):
    content_decoded = gd_obj.decrypt_message_content_string(content)

    message = await messages.create(
        ctx,
        sender_user_id=user.id,
        recipient_user_id=recipient_user_id,
        subject=subject,
        content=content_decoded,
    )

    if isinstance(message, ServiceError):
        logger.info(
            f"{user} failed to send message to ID {recipient_user_id} with error {message!r}.",
        )
        return responses.fail()

    logger.info(f"{user} successfully sent message to ID {recipient_user_id}.")
    return responses.success()


async def messages_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    page: int = Form(0, alias="page"),
    is_sender_user_id: bool = Form(0, alias="getSent"),
):

    if is_sender_user_id:
        message_direction = MessageDirection.SENT
        result = await messages.from_sender_user_id(
            ctx,
            sender_user_id=user.id,
            page=page,
            page_size=PAGE_SIZE,
            include_deleted=False,
        )
    else:
        message_direction = MessageDirection.RECEIVED
        result = await messages.from_recipient_user_id(
            ctx,
            recipient_user_id=user.id,
            page=page,
            page_size=PAGE_SIZE,
            include_deleted=False,
        )

    if isinstance(result, ServiceError):
        logger.info(f"{user} failed to view messages list with error {result!r}.")
        return responses.fail()

    if not result.messages:
        return responses.code(-2)

    response = "|".join(
        gd_obj.dumps(
            gd_obj.create_message(
                message.message,
                message.user,
                message_direction=message_direction,
            ),
        )
        for message in result.messages
    )
    response += "#" + gd_obj.create_pagination_info(result.total, page, PAGE_SIZE)

    if not is_sender_user_id:
        for message in result.messages:
            await messages.mark_message_as_seen(ctx, user, message.message.id)

    logger.info(f"{user} successfully viewed messages list.")
    return response


# XXX: Untested because client doesn't seem to use this endpoint anymore.
# Added for completion.
async def message_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    message_id: int = Form(..., alias="messageID"),
):
    result = await messages.from_id(ctx, user, message_id=message_id)

    if isinstance(result, ServiceError):
        logger.info(f"{user} failed to view message with error {result!r}.")
        return responses.fail()

    await messages.mark_message_as_seen(ctx, user, result.message.id)

    logger.info(f"{user} successfully viewed message.")
    return gd_obj.dumps(
        gd_obj.create_message(
            result.message,
            result.user,
            message_direction=MessageDirection.RECEIVED,
        ),
    )


async def message_delete(
    ctx: HTTPContext = Depends(),
    user: User = Depends(
        authenticate_dependency(
            required_privileges=UserPrivileges.MESSAGES_DELETE_OWN,
        ),
    ),
    message_id: int = Form(0, alias="messageID"),
    message_id_list: str | None = Form(None, alias="messages"),
):
    if message_id_list:
        messages_list = [int(message) for message in message_id_list.split(",")]
    else:
        messages_list = [message_id]

    for message in messages_list:
        await messages.delete_by_user(ctx, user, message_id=message)

    logger.info(f"{user} successfully deleted message(s).")
    return responses.success()
