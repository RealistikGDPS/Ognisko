from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from typing import Union

@dataclass
class User:
    id: int
    ext_id: str
    name: str

    # Stats
    stars: int
    demons: int
    primary_colour: int
    secondary_colour: int
    display_type: int # Which gamemode to display as main
    coins: int
    user_coins: int
    creator_points: int

    # Display icons
    icon: int
    ship: int
    ball: int
    ufo: int
    wave: int
    robot: int
    spider: int
    glow: bool

    # Privileges?
    player_lb_ban: bool
    creator_lb_ban: bool

    @property
    def registered(self) -> bool:
        """Whether the user model corresponds to a registered account."""

        return self.ext_id.isnumeric()

    @property
    def account_id(self) -> Optional[int]:
        if self.registered:
            return int(self.ext_id)
        
        return None
