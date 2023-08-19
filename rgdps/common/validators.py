from __future__ import annotations

from typing import Any
from pydantic_core import core_schema
from rgdps.common import hashes

# Learning source: https://github.com/pydantic/pydantic/issues/692#issuecomment-515565389
class Base64String(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _: type[Any],
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(cls._validate, core_schema.str_schema())

    @classmethod
    def encode(cls, data: str) -> Base64String:
        return Base64String(hashes.encode_base64(data))

    @classmethod
    def _validate(cls, value: Any, _: core_schema.ValidationInfo) -> Base64String:
        if not isinstance(value, (str, bytes)):
            raise TypeError("Value must be str or bytes")

        if isinstance(value, bytes):
            value = value.decode()

        try:
            return Base64String(hashes.decode_base64(value))
        except Exception as e:
            raise ValueError(f"Input is not valid base64") from e
