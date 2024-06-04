# Made solely because the name `AsyncClient` annoyed me.
from __future__ import annotations

from meilisearch_python_sdk import AsyncClient


class MeiliSearchClient(AsyncClient):
    """An asynchronous MeiliSearch client."""

    ...
