from __future__ import annotations

from datetime import datetime

from ognisko.resources._common import DatabaseModel
from ognisko.utilities.enum import StrEnum


class SocialLinkType(StrEnum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    DISCORD = "discord"


class UserSocialLinkModel(DatabaseModel):
    id: int
    user_id: int
    link_type: SocialLinkType
    link: str
    linked_at: datetime
