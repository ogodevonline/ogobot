"""Logging configuration with loguru"""

import sys

from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """Setup loguru logging"""
    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "<level>{level: <8}</level> | <cyan>{name}</cyan>:"
            "<cyan>{function}</cyan> - <level>{message}</level>"
        ),
        level=level,
    )
    logger.add(
        "logs/seac.log",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
        ),
        level=level,
        rotation="500 MB",
    )
