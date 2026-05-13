"""
logger.py
---------
Configura un logger estándar para el monitor de URLs.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Retorna un logger con formato de consola."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    return logger
