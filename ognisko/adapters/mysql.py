from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession


#class MySQLConnection(AsyncSession):
#    pass

type MySQLConnection = AsyncSession
