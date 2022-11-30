from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Mapping
from typing import Optional

from rgdps.constants.privacy import PrivacySetting


@dataclass
class User:
    id: int
    username: str
    email: str
    password: str

    message_privacy: PrivacySetting
    friend_privacy: PrivacySetting
    comment_privacy: PrivacySetting

    youtube_name: Optional[str]
    twitter_name: Optional[str]
    twitch_name: Optional[str]

    register_ts: datetime

    # Stats
    stars: int
    demons: int
    primary_colour: int
    secondary_colour: int
    display_type: int
    icon: int
    ship: int
    ball: int
    ufo: int
    wave: int
    robot: int
    spider: int
    explosion: int
    glow: bool
    creator_points: int
    coins: int
    user_coins: int
    diamonds: int

    def __str__(self) -> str:
        return f"{self.username} ({self.id})"

    @staticmethod
    def from_mapping(user_dict: Mapping[str, Any]) -> User:
        return User(
            id=user_dict["id"],
            username=user_dict["username"],
            email=user_dict["email"],
            password=user_dict["password"],
            message_privacy=PrivacySetting(user_dict["message_privacy"]),
            friend_privacy=PrivacySetting(user_dict["friend_privacy"]),
            comment_privacy=PrivacySetting(user_dict["comment_privacy"]),
            youtube_name=user_dict["youtube_name"],
            twitter_name=user_dict["twitter_name"],
            twitch_name=user_dict["twitch_name"],
            register_ts=user_dict["register_ts"],
            stars=user_dict["stars"],
            demons=user_dict["demons"],
            primary_colour=user_dict["primary_colour"],
            secondary_colour=user_dict["secondary_colour"],
            display_type=user_dict["display_type"],
            icon=user_dict["icon"],
            ship=user_dict["ship"],
            ball=user_dict["ball"],
            ufo=user_dict["ufo"],
            wave=user_dict["wave"],
            robot=user_dict["robot"],
            spider=user_dict["spider"],
            explosion=user_dict["explosion"],
            glow=bool(user_dict["glow"]),
            creator_points=user_dict["creator_points"],
            coins=user_dict["coins"],
            user_coins=user_dict["user_coins"],
            diamonds=user_dict["diamonds"],
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "message_privacy": self.message_privacy.value,
            "friend_privacy": self.friend_privacy.value,
            "comment_privacy": self.comment_privacy.value,
            "twitter_name": self.twitter_name,
            "youtube_name": self.youtube_name,
            "twitch_name": self.twitch_name,
            "stars": self.stars,
            "demons": self.demons,
            "primary_colour": self.primary_colour,
            "secondary_colour": self.secondary_colour,
            "display_type": self.display_type,
            "icon": self.icon,
            "ship": self.ship,
            "ball": self.ball,
            "ufo": self.ufo,
            "wave": self.wave,
            "robot": self.robot,
            "spider": self.spider,
            "explosion": self.explosion,
            "glow": self.glow,
            "creator_points": self.creator_points,
            "coins": self.coins,
            "user_coins": self.user_coins,
            "diamonds": self.diamonds,
        }

        if include_id:
            res["id"] = self.id

        return res
