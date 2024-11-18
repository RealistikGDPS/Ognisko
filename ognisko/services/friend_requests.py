from __future__ import annotations

from datetime import datetime
from typing import NamedTuple

from ognisko.resources import Context
from ognisko.resources import FriendRequest
from ognisko.resources import User
from ognisko.resources import UserRelationshipType
from ognisko.services._common import ServiceError


class FriendRequestResponse(NamedTuple):
    request: FriendRequest
    user: User


class PaginatedFriendRequestResponse(NamedTuple):
    requests: list[FriendRequestResponse]
    total: int


async def get_user(
    ctx: Context,
    user_id: int,
    page: int = 0,
    page_size: int = 10,
    is_sender_user_id: bool = False,
) -> PaginatedFriendRequestResponse | ServiceError:
    if is_sender_user_id:
        requests = await ctx.friend_requests.from_sender_user_id_paginated(
            user_id,
            page,
            page_size,
            include_deleted=False,
        )
    else:
        requests = await ctx.friend_requests.from_recipient_user_id_paginated(
            user_id,
            page,
            page_size,
            include_deleted=False,
        )

    users = await ctx.users.multiple_from_id(
        # Swap the sender and recipient according to the from_sender_id flag
        [
            request.recipient_user_id if is_sender_user_id else request.sender_user_id
            for request in requests
        ],
    )
    friend_request_responses = [
        FriendRequestResponse(request, user) for request, user in zip(requests, users)
    ]

    if is_sender_user_id:
        friend_request_count = await ctx.friend_requests.count_outgoing_requests(
            user_id,
        )
    else:
        friend_request_count = await ctx.friend_requests.count_incoming_requests(
            user_id,
        )

    return PaginatedFriendRequestResponse(
        friend_request_responses,
        friend_request_count,
    )


async def mark_as_seen(
    ctx: Context,
    user_id: int,
    request_id: int,
) -> FriendRequest | ServiceError:
    request = await ctx.friend_requests.from_id(request_id)

    if request is None:
        return ServiceError.FRIEND_REQUEST_NOT_FOUND

    # This is only triggered by recipient.
    if request.recipient_user_id != user_id:
        return ServiceError.FRIEND_REQUEST_INVALID_OWNER

    request = await ctx.friend_requests.update_partial(
        request_id,
        seen_ts=datetime.now(),
    )

    if request is None:
        return ServiceError.FRIEND_REQUEST_NOT_FOUND

    return request


async def accept(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    request_id: int,
) -> ServiceError | None:
    request = await ctx.friend_requests.from_id(request_id)

    if request is None:
        return ServiceError.FRIEND_REQUEST_NOT_FOUND

    if sender_user_id == recipient_user_id:
        return ServiceError.FRIEND_REQUEST_INVALID_TARGET_ID

    if (
        request.sender_user_id != sender_user_id
        or request.recipient_user_id != recipient_user_id
    ):
        return ServiceError.FRIEND_REQUEST_INVALID_OWNER

    request = await ctx.friend_requests.update_partial(
        request.id,
        deleted=True,
    )

    if request is None:
        return ServiceError.FRIEND_REQUEST_NOT_FOUND

    # Create 2 records so it's a mutual friend relationship
    await ctx.user_relationships.create(
        sender_user_id,
        recipient_user_id,
        UserRelationshipType.FRIEND,
    )
    await ctx.user_relationships.create(
        recipient_user_id,
        sender_user_id,
        UserRelationshipType.FRIEND,
    )


async def create(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    message: str,
) -> FriendRequest | ServiceError:
    if sender_user_id == recipient_user_id:
        return ServiceError.FRIEND_REQUEST_INVALID_TARGET_ID

    exists = await ctx.friend_requests.exists_from_target_and_sender(
        sender_user_id,
        recipient_user_id,
    )

    if exists:
        return ServiceError.FRIEND_REQUEST_EXISTS

    request = await ctx.friend_requests.create(
        sender_user_id,
        recipient_user_id,
        message,
    )
    return request


async def delete(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
) -> FriendRequest | ServiceError:
    request = await ctx.friend_requests.from_target_and_reciptient(
        sender_user_id,
        recipient_user_id,
    )

    if request is None:
        return ServiceError.FRIEND_REQUEST_NOT_FOUND

    if (
        request.sender_user_id != sender_user_id
        or request.recipient_user_id != recipient_user_id
    ):
        return ServiceError.FRIEND_REQUEST_INVALID_OWNER

    request = await ctx.friend_requests.update_partial(
        request.id,
        deleted=True,
    )

    if request is None:
        return ServiceError.FRIEND_REQUEST_NOT_FOUND

    return request


# TODO: Return serviceerror
async def delete_multiple(
    ctx: Context,
    user_id: int,
    accounts_list: list[int],
    is_sender_user_id: bool = False,
) -> None:
    for account_id in accounts_list:
        if is_sender_user_id:
            sender_user_id = user_id
            recipient_user_id = account_id
        else:
            sender_user_id = account_id
            recipient_user_id = user_id

        request = await ctx.friend_requests.from_target_and_reciptient(
            sender_user_id,
            recipient_user_id,
        )

        if request is None:
            continue

        if (
            request.sender_user_id != sender_user_id
            or request.recipient_user_id != recipient_user_id
        ):
            continue

        await ctx.friend_requests.update_partial(request.id, deleted=True)
