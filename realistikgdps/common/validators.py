from __future__ import annotations

import base64
from typing import Any

from pydantic.typing import CallableGenerator

# Learning source: https://github.com/pydantic/pydantic/issues/692#issuecomment-515565389
class Base64String(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def encode(cls, data: str) -> Base64String:
        return cls(base64.b64encode(data.encode()).decode())

    @classmethod
    def validate(cls, value: Any) -> Base64String:
        if not isinstance(value, (str, bytes)):
            raise TypeError("Value must be str or bytes")

        if isinstance(value, str):
            value = value.encode()

        try:
            return cls(base64.b64decode(value).decode())
        except Exception as e:
            raise ValueError(f"Input is not valid base64") from e
