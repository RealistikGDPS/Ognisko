import base64

from fastapi import Depends
from fastapi import Form

from rgdps.api import responses
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common import gd_obj
from rgdps.common.validators import Base64String
from rgdps.constants.errors import ServiceError
from rgdps.models.message import MessageDirection
from rgdps.models.user import User
from rgdps.usecases import messages


async def message_post(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    recipient_user_id: int = Form(..., alias="toAccountID"),
    subject: Base64String = Form(...),
    content: Base64String = Form(..., alias="body"),
):
    await messages.create(
        ctx,
        sender_user_id=user.id,
        recipient_user_id=recipient_user_id,
        subject=subject,
        content=content,
    )

    return responses.success()


async def messages_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
):
    others_messages = await messages.from_recipient_user_id(
        ctx,
        recipient_user_id=user.id,
        include_deleted=False,
    )
    if isinstance(others_messages, ServiceError):
        return responses.fail()

    our_messages = await messages.from_sender_user_id(
        ctx,
        sender_user_id=user.id,
        include_deleted=False,
    )
    if isinstance(our_messages, ServiceError):
        return responses.fail()

    return (
        "|".join(
            gd_obj.dumps(
                gd_obj.create_message(
                    message,
                    message_direction=MessageDirection.SENT,
                ),
            )
            for message in our_messages
        )
        + "|"
        + "|".join(
            gd_obj.dumps(
                gd_obj.create_message(
                    message,
                    message_direction=MessageDirection.RECEIVED,
                ),
            )
            for message in others_messages
        )
    )
