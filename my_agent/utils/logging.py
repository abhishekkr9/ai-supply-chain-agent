"""Centralized logging configuration for the logistics agent."""
import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Returns a logger scoped to the given module name.

    Log level is controlled by the LOG_LEVEL env var (default: INFO).
    Format: timestamp | level | logger | message
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, level, logging.INFO))

        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.propagate = False

    return logger
