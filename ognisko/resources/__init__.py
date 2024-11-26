from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ognisko.adapters.boomlings import GeometryDashClient
from ognisko.adapters.meilisearch import MeiliSearchClient
from ognisko.adapters.mysql import AbstractMySQLService
from ognisko.adapters.redis import RedisClient
from ognisko.adapters.storage import AbstractStorage

from .daily_chest import DailyChest
from .daily_chest import DailyChestRepository
from .daily_chest import DailyChestRewardType
from .daily_chest import DailyChestType
from .daily_chest import DailyChestView
from .friend_request import FriendRequest
from .friend_request import FriendRequestRepository
from .leaderboard import LeaderboardRepository
from .level import Level
from .level import LevelRepository
from .level_comment import LevelComment
from .level_comment import LevelCommentRepository
from .level_data import LevelData
from .level_data import LevelDataRepository
from .level_schedule import LevelSchedule
from .level_schedule import LevelScheduleRepository
from .like import Like
from .like import LikeRepository
from .like import LikeType
from .message import Message
from .message import MessageRepository
from .save_data import SaveData
from .save_data import SaveDataRepository
from .song import Song
from .song import SongRepository
from .user import User
from .user import UserRepository
from .user_comment import UserComment
from .user_comment import UserCommentRepository
from .user_credential import UserCredential
from .user_credential import UserCredentialRepository
from .user_replationship import UserRelationship
from .user_replationship import UserRelationshipRepository
from .user_replationship import UserRelationshipType


class Context(ABC):
    # Abstract properties
    @property
    @abstractmethod
    def _mysql(self) -> AbstractMySQLService: ...

    @property
    @abstractmethod
    def _redis(self) -> RedisClient: ...

    @property
    @abstractmethod
    def _meili(self) -> MeiliSearchClient: ...

    @property
    @abstractmethod
    def _storage(self) -> AbstractStorage: ...

    @property
    @abstractmethod
    def _gd(self) -> GeometryDashClient: ...

    # Rest
    @property
    def save_data(self) -> SaveDataRepository:
        return SaveDataRepository(self._storage)

    @property
    def users(self) -> UserRepository:
        return UserRepository(
            self._mysql,
            self._meili,
        )

    @property
    def level_data(self) -> LevelDataRepository:
        return LevelDataRepository(
            self._storage,
        )

    @property
    def relationships(self) -> UserRelationshipRepository:
        return UserRelationshipRepository(self._mysql)

    @property
    def credentials(self) -> UserCredentialRepository:
        return UserCredentialRepository(self._mysql)

    @property
    def daily_chests(self) -> DailyChestRepository:
        return DailyChestRepository(self._mysql)

    @property
    def leaderboards(self) -> LeaderboardRepository:
        return LeaderboardRepository(self._redis)

    @property
    def messages(self) -> MessageRepository:
        return MessageRepository(self._mysql)

    @property
    def user_comments(self) -> UserCommentRepository:
        return UserCommentRepository(self._mysql)

    @property
    def likes(self) -> LikeRepository:
        return LikeRepository(self._mysql)

    @property
    def friend_requests(self) -> FriendRequestRepository:
        return FriendRequestRepository(self._mysql)

    @property
    def level_comments(self) -> LevelCommentRepository:
        return LevelCommentRepository(self._mysql)

    @property
    def level_schedules(self) -> LevelScheduleRepository:
        return LevelScheduleRepository(self._mysql)

    @property
    def levels(self) -> LevelRepository:
        return LevelRepository(self._mysql, self._meili)

    @property
    def songs(self) -> SongRepository:
        return SongRepository(self._mysql, self._gd)

    @property
    def user_relationships(self) -> UserRelationshipRepository:
        return UserRelationshipRepository(self._mysql)
