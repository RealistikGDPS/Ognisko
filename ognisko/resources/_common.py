from __future__ import annotations

from typing import NamedTuple
from typing import TypedDict
from typing import Unpack
from typing import get_args
from typing import Any
from cachetools import cached

from sqlalchemy import Base, Column, Integer

from ognisko.utilities.colour import Colour


class DatabaseModel(Base):
    """The base model for all SQLAlchemy models in Ognisko."""

    id = Column(Integer, primary_key=True, autoincrement=True)


class PartialUpdateBase(TypedDict, total=False):
    id: int

    ...


class BaseRepository[
    Model: DatabaseModel,
    PartialUpdate: PartialUpdateBase,
    CreateModel: DatabaseModel = Model,
    UpdateModel: DatabaseModel = Model,
]:
    __slots__ = (
        "_session",
    )

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    
    @property
    @cached(cache={})
    def __innter_type(self) -> type[Model]:
        """Internal variable to return the actual type of the model."""

        annotated = get_args(self)
        return annotated[0]
    

    async def from_id(self, id: int) -> Model | None:
        return await self._session.get(self.__innter_type, id)


    async def create(self, model: CreateModel) -> Model:
        new_model = self.__innter_type(**model.model_dump())
        self._session.add(new_model)

        return await self.from_id(new_model.id) # type: ignore
    

    async def update(self, id: int, **kwargs: Unpack[PartialUpdate]) -> Model:
        model = await self.from_id(id)

        for key, value in kwargs.items():
            setattr(model, key, value)


        await self._session.

        return model



class SearchResults[T](NamedTuple):
    results: list[T]
    total: int
    page_size: int
