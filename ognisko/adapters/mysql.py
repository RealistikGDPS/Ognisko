# NOTE: This class exists due to Databases 0.6.0 breaking type annotations.
# NOTE: The usage of `_mapping` is required as accessing a row will raise a
# silent `DeprecationWarning`, leading to a lot of wasted time.
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncGenerator
from collections.abc import Mapping
from typing import Any
from typing import override
from typing import Protocol
from typing import Mapping
from typing import Callable
from typing import Self

from databases import Database
from databases import DatabaseURL
from databases.core import Connection
from databases.core import Transaction
from databases.interfaces import Record
from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import update
from sqlalchemy import insert
from sqlalchemy import Select
from sqlalchemy import Insert
from sqlalchemy import Update
from sqlalchemy import Delete
from sqlalchemy.orm import DeclarativeBase as BaseModel
from sqlalchemy.dialects.mysql.mysqldb import MySQLDialect_mysqldb
from sqlalchemy.sql.compiler import Compiled
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.elements import SQLCoreOperations
from sqlalchemy.sql._typing import ColumnExpressionArgument, _ColumnExpressionOrStrLabelArgument

type MySQLValue = Any
type MySQLRow = Mapping[str, MySQLValue]
type MySQLValues = dict[str, MySQLValue]


# https://github.com/osuAkatsuki/bancho.py/blob/f9263dd6c71e3298bd10ebd5d1787e78a7a82e12/app/adapters/database.py#L17C1-L18C33
# Compatibility with databases
class MySQLDialect(MySQLDialect_mysqldb):
    default_paramstyle = "named"


class _MySQLQueryableProtocol(Protocol):
    async def execute(self, query: str, values: MySQLValues | None = None) -> Any: ...
    async def fetch_one(self, query: str, values: MySQLValues | None = None) -> Record | None: ...
    async def fetch_all(self, query: str, values: MySQLValues | None = None) -> list[Record]: ...
    async def fetch_val(self, query: str, values: MySQLValues | None = None) -> Any: ...
    async def iterate(self, query: str, values: MySQLValues | None = None) -> AsyncGenerator[Mapping, None]: ...


MYSQL_DIALECT = MySQLDialect()

class _CompilableStatementWrapper[Q: ClauseElement]:
    __slots__ = ("_query", "_connection")
    _connection: _MySQLQueryableProtocol
    _query: Q

    def _compile(self) -> tuple[str, MySQLValues | None]:
        compiled: Compiled = self._query.compile(dialect=MYSQL_DIALECT)
        if compiled.params is not None:
            return str(compiled), dict(compiled.params)
        
        return str(compiled), None
    

class _SelectWrapper[T: BaseModel](_CompilableStatementWrapper[Select[tuple[T]]]):
    def __init__(self, model: type[T], connection: _MySQLQueryableProtocol) -> None:
        self._query = select(model)
        self._connection = connection

    def where(self, *clauses: ColumnExpressionArgument[bool]) -> Self:
        self._query = self._query.where(*clauses)
        return self
    
    def limit(self, limit: int) -> Self:
        self._query = self._query.limit(limit)
        return self
        
    def offset(self, offset: int) -> Self:
        self._query = self._query.offset(offset)
        return self
        
    def order_by(self, *clauses: _ColumnExpressionOrStrLabelArgument[Any]) -> Self:
        self._query = self._query.order_by(*clauses)
        return self
    
    async def fetch_one(self) -> T | None:
        query, args = self._compile()
        return await self._connection.fetch_one(query, args) # type: ignore
    
    async def fetch_all(self) -> list[T]:
        query, args = self._compile()
        return await self._connection.fetch_all(query, args) # type: ignore
    
    async def iterate(self) -> AsyncGenerator[T, None]:
        query, args = self._compile()
        async for row in self._connection.iterate(query, args):
            # TODO: I am sus about the type here.
            yield row # type: ignore


class _DeleteWrapper[T: BaseModel](_CompilableStatementWrapper[Delete[tuple[T]]]):
    def __init__(self, model: type[T], connection: _MySQLQueryableProtocol) -> None:
        self._query = delete(model)
        self._connection = connection
    
    async def execute(self) -> int:
        """Returns the number of rows deleted."""
        query, args = self._compile()

        return await self._connection.execute(query, args)
    
    def where(self, *clauses: ColumnExpressionArgument[bool]) -> Self:
        self._query = self._query.where(*clauses)
        return self
    

class _UpdateWrapper[T: BaseModel](_CompilableStatementWrapper[Update[tuple[T]]]):
    def __init__(self, model: type[T], connection: _MySQLQueryableProtocol) -> None:
        self._query = update(model)
        self._connection = connection
    
    async def execute(self) -> int:
        """Returns the number of rows updated."""
        query, args = self._compile()

        return await self._connection.execute(query, args)
    
    def where(self, *clauses: ColumnExpressionArgument[bool]) -> Self:
        self._query = self._query.where(*clauses)
        return self
    
    # TODO: Type kwargs properly.
    def values(self, **kwargs: MySQLValue) -> Self:
        self._query = self._query.values(**kwargs)
        return self
    

class _InsertWrapper[T: BaseModel](_CompilableStatementWrapper[Insert[tuple[T]]]):
    def __init__(self, model: type[T], connection: _MySQLQueryableProtocol) -> None:
        self._query = insert(model)
        self._connection = connection
    
    async def execute(self) -> None:
        query, args = self._compile()

        await self._connection.execute(query, args)

    # TODO: Type kwargs properly.
    def values(self, **kwargs: MySQLValues) -> Self:
        self._query = self._query.values(**kwargs)
        return self

class ImplementsQueryableConnection(ABC):
    """An abstract class that implements MySQL query methods, alongside
    SQLAlchemy builder functions."""
    @property
    @abstractmethod
    def _connection(self) -> _MySQLQueryableProtocol: ...

    async def fetch_one(
        self,
        query: str,
        values: MySQLValues | None = None,
    ) -> MySQLRow | None:
        res = await self._connection.fetch_one(query, values)  # type: ignore
        return res._mapping if res is not None else None

    async def fetch_all(
        self,
        query: str,
        values: MySQLValues | None = None,
    ) -> list[MySQLRow]:
        res = await self._connection.fetch_all(query, values)  # type: ignore
        return [res._mapping for res in res]

    async def fetch_val(
        self,
        query: str,
        values: MySQLValues | None = None,
    ) -> Any:
        res = await self._connection.fetch_val(query, values)  # type: ignore
        return res

    async def execute(self, query: str, values: MySQLValues | None = None) -> Any:
        return await self._connection.execute(query, values)  # type: ignore

    def iterate(
        self,
        query: str,
        values: MySQLValues | None = None,
    ) -> AsyncGenerator[MySQLRow, None]:
        return self._connection.iterate(query, values)  # type: ignore
    
    # SQLAlchemy builder functions
    def select[T: BaseModel](self, model: type[T]) -> _SelectWrapper[T]:
        return _SelectWrapper(model, self._connection)
    
    def insert[T: BaseModel](self, model: type[T]) -> _InsertWrapper[T]:
        return _InsertWrapper(model, self._connection)
    
    def update[T: BaseModel](self, model: type[T]) -> _UpdateWrapper[T]:
        return _UpdateWrapper(model, self._connection)
    
    def delete[T: BaseModel](self, model: type[T]) -> _DeleteWrapper[T]:
        return _DeleteWrapper(model, self._connection)


class MySQLService(ImplementsQueryableConnection):
    def __init__(self, database_url: DatabaseURL) -> None:
        self._pool = Database(database_url)

    @property
    @override
    def _connection(self) -> _MySQLQueryableProtocol:
        return self._pool

    async def connect(self) -> None:
        await self._pool.connect()

    async def disconnect(self) -> None:
        await self._pool.disconnect()

    def transaction(self) -> MySQLTransaction:
        return MySQLTransaction(self._pool)


class MySQLTransaction(ImplementsQueryableConnection):
    """A wrapper around a transaction that implements the same interface as
    `MySQLService`."""

    def __init__(self, backend_pool: Database) -> None:
        self._backend_pool: Database = backend_pool
        self._current_connection: Connection | None = None
        self._transaction: Transaction | None = None

    async def __aenter__(self) -> MySQLTransaction:
        self._current_connection = await self._backend_pool.connection().__aenter__()
        self._transaction = await self._current_connection.transaction().__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        # This handles rollback on exception using `args`.
        if self._transaction is not None:
            await self._transaction.__aexit__(*args)

        if self._current_connection is not None:
            await self._current_connection.__aexit__(*args)

    @property
    @override
    def _connection(self) -> _MySQLQueryableProtocol:
        #assert self._current_connection is not None
        return self._current_connection # type: ignore
