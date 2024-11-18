# from __future__ import annotations # This causes a pydantic issue. Yikes.

from typing import override

from fastapi import FastAPI
from fastapi import Request

from ognisko.adapters.boomlings import GeometryDashClient
from ognisko.adapters.meilisearch import MeiliSearchClient
from ognisko.adapters.mysql import AbstractMySQLService
from ognisko.adapters.redis import RedisClient
from ognisko.adapters.storage import AbstractStorage
from ognisko.resources import Context
from ognisko.resources import DailyChestRepository
from ognisko.resources import FriendRequestRepository
from ognisko.resources import LeaderboardRepository
from ognisko.resources import LevelCommentRepository
from ognisko.resources import LevelDataRepository
from ognisko.resources import LevelRepository
from ognisko.resources import LevelScheduleRepository
from ognisko.resources import LikeRepository
from ognisko.resources import MessageRepository
from ognisko.resources import SaveDataRepository
from ognisko.resources import SongRepository
from ognisko.resources import UserCommentRepository
from ognisko.resources import UserCredentialRepository
from ognisko.resources import UserRelationshipRepository
from ognisko.resources import UserRepository


class HTTPContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def __mysql(self) -> AbstractMySQLService:
        return self.request.app.state.mysql

    @property
    def __redis(self) -> RedisClient:
        return self.request.app.state.redis

    @property
    def __meili(self) -> MeiliSearchClient:
        return self.request.app.state.meili

    @property
    def __storage(self) -> AbstractStorage:
        return self.request.app.state.storage

    @property
    def __gd(self) -> GeometryDashClient:
        return self.request.app.state.gd

    @property
    def save_data(self) -> SaveDataRepository:
        return SaveDataRepository(self.__storage)

    @property
    @override
    def users(self) -> UserRepository:
        return UserRepository(
            self.__mysql,
            self.__meili,
        )

    @property
    @override
    def level_data(self) -> LevelDataRepository:
        return LevelDataRepository(
            self.__storage,
        )

    @property
    @override
    def relationships(self) -> UserRelationshipRepository:
        return UserRelationshipRepository(self.__mysql)

    @property
    @override
    def credentials(self) -> UserCredentialRepository:
        return UserCredentialRepository(self.__mysql)

    @property
    @override
    def daily_chests(self) -> DailyChestRepository:
        return DailyChestRepository(self.__mysql)

    @property
    @override
    def leaderboards(self) -> LeaderboardRepository:
        return LeaderboardRepository(self.__redis)

    @property
    @override
    def messages(self) -> MessageRepository:
        return MessageRepository(self.__mysql)

    @property
    @override
    def user_comments(self) -> UserCommentRepository:
        return UserCommentRepository(self.__mysql)

    @property
    @override
    def likes(self) -> LikeRepository:
        return LikeRepository(self.__mysql)

    @property
    @override
    def friend_requests(self) -> FriendRequestRepository:
        return FriendRequestRepository(self.__mysql)

    @property
    @override
    def level_comments(self) -> LevelCommentRepository:
        return LevelCommentRepository(self.__mysql)

    @property
    @override
    def level_schedules(self) -> LevelScheduleRepository:
        return LevelScheduleRepository(self.__mysql)

    @property
    @override
    def levels(self) -> LevelRepository:
        return LevelRepository(self.__mysql, self.__meili)

    @property
    @override
    def songs(self) -> SongRepository:
        return SongRepository(self.__mysql, self.__gd)


# FIXME: Proper context for pubsub handlers that does not rely on app.
class PubsubContext(Context):
    """A shared context for pubsub handlers."""

    def __init__(self, app: FastAPI) -> None:
        self.state = app.state

    @property
    def __mysql(self) -> AbstractMySQLService:
        return self.state.mysql

    @property
    def __redis(self) -> RedisClient:
        return self.state.redis

    @property
    def __meili(self) -> MeiliSearchClient:
        return self.state.meili

    @property
    def __storage(self) -> AbstractStorage:
        return self.state.storage

    @property
    def __gd(self) -> GeometryDashClient:
        return self.state.gd

    @property
    def save_data(self) -> SaveDataRepository:
        return SaveDataRepository(self.__storage)

    @property
    @override
    def users(self) -> UserRepository:
        return UserRepository(
            self.__mysql,
            self.__meili,
        )

    @property
    @override
    def level_data(self) -> LevelDataRepository:
        return LevelDataRepository(
            self.__storage,
        )

    @property
    @override
    def relationships(self) -> UserRelationshipRepository:
        return UserRelationshipRepository(self.__mysql)

    @property
    @override
    def credentials(self) -> UserCredentialRepository:
        return UserCredentialRepository(self.__mysql)

    @property
    @override
    def daily_chests(self) -> DailyChestRepository:
        return DailyChestRepository(self.__mysql)

    @property
    @override
    def leaderboards(self) -> LeaderboardRepository:
        return LeaderboardRepository(self.__redis)

    @property
    @override
    def messages(self) -> MessageRepository:
        return MessageRepository(self.__mysql)

    @property
    @override
    def user_comments(self) -> UserCommentRepository:
        return UserCommentRepository(self.__mysql)

    @property
    @override
    def likes(self) -> LikeRepository:
        return LikeRepository(self.__mysql)

    @property
    @override
    def friend_requests(self) -> FriendRequestRepository:
        return FriendRequestRepository(self.__mysql)

    @property
    @override
    def level_comments(self) -> LevelCommentRepository:
        return LevelCommentRepository(self.__mysql)

    @property
    @override
    def level_schedules(self) -> LevelScheduleRepository:
        return LevelScheduleRepository(self.__mysql)

    @property
    @override
    def levels(self) -> LevelRepository:
        return LevelRepository(self.__mysql, self.__meili)

    @property
    @override
    def songs(self) -> SongRepository:
        return SongRepository(self.__mysql, self.__gd)
