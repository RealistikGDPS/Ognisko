from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Mapping

from rgdps.constants.user_credentials import CredentialVersion


@dataclass
class UserCredential:
    id: int
    user_id: int
    version: CredentialVersion
    value: str

    @staticmethod
    def from_mapping(credential_dict: Mapping[str, Any]) -> UserCredential:
        return UserCredential(
            id=credential_dict["id"],
            user_id=credential_dict["user_id"],
            version=CredentialVersion(credential_dict["version"]),
            value=credential_dict["value"],
        )

    def as_dict(self, *, include_id: bool) -> dict[str, Any]:
        res = {
            "user_id": self.user_id,
            "version": self.version.value,
            "value": self.value,
        }

        if include_id:
            res["id"] = self.id or None

        return res
