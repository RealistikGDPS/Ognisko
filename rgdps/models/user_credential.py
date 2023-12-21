from __future__ import annotations

from dataclasses import dataclass

from rgdps.constants.user_credentials import CredentialVersion


@dataclass
class UserCredential:
    user_id: int
    version: CredentialVersion
    value: str
