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

PAGE_SIZE = 50

async def message_post(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
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

    # TODO: LOGS!!
    if isinstance(message, ServiceError):
        return responses.fail()

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

    return response
