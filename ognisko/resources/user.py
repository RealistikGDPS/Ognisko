from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from ognisko.adapters import AbstractMySQLService
from ognisko.adapters import MeiliSearchClient
from ognisko.common import modelling
from ognisko.common import time as time_utils
from ognisko.common.colour import Colour
from ognisko.resources._common import DatabaseModel
from ognisko.resources._common import SearchResults
from ognisko.utilities.enum import StrEnum


class UserPrivacySetting(StrEnum):
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


class UserDisplayBadge(StrEnum):
    """Enum for determining whether a user should be displayed as a
    moderator, elder moderator, or neither.
    """

    NONE = "none"
    MODERATOR = "moderator"
    ELDER_MODERATOR = "elder_moderator"


class UserModel(DatabaseModel):
    id: int
    username: str
    email: str

    displayed_badge: UserDisplayBadge
    message_privacy: UserPrivacySetting
    friend_privacy: UserPrivacySetting
    comment_privacy: UserPrivacySetting

    registered_at: datetime
    comment_colour: Colour


ALL_FIELDS = modelling.get_model_fields(UserModel)
CUSTOMISABLE_FIELDS = modelling.remove_id_field(ALL_FIELDS)


_ALL_FIELDS_COMMA = modelling.comma_separated(ALL_FIELDS)
_ALL_FIELDS_COLON = modelling.colon_prefixed_comma_separated(ALL_FIELDS)

DEFAULT_PAGE_SIZE = 10


class _UserUpdatePartial(TypedDict):
    """Set of optional key-word arguments that may be used to update a user."""

    username: NotRequired[str]
    email: NotRequired[str]
    privileges: NotRequired[UserPrivileges]
    message_privacy: NotRequired[UserPrivacySetting]
    friend_privacy: NotRequired[UserPrivacySetting]
    comment_privacy: NotRequired[UserPrivacySetting]
    youtube_name: NotRequired[str | None]
    twitter_name: NotRequired[str | None]
    twitch_name: NotRequired[str | None]
    stars: NotRequired[int]
    demons: NotRequired[int]
    moons: NotRequired[int]
    primary_colour: NotRequired[int]
    secondary_colour: NotRequired[int]
    glow_colour: NotRequired[int]
    display_type: NotRequired[int]
    icon: NotRequired[int]
    ship: NotRequired[int]
    ball: NotRequired[int]
    ufo: NotRequired[int]
    wave: NotRequired[int]
    robot: NotRequired[int]
    spider: NotRequired[int]
    swing_copter: NotRequired[int]
    jetpack: NotRequired[int]
    explosion: NotRequired[int]
    glow: NotRequired[bool]
    creator_points: NotRequired[int]
    coins: NotRequired[int]
    user_coins: NotRequired[int]
    diamonds: NotRequired[int]
    comment_colour: NotRequired[Colour]


# Meili type accommodation.
def _meili_dict_from_model(user_model: UserModel) -> dict[str, Any]:
    return _meili_dict_from_dict(user_model.model_dump())


def _meili_dict_from_dict(user_dict: dict[str, Any]) -> dict[str, Any]:
    if "privileges" in user_dict:
        user_dict["privileges"] = int.from_bytes(
            user_dict["privileges"],
            byteorder="little",
            signed=False,
        )
        user_dict["is_public"] = (
            user_dict["privileges"] & UserPrivileges.USER_PROFILE_PUBLIC > 0
        )

    if "register_ts" in user_dict:
        user_dict["register_ts"] = time_utils.into_unix_ts(user_dict["register_ts"])

    return user_dict


def _model_from_meili_dict(user_dict: dict[str, Any]) -> UserModel:
    user_dict = user_dict.copy()

    user_dict["privileges"] = UserPrivileges(int(user_dict["privileges"])).as_bytes()

    user_dict["register_ts"] = time_utils.from_unix_ts(user_dict["register_ts"])

    del user_dict["is_public"]

    return UserModel(**user_dict)


class UserRepository:
    def __init__(
        self,
        mysql: AbstractMySQLService,
        meili: MeiliSearchClient,
    ) -> None:
        self._mysql = mysql
        self._meili = meili.index("users")

    async def from_id(self, user_id: int) -> UserModel | None:
        user_db = await self._mysql.fetch_one(
            f"SELECT {_ALL_FIELDS_COMMA} FROM users WHERE id = :id",
            {"id": user_id},
        )

        if user_db is None:
            return None

        return UserModel(**user_db)

    async def multiple_from_id(self, user_ids: list[int]) -> list[UserModel]:
        if not user_ids:
            return []

        users_db = self._mysql.iterate(
            f"SELECT {_ALL_FIELDS_COMMA} FROM users WHERE id IN :ids",
            {"ids": tuple(user_ids)},
        )

        return [UserModel(**user_row) async for user_row in users_db]

    async def __update_meili(self, model: UserModel) -> None:
        user_dict = _meili_dict_from_model(model)
        await self._meili.add_documents([user_dict])

    async def create(
        self,
        username: str,
        email: str,
        *,
        privileges: UserPrivileges = DEFAULT_PRIVILEGES,
        message_privacy: UserPrivacySetting = UserPrivacySetting.PUBLIC,
        friend_privacy: UserPrivacySetting = UserPrivacySetting.PUBLIC,
        comment_privacy: UserPrivacySetting = UserPrivacySetting.PUBLIC,
        youtube_name: str | None = None,
        twitter_name: str | None = None,
        twitch_name: str | None = None,
        register_ts: datetime | None = None,
        stars: int = 0,
        demons: int = 0,
        moons: int = 0,
        primary_colour: int = 0,
        # NOTE: secondary_colour is 4 by default in the game
        secondary_colour: int = 4,
        glow_colour: int = 0,
        display_type: int = 0,
        icon: int = 0,
        ship: int = 0,
        ball: int = 0,
        ufo: int = 0,
        wave: int = 0,
        robot: int = 0,
        spider: int = 0,
        swing_copter: int = 0,
        jetpack: int = 0,
        explosion: int = 0,
        glow: bool = False,
        creator_points: int = 0,
        coins: int = 0,
        user_coins: int = 0,
        diamonds: int = 0,
        user_id: int | None = 0,
        comment_colour: Colour = Colour.default(),
    ) -> UserModel:
        if register_ts is None:
            register_ts = datetime.now()

        user_id_provided = user_id is not None
        if user_id is None:
            user_id = 0

        user = UserModel(
            id=user_id,
            username=username,
            email=email,
            privileges=privileges,
            message_privacy=message_privacy,
            friend_privacy=friend_privacy,
            comment_privacy=comment_privacy,
            youtube_name=youtube_name,
            twitter_name=twitter_name,
            twitch_name=twitch_name,
            register_ts=register_ts,
            stars=stars,
            demons=demons,
            moons=moons,
            primary_colour=primary_colour,
            secondary_colour=secondary_colour,
            glow_colour=glow_colour,
            display_type=display_type,
            icon=icon,
            ship=ship,
            ball=ball,
            ufo=ufo,
            wave=wave,
            robot=robot,
            spider=spider,
            swing_copter=swing_copter,
            jetpack=jetpack,
            explosion=explosion,
            glow=glow,
            creator_points=creator_points,
            coins=coins,
            user_coins=user_coins,
            diamonds=diamonds,
            comment_colour=comment_colour,
        )

        if user_id_provided:
            user_dict = user.model_dump()
        else:
            user_dict = user.model_dump(exclude={"id"}) | {
                "id": None,
            }

        user.id = await self._mysql.execute(
            f"INSERT INTO users ({_ALL_FIELDS_COMMA}) VALUES ({_ALL_FIELDS_COLON})",
            user_dict,
        )

        await self.__update_meili(user)
        return user

    async def update_partial(
        self,
        user_id: int,
        **kwargs: Unpack[_UserUpdatePartial],
    ) -> UserModel | None:
        changed_fields = modelling.unpack_enum_types(kwargs)

        await self._mysql.execute(
            modelling.update_from_partial_dict("users", user_id, changed_fields),
            changed_fields,
        )

        meili_dict = _meili_dict_from_dict(dict(kwargs)) | {
            "id": user_id,
        }

        await self._meili.update_documents([meili_dict])
        return await self.from_id(user_id)

    async def from_username(self, username: str) -> UserModel | None:
        user_id = await self._mysql.fetch_val(
            "SELECT id FROM users WHERE username = :username",
            {"username": username},
        )

        if user_id is None:
            return None

        return await self.from_id(user_id)

    async def all(self) -> AsyncGenerator[UserModel, None]:
        async for user_db in self._mysql.iterate(
            f"SELECT {_ALL_FIELDS_COMMA} FROM users",
        ):
            yield UserModel(**user_db)

    # Search related.
    async def search(
        self,
        query: str,
        *,
        page: int = 0,
        page_size: int = DEFAULT_PAGE_SIZE,
        include_hidden: bool = False,
    ) -> SearchResults[UserModel]:
        filters = []
        if not include_hidden:
            filters.append("is_public = true")

        results_db = await self._meili.search(
            query,
            offset=page * page_size,
            limit=page_size,
            filter=filters,
        )

        results = [_model_from_meili_dict(result) for result in results_db.hits]

        return SearchResults(
            results,
            results_db.estimated_total_hits or 0,
            page_size,
        )

    # Non-model related checks.
    async def is_email_available(self, email: str) -> bool:
        return not self._mysql.fetch_val(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = :email)",
            {
                "email": email,
            },
        )

    async def is_username_available(self, username: str) -> bool:
        return not self._mysql.fetch_val(
            "SELECT EXISTS(SELECT 1 FROM users WHERE username = :username)",
            {
                "username": username,
            },
        )

    async def count_all(self) -> int:
        return await self._mysql.fetch_val("SELECT COUNT(*) FROM users")
