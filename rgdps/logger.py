from __future__ import annotations

import logging.config

from logzio.handler import ExtraFieldsLogFilter


# TODO: Look into more customisability.
_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "logzioFormat": {"format": '{"additional_field": "value"}', "validate": False},
    },
    "handlers": {
        "logzio": {
            "class": "logzio.handler.LogzioHandler",
            "level": "INFO",
            "formatter": "logzioFormat",
            "token": "",
            "logzio_type": "python",
            "logs_drain_timeout": 5,
            "url": "https://listener.logz.io:8071",
        },
    },
    "loggers": {"rgdps": {"level": "DEBUG", "handlers": ["logzio"], "propagate": True}},
}


LOGGER = logging.getLogger("rgdps")


def init_basic_logging(log_level: str | int) -> None:
    logging.basicConfig(level=log_level)


def init_logzio_logging(logzio_token: str, log_level: str) -> None:
    _LOGGING_CONFIG["handlers"]["logzio"]["token"] = logzio_token
    _LOGGING_CONFIG["loggers"]["rgdps"]["level"] = log_level

    logging.config.dictConfig(_LOGGING_CONFIG)


def debug(*args, **kwargs) -> None:
    return LOGGER.debug(*args, **kwargs)


def info(*args, **kwargs) -> None:
    return LOGGER.info(*args, **kwargs)


def warning(*args, **kwargs) -> None:
    return LOGGER.warning(*args, **kwargs)


def error(*args, **kwargs) -> None:
    return LOGGER.error(*args, **kwargs)


def critical(*args, **kwargs) -> None:
    return LOGGER.critical(*args, **kwargs)
