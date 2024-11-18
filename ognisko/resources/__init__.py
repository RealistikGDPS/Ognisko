from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .daily_chest import DailyChest
from .daily_chest import DailyChestRepository
from .daily_chest import DailyChestRewardType
from .daily_chest import DailyChestType
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
    @property
    @abstractmethod
    def save_data(self) -> SaveDataRepository: ...

    @property
    @abstractmethod
    def users(self) -> UserRepository: ...

    @property
    @abstractmethod
    def level_data(self) -> LevelDataRepository: ...

    @property
    @abstractmethod
    def relationships(self) -> UserRelationshipRepository: ...

    @property
    @abstractmethod
    def credentials(self) -> UserCredentialRepository: ...

    @property
    @abstractmethod
    def daily_chests(self) -> DailyChestRepository: ...

    @property
    @abstractmethod
    def leaderboards(self) -> LeaderboardRepository: ...

    @property
    @abstractmethod
    def messages(self) -> MessageRepository: ...

    @property
    @abstractmethod
    def user_comments(self) -> UserCommentRepository: ...

    @property
    @abstractmethod
    def likes(self) -> LikeRepository: ...

    @property
    @abstractmethod
    def friend_requests(self) -> FriendRequestRepository: ...

    @property
    @abstractmethod
    def level_comments(self) -> LevelCommentRepository: ...

    @property
    @abstractmethod
    def level_schedules(self) -> LevelScheduleRepository: ...

    @property
    @abstractmethod
    def levels(self) -> LevelRepository: ...

    @property
    @abstractmethod
    def songs(self) -> SongRepository: ...

    @property
    @abstractmethod
    def user_relationships(self) -> UserRelationshipRepository: ...
