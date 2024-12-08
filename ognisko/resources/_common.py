from __future__ import annotations

from typing import NamedTuple

from sqlalchemy import Base
from sqlalchemy import BinaryExpression
from sqlalchemy import Column
from sqlalchemy import Integer

from ognisko.adapters import ImplementsMySQL


class DatabaseModel(Base):
    """The base model for all SQLAlchemy models in Ognisko. Includes
    an ID column that autoincrements."""

    id = Column(Integer, primary_key=True, autoincrement=True)


class BaseRepository[
    Model: DatabaseModel,
]:
    __slots__ = (
        "_mysql",
        "_model",
    )

    def __init__(self, mysql: ImplementsMySQL, model: type[Model]) -> None:
        self._mysql = mysql
        self._model = model

    async def from_id(self, resource_id: int) -> Model | None:
        return (
            await self._mysql.select(self._model)
            .where(self._model.id == resource_id)
            .fetch_one()
        )

    async def from_multiple_ids(
        self,
        resource_ids: list[int],
        *,
        ensure_sequence: bool = False,
    ) -> list[Model]:
        """Fetches multiple resources given a list of their IDs.
        The order is not guaranteed unless ensure_sequence is set to True."""
        results = (
            await self._mysql.select(self._model)
            .where(self._model.id.in_(resource_ids))
            .fetch_all()
        )

        if ensure_sequence:
            results = sorted(results, key=lambda x: resource_ids.index(x.id))  # type: ignore

        return results

    async def delete_from_id(self, resource_id: int) -> bool:
        """Deletes a resource from the model's table."""
        return (
            await self._mysql.delete(self._model)
            .where(
                self._model.id == resource_id,
            )
            .execute()
            > 0
        )

    async def create(self, *values: BinaryExpression) -> Model:
        """Creates a new resource in the model's table. It uses the SL
        of sqlalchemy to provide a typed argument.

        Example:
        ```py
        instance = await repository.create(
            Model.name << "example",
            Model.age << 20,
        )
        """
        # Generate kwargs from the values
        kwargs = {}
        for value in values:
            key = value.left.key
            value = value.right.value

            kwargs[key] = value

        resource_id = await self._mysql.insert(self._model).values(**kwargs).execute()
        return await self.from_id(resource_id)  # type: ignore

    async def update_partial(
        self,
        resource_id: int,
        *values: BinaryExpression,
    ) -> Model | None:
        """Updates a resource in the model's table. It uses the SL
        of sqlalchemy to provide a typed argument.

        Example:
        ```py
        instance = await repository.update_partial(
            1,
            Model.name == "example",
            Model.age == 20,
        )
        """
        # Generate kwargs from the values
        kwargs = {}
        for value in values:
            key = value.left.key
            value = value.right.value

            kwargs[key] = value

        await self._mysql.update(self._model).where(
            self._model.id == resource_id,
        ).values(**kwargs).execute()
        return await self.from_id(resource_id)

    async def count_all(self) -> int:
        """Counts all resources in the model's table."""

        # The or 0 is necessary because fetch_val returns None if no
        # results are found.
        return (
            await self._mysql.fetch_val(
                f"SELECT COUNT(*) FROM {self._model.__tablename__}",
            )
            or 0
        )


class SearchResults[T](NamedTuple):
    results: list[T]
    total: int
    page_size: int
