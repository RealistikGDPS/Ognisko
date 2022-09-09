from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from dataclasses import field
from json import dump
from json import load
from typing import Any


@dataclass
class Config:
    http_port: int = 8922
    http_url_prefix: str = "/gdpsdatabase"
    http_host: str = "127.0.0.1"
    sql_host: str = "localhost"
    sql_user: str = "root"
    sql_db: str = "rosu"
    sql_pass: str = "password"
    data_dir: str = ".data"
    srv_name: str = "RealistikGDPS"


def read_config_json() -> dict[str, Any]:
    with open("config.json") as f:
        return load(f)


def write_config(config: Config):
    with open("config.json", "w") as f:
        dump(config.__dict__, f, indent=4)


def load_config() -> Config:
    """Loads the config from the file, handling config updates.

    Note:
        Raises `SystemExit` on config update.
    """

    config_dict = {}

    if os.path.exists("config.json"):
        config_dict = read_config_json()

    # Compare config json attributes with config class attributes
    missing_keys = [key for key in Config.__annotations__ if key not in config_dict]

    # Remove extra fields
    for key in tuple(
        config_dict,
    ):  # Tuple cast is necessary to create a copy of the keys.
        if key not in Config.__annotations__:
            del config_dict[key]

    # Create config regardless, populating it with missing keys and removing
    # unnecessary keys.
    config = Config(**config_dict)

    if missing_keys:
        logging.info(f"Your config has been updated with {len(missing_keys)} new keys.")
        logging.debug("Missing keys: " + ", ".join(missing_keys))
        write_config(config)
        raise SystemExit(0)

    return config


config = load_config()
