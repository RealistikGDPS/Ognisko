from __future__ import annotations

import base64
from typing import Any
from typing import Generator

from rgdps.common import hashes

# Learning source: https://github.com/pydantic/pydantic/issues/692#issuecomment-515565389
class Base64String(str):
    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate

    @classmethod
    def encode(cls, data: str) -> Base64String:
        return Base64String(hashes.encode_base64(data))

    @classmethod
    def validate(cls, value: Any) -> Base64String:
        if not isinstance(value, (str, bytes)):
            raise TypeError("Value must be str or bytes")

        if isinstance(value, bytes):
            value = value.decode()

        try:
            return Base64String(hashes.decode_base64(value))
        except Exception as e:
            raise ValueError(f"Input is not valid base64") from e
