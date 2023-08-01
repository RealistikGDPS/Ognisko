from __future__ import annotations

from typing import Any
from typing import Mapping

from databases import Database
from databases import DatabaseURL

# NOTE: This class exists due to Databases 0.6.0 breaking type annotations.
# NOTE: The usage of `_mapping` is required as accessing a row will raise a
# silent `DeprecationWarning`, leading to a lot of wasted time.
class MySQLService:
    def __init__(self, database_url: DatabaseURL) -> None:
        self._pool = Database(database_url)

    async def connect(self) -> None:
        await self._pool.connect()

    async def fetch_one(
        self,
        query: str,
        values: dict[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        res = await self._pool.fetch_one(query, values)  # type: ignore
        return res._mapping if res is not None else None

    async def fetch_all(
        self,
        query: str,
        values: dict[str, Any] | None = None,
    ) -> list[Mapping[str, Any]]:
        res = await self._pool.fetch_all(query, values)  # type: ignore
        return [res._mapping for res in res]

    async def execute(self, query: str, values: dict[str, Any] | None = None) -> Any:
        return await self._pool.execute(query, values)  # type: ignore

    async def fetch_val(
        self,
        query: str,
        values: dict[str, Any] | None = None,
    ) -> Any:
        res = await self._pool.fetch_val(query, values)  # type: ignore
        return res

    async def disconnect(self) -> None:
        await self._pool.disconnect()
