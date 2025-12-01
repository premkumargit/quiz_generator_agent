
"""Shared logging setup for the quiz video agentic project."""

import logging
import os


def setup_logging(default_level: str | int = logging.INFO) -> None:
    """Configure root logging once.

    - Uses LOG_LEVEL env var if set (e.g. DEBUG, INFO, WARNING, ERROR).
    - Otherwise falls back to `default_level`.
    """
    level_name = os.getenv("LOG_LEVEL")
    if isinstance(default_level, str):
        default = getattr(logging, default_level.upper(), logging.INFO)
    else:
        default = default_level

    if level_name:
        level = getattr(logging, level_name.upper(), default)
    else:
        level = default

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )
    else:
        logging.getLogger().setLevel(level)
