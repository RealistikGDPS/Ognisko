from __future__ import annotations

import databases
import httpx
from redis import asyncio as aioredis

from realistikgdps.config import config

http = httpx.AsyncClient()
database = databases.Database(
    databases.DatabaseURL(
        "mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
            username=config.sql_user,
            password=config.sql_pass,
            host=config.sql_host,
            port=config.sql_port,
            db=config.sql_db,
        ),
    ),
)
redis = aioredis.from_url(
    f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
)
