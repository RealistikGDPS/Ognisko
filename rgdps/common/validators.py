from __future__ import annotations

import re
from typing import Any

from pydantic_core import core_schema

from rgdps.common import hashes

TEXT_BOX_REGEX = re.compile(r"^[a-zA-Z0-9 ]+$")
SOCIAL_MEDIA_REGEX = re.compile(r"^[\w\-.' ]+$")


class Base64String(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _: type[Any],
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

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
            raise ValueError("Input is not valid base64") from e


class TextBoxString(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _: type[Any],
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: Any, _: core_schema.ValidationInfo) -> TextBoxString:
        if not isinstance(value, (str, bytes)):
            raise TypeError("Value must be str or bytes")

        if isinstance(value, bytes):
            value = value.decode()

        # Value needs to be: stripped and alphanumeric.
        value = value.strip()

        if not TEXT_BOX_REGEX.match(value):
            raise ValueError("Input contains illegal characters")

        return TextBoxString(value)


class SocialMediaString(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _: type[Any],
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: Any, _: core_schema.ValidationInfo) -> TextBoxString:
        if not isinstance(value, (str, bytes)):
            raise TypeError("Value must be str or bytes")

        if isinstance(value, bytes):
            value = value.decode()

        # Value needs to be: stripped and alphanumeric + it can contain `_`, `-`, `.`, and `'`.
        value = value.strip()

        if not SOCIAL_MEDIA_REGEX.match(value):
            raise ValueError("Input contains illegal characters")

        return TextBoxString(value)


class MessageContentString(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _: type[Any],
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(
        cls,
        value: Any,
        _: core_schema.ValidationInfo,
    ) -> MessageContentString:
        if not isinstance(value, (str, bytes)):
            raise TypeError("Value must be str or bytes")

        if isinstance(value, bytes):
            value = value.decode()

        try:
            return MessageContentString(hashes.decrypt_message_content(value))
        except Exception as e:
            raise ValueError("Input is not valid base64 and xor cipher") from e
        

class IntegerList(list[int]):
    @classmethod
    def _validate(
        cls,
        value: Any,
        _: core_schema.ValidationInfo,
    ) -> IntegerList:
        if not isinstance(value, (str, bytes)):
            raise TypeError("Value must be str or bytes")

        if isinstance(value, bytes):
            value = value.decode()
        
        return IntegerList(
            map(int, value.strip().split(","))
        )
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _: type[Any],
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls._validate,
            core_schema.list_schema(),
        )
