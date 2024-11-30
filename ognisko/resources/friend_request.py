from __future__ import annotations

from datetime import datetime
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from ognisko.adapters import AbstractMySQLService
from ognisko.common import modelling
from ognisko.resources._common import DatabaseModel


class FriendRequestModel(DatabaseModel):
    id: int
    sender_user_id: int
    recipient_user_id: int
    message: str
    posted_at: datetime
    seen_at: datetime | None


class _FriendRequestUpdatePartial(TypedDict):
    sender_user_id: NotRequired[int]
    recipient_user_id: NotRequired[int]
    seen_ts: NotRequired[datetime]
    deleted: NotRequired[bool]


ALL_FIELDS = modelling.get_model_fields(FriendRequestModel)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)

_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COMMA = modelling.comma_separated(CUSTOMISABLE_FIELDS)

_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)
_CUSTOMISABLE_FIELDS_COLON = modelling.colon_prefixed_comma_separated(
    CUSTOMISABLE_FIELDS,
)


class FriendRequestRepository:
    __slots__ = ("_mysql",)

    def __init__(self, mysql: AbstractMySQLService) -> None:
        self._mysql = mysql

    async def from_id(self, request_id: int) -> FriendRequestModel | None:
        friend_request_db = await self._mysql.fetch_one(
            f"SELECT * FROM friend_requests WHERE id = :request_id",
            {"request_id": request_id},
        )

        if friend_request_db is None:
            return None

        return FriendRequestModel(**friend_request_db)

    async def from_target_and_reciptient(
        self,
        sender_user_id: int,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> FriendRequestModel | None:
        friend_request_db = await self._mysql.fetch_one(
            f"SELECT * FROM friend_requests WHERE sender_user_id = :sender_user_id"
            " AND recipient_user_id = :recipient_user_id AND deleted IN :include_deleted",
            {
                "sender_user_id": sender_user_id,
                "recipient_user_id": recipient_user_id,
                "include_deleted": (0, 1) if include_deleted else (0,),
            },
        )

        if friend_request_db is None:
            return None

        return FriendRequestModel(**friend_request_db)

    async def from_sender_user_id(
        self,
        sender_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        friend_requests_db = await self._mysql.fetch_all(
            f"SELECT * FROM friend_requests WHERE sender_user_id = :sender_user_id"
            " AND deleted IN :include_deleted",
            {
                "sender_user_id": sender_user_id,
                "include_deleted": (0, 1) if include_deleted else (0,),
            },
        )

        return [
            FriendRequestModel(**friend_request_db)
            for friend_request_db in friend_requests_db
        ]

    async def from_recipient_user_id(
        self,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        friend_requests_db = await self._mysql.fetch_all(
            f"SELECT * FROM friend_requests WHERE recipient_user_id = :recipient_user_id"
            " AND deleted IN :include_deleted",
            {
                "recipient_user_id": recipient_user_id,
                "include_deleted": (0, 1) if include_deleted else (0,),
            },
        )

        return [
            FriendRequestModel(**friend_request_db)
            for friend_request_db in friend_requests_db
        ]

    async def from_sender_user_id_paginated(
        self,
        sender_user_id: int,
        page: int,
        page_size: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        friend_requests_db = await self._mysql.fetch_all(
            f"SELECT * FROM friend_requests WHERE sender_user_id = :sender_user_id"
            " AND deleted IN :include_deleted LIMIT :limit OFFSET :offset",
            {
                "sender_user_id": sender_user_id,
                "include_deleted": (0, 1) if include_deleted else (0,),
                "limit": page_size,
                "offset": page * page_size,
            },
        )

        return [
            FriendRequestModel(**friend_request_db)
            for friend_request_db in friend_requests_db
        ]

    async def from_recipient_user_id_paginated(
        self,
        recipient_user_id: int,
        page: int,
        page_size: int,
        *,
        include_deleted: bool = False,
    ) -> list[FriendRequestModel]:
        friend_requests_db = await self._mysql.fetch_all(
            f"SELECT * FROM friend_requests WHERE recipient_user_id = :recipient_user_id"
            " AND deleted IN :include_deleted LIMIT :limit OFFSET :offset",
            {
                "recipient_user_id": recipient_user_id,
                "include_deleted": (0, 1) if include_deleted else (0,),
                "limit": page_size,
                "offset": page * page_size,
            },
        )

        return [
            FriendRequestModel(**friend_request_db)
            for friend_request_db in friend_requests_db
        ]

    async def count_incoming_requests(self, user_id: int) -> int:
        return await self._mysql.fetch_val(
            "SELECT COUNT(*) FROM friend_requests WHERE "
            "recipient_user_id = :user_id AND deleted = 0",
            {"user_id": user_id},
        )

    async def count_outgoing_requests(self, user_id: int) -> int:
        return await self._mysql.fetch_val(
            "SELECT COUNT(*) FROM friend_requests WHERE "
            "sender_user_id = :user_id AND deleted = 0",
            {"user_id": user_id},
        )

    async def exists_from_target_and_sender(
        self,
        sender_user_id: int,
        recipient_user_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        return (
            await self._mysql.fetch_val(
                "SELECT 1 FROM friend_requests WHERE sender_user_id = :sender_user_id"
                " AND recipient_user_id = :recipient_user_id AND deleted IN :include_deleted",
                {
                    "sender_user_id": sender_user_id,
                    "recipient_user_id": recipient_user_id,
                    "include_deleted": (0, 1) if include_deleted else (0,),
                },
            )
        ) is not None

    async def create(
        self,
        sender_user_id: int,
        recipient_user_id: int,
        message: str,
        post_ts: datetime | None = None,
        seen_ts: datetime | None = None,
    ) -> FriendRequestModel:
        if post_ts is None:
            post_ts = datetime.now()

        friend_request = FriendRequestModel(
            id=0,
            sender_user_id=sender_user_id,
            recipient_user_id=recipient_user_id,
            message=message,
            posted_at=post_ts,
            seen_at=seen_ts,
        )

        friend_request.id = await self._mysql.execute(
            f"INSERT INTO friend_requests ({_CUSTOMISABLE_FIELDS_COMMA}) VALUES "
            f"({_CUSTOMISABLE_FIELDS_COLON})",
            friend_request.model_dump(exclude={"id"}),
        )

        return friend_request

    async def update_partial(
        self,
        request_id: int,
        **kwargs: Unpack[_FriendRequestUpdatePartial],
    ) -> FriendRequestModel | None:
        changed_fields = modelling.unpack_enum_types(kwargs)

        await self._mysql.execute(
            modelling.update_from_partial_dict(
                "friend_requests",
                request_id,
                changed_fields,
            ),
            changed_fields,
        )

        return await self.from_id(request_id)

    async def count_all(self) -> int:
        return await self._mysql.fetch_val("SELECT COUNT(*) FROM friend_requests")
