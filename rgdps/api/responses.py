from __future__ import annotations

from fastapi.responses import PlainTextResponse

from rgdps.common.typing import SupportsStr
from rgdps.constants.responses import GenericResponse


def success() -> PlainTextResponse:
    return PlainTextResponse(str(GenericResponse.SUCCESS))


def fail() -> PlainTextResponse:
    return PlainTextResponse(str(GenericResponse.FAIL))


def code(code: SupportsStr) -> PlainTextResponse:
    return PlainTextResponse(str(code))
