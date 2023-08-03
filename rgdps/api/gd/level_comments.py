from __future__ import annotations

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
from rgdps.models.user import User
from rgdps.usecases import level_comments

PAGE_SIZE = 10


async def create_comment_post(
    ctx: HTTPContext = Depends(),
    user: User = Depends(
        authenticate_dependency(required_privileges=UserPrivileges.COMMENTS_POST),
    ),
    level_id: int = Form(..., alias="levelID"),
    content: Base64String = Form(..., alias="comment"),
    percent: int = Form(default=0),
):
    comment = await level_comments.create(
        ctx,
        user_id=user.id,
        level_id=level_id,
        content=content,
        percent=percent,
    )

    if isinstance(comment, ServiceError):
        logger.info(f"Failed to add comment with error {comment!r}")
        return responses.fail()

    logger.info(f"Successfully added comment {comment}!")
    return str(comment.id)


async def level_comments_get(
    ctx: HTTPContext = Depends(),
    level_id: int = Form(..., alias="levelID"),
    page: int = Form(...),
):
    result = await level_comments.get_level(
        ctx,
        level_id,
        page,
        PAGE_SIZE,
    )

    if isinstance(result, ServiceError):
        logger.info(f"Failed to load comments with error {result!r}")
        return responses.fail()

    response = "|".join(
        gd_obj.dumps(
            [
                gd_obj.create_level_comment(comment.comment, comment.user),
                gd_obj.create_level_comment_author_string(comment.user),
            ],
            sep="~",
        )
        for comment in result.comments
    )
    response += "#" + gd_obj.create_pagination_info(result.total, page, PAGE_SIZE)

    logger.info(response)

    logger.info(f"Successfully viewed comments for level ID {level_id}.")
    return response
