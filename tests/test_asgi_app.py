import pytest
from fastapi import FastAPI

from ognisko.api import init_api


@pytest.fixture
def app() -> FastAPI:
    return init_api()


# Context requirements.
def test_sql_exists(app: FastAPI) -> None:
    assert app.state.mysql is not None


def test_redis_exists(app: FastAPI) -> None:
    assert app.state.redis is not None


def test_meili_exists(app: FastAPI) -> None:
    assert app.state.meili is not None


def test_http_exists(app: FastAPI) -> None:
    assert app.state.http is not None


def test_user_cache_exists(app: FastAPI) -> None:
    assert app.state.user_cache is not None


def test_password_cache_exists(app: FastAPI) -> None:
    assert app.state.password_cache is not None
