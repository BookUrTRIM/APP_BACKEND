import logging
import logging.config
import os


def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
        "loggers": {
            # SQLAlchemy génère beaucoup de logs en DEBUG — on les filtre sauf en dev
            "sqlalchemy.engine": {
                "level": "WARNING" if log_level != "DEBUG" else "INFO",
                "propagate": True,
            },
            "sqlalchemy.pool": {
                "level": "WARNING",
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(config)
