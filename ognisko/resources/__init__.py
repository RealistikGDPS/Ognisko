from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ognisko.adapters.boomlings import GeometryDashClient
from ognisko.adapters.meilisearch import MeiliSearchClient
from ognisko.adapters.mysql import MySQLConnection
from ognisko.adapters.redis import RedisClient
from ognisko.adapters.storage import AbstractStorage

from .custom_song import CustomSongModel
from .custom_song import SongRepository
from .daily_chest import DailyChestModel
from .daily_chest import DailyChestRepository
from .daily_chest import DailyChestRewardType
from .daily_chest import DailyChestTier
from .daily_chest import DailyChestView
from .friend_request import FriendRequestModel
from .friend_request import FriendRequestRepository
from .leaderboard import LeaderboardRepository
from .level import CustomLevelModel
from .level import LevelRepository
from .level_comment import LevelCommentModel
from .level_comment import LevelCommentRepository
from .level_data import LevelData
from .level_data import LevelDataRepository
from .level_schedule import LevelScheduleModel
from .level_schedule import LevelScheduleRepository
from .like_interaction import LikedResource
from .like_interaction import LikeInteractionModel
from .like_interaction import LikeInteractionRepository
from .message import MessageRepository
from .message import UserMessageModel
from .save_data import SaveData
from .save_data import SaveDataRepository
from .user import UserModel
from .user import UserRepository
from .user_comment import UserCommentRepository
from .user_comment import UserProfileCommentModel
from .user_credential import UserCredentialModel
from .user_credential import UserCredentialRepository
from .user_replationship import UserRelationshipModel
from .user_replationship import UserRelationshipRepository
from .user_replationship import UserRelationshipType


class Context(ABC):
    # Abstract properties
    @property
    @abstractmethod
    def _mysql(self) -> MySQLConnection: ...

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
    def likes(self) -> LikeInteractionRepository:
        return LikeInteractionRepository(self._mysql)

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
