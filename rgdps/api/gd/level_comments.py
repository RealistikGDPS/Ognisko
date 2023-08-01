from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.api import responses
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common.validators import Base64String
from rgdps.constants.errors import ServiceError
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User
from rgdps.usecases import level_comments


async def create_comment_post(
    ctx: HTTPContext = Depends(),
    user: User = Depends(
        authenticate_dependency(required_privileges=UserPrivileges.COMMENTS_POST),
    ),
    level_id: int = Form(..., alias="levelID"),
    content: Base64String = Form(..., alias="comment"),
):
    comment = await level_comments.create(
        ctx,
        user_id=user.id,
        level_id=level_id,
        content=content,
    )

    if isinstance(comment, ServiceError):
        logger.info(f"Failed to add comment with error {comment!r}")
        return responses.fail()

    logger.info(f"Successfully added comment {comment}!")
    return str(comment.id)
