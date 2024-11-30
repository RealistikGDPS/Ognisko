from __future__ import annotations

from typing import NamedTuple

from sqlmodel import SQLModel

from ognisko.utilities.colour import Colour


class DatabaseModel(SQLModel):
    """The base model for all SQLAlchemy models in Ognisko."""

    ...


class SearchResults[T](NamedTuple):
    results: list[T]
    total: int
    page_size: int
