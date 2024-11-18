from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def read_comma_separated_list(value: str) -> list[str]:
    return [x.strip() for x in value.split(",")]


def read_boolean(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")


OGNISKO_HTTP_PORT = int(os.environ["OGNISKO_HTTP_PORT"])
OGNISKO_HTTP_HOST = os.environ["OGNISKO_HTTP_HOST"]
OGNISKO_HTTP_URL_PREFIX = os.environ["OGNISKO_HTTP_URL_PREFIX"]
OGNISKO_PRODUCT_NAME = os.environ["OGNISKO_PRODUCT_NAME"]
OGNISKO_USER_COMMAND_PREFIX = os.environ["OGNISKO_USER_COMMAND_PREFIX"]
OGNISKO_OFFICIAL_SERVER_MIRROR_URL = os.environ["OGNISKO_OFFICIAL_SERVER_MIRROR_URL"]
OGNISKO_LOG_LEVEL = os.environ["OGNISKO_LOG_LEVEL"]
OGNISKO_INTERNAL_DATA_DIRECTORY = os.environ["OGNISKO_INTERNAL_DATA_DIRECTORY"]
OGNISKO_USE_USER_AGENT_GUARD = read_boolean(os.environ["OGNISKO_USE_USER_AGENT_GUARD"])

MYSQL_HOST = os.environ["MYSQL_HOST"]  # Non-standard
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DATABASE = os.environ["MYSQL_DATABASE"]
MYSQL_TCP_PORT = int(os.environ["MYSQL_TCP_PORT"])

REDIS_HOST = os.environ["REDIS_HOST"]  # Non-standard
REDIS_PORT = int(os.environ["REDIS_PORT"])  # Non-standard
REDIS_DATABASE = int(os.environ["REDIS_DB"])  # Non-standard

MEILI_HOST = os.environ["MEILI_HOST"]  # Non-standard
MEILI_PORT = int(os.environ["MEILI_PORT"])  # Non-standard
MEILI_MASTER_KEY = os.environ["MEILI_MASTER_KEY"]

# These will be temp disabled.
S3_ENABLED = False
# S3_ENABLED = read_boolean(os.environ["S3_ENABLED"])
# S3_BUCKET = os.environ["S3_BUCKET"]
# S3_REGION = os.environ["S3_REGION"]
# S3_ENDPOINT = os.environ["S3_ENDPOINT"]
# S3_ACCESS_KEY = os.environ["S3_ACCESS_KEY"]
# S3_SECRET_KEY = os.environ["S3_SECRET_KEY"]
