from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncGenerator
from collections.abc import Mapping
from typing import Any

from databases import Database
from databases import DatabaseURL
from databases.core import Connection
from databases.core import Transaction
from sqlalchemy.sql import ClauseElement

type MySQLValue = Any
type MySQLRow = Mapping[str, MySQLValue]
type MySQLValues = dict[str, MySQLValue]
type QueryType = str | ClauseElement


class AbstractMySQLService(ABC):
    @abstractmethod
    async def fetch_one(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> MySQLRow | None: ...

    @abstractmethod
    async def fetch_all(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> list[MySQLRow]: ...

    @abstractmethod
    async def fetch_val(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> Any: ...

    @abstractmethod
    async def execute(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> Any: ...

    @abstractmethod
    def iterate(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> AsyncGenerator[MySQLRow, None]: ...


class MySQLService(AbstractMySQLService):
    def __init__(self, database_url: DatabaseURL) -> None:
        self._pool = Database(database_url)

    async def connect(self) -> None:
        await self._pool.connect()

    async def disconnect(self) -> None:
        await self._pool.disconnect()

    async def fetch_one(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> MySQLRow | None:
        res = await self._pool.fetch_one(query, values)  # type: ignore
        return res._mapping if res is not None else None

    async def fetch_all(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> list[MySQLRow]:
        res = await self._pool.fetch_all(query, values)  # type: ignore
        return [res._mapping for res in res]

    async def fetch_val(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> Any:
        res = await self._pool.fetch_val(query, values)  # type: ignore
        return res

    async def execute(self, query: QueryType, values: MySQLValues | None = None) -> Any:
        return await self._pool.execute(query, values)  # type: ignore

    def iterate(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> AsyncGenerator[MySQLRow, None]:
        return self._pool.iterate(query, values)  # type: ignore

    def transaction(self) -> MySQLTransaction:
        return MySQLTransaction(self._pool)


class MySQLTransaction(AbstractMySQLService):
    """A wrapper around a transaction that implements the same interface as
    `MySQLService`."""

    def __init__(self, backend_pool: Database) -> None:
        self._backend_pool: Database = backend_pool
        self._connection: Connection | None = None
        self._transaction: Transaction | None = None

    async def __aenter__(self) -> MySQLTransaction:
        self._connection = await self._backend_pool.connection().__aenter__()
        self._transaction = await self._connection.transaction().__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        # NOTE: This handles rollback on exception using `args`.
        if self._transaction is not None:
            await self._transaction.__aexit__(*args)

        if self._connection is not None:
            await self._connection.__aexit__(*args)

    async def fetch_one(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> MySQLRow | None:
        res = await self._connection.fetch_one(query, values)  # type: ignore
        return res._mapping if res is not None else None

    async def fetch_all(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> list[MySQLRow]:
        res = await self._connection.fetch_all(query, values)  # type: ignore
        return [res._mapping for res in res]

    async def fetch_val(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> Any:
        res = await self._connection.fetch_val(query, values)  # type: ignore
        return res

    async def execute(self, query: QueryType, values: MySQLValues | None = None) -> Any:
        return await self._connection.execute(query, values)  # type: ignore

    def iterate(
        self,
        query: QueryType,
        values: MySQLValues | None = None,
    ) -> AsyncGenerator[MySQLRow, None]:
        return self._connection.iterate(query, values)  # type: ignore
