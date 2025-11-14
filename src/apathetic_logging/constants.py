# src/apathetic_logging/constants.py
"""Constants for Apathetic Logging."""

from __future__ import annotations

import logging
import os
from typing import ClassVar


class ApatheticLogging_Priv_Constants:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Constants for apathetic logging functionality.

    This class contains all constant values used by ApatheticLogging.
    It's kept separate for organizational purposes.
    """

    DEFAULT_APATHETIC_LOG_LEVEL: str = "info"
    DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS: ClassVar[list[str]] = ["LOG_LEVEL"]

    # Flag for quick runtime enable/disable
    TEST_TRACE_ENABLED: bool = os.getenv("TEST_TRACE", "").lower() in {
        "1",
        "true",
        "yes",
    }

    # Logger levels
    TRACE_LEVEL: int = logging.DEBUG - 5
    # DEBUG      - builtin # verbose
    # INFO       - builtin
    # WARNING    - builtin
    # ERROR      - builtin
    # CRITICAL   - builtin # quiet mode
    SILENT_LEVEL: int = logging.CRITICAL + 1  # one above the highest builtin level

    LEVEL_ORDER: ClassVar[list[str]] = [
        "trace",
        "debug",
        "info",
        "warning",
        "error",
        "critical",
        "silent",  # disables all logging
    ]

    class ANSIColors:
        """ANSI color code constants."""

        RESET: str = "\033[0m"
        CYAN: str = "\033[36m"
        YELLOW: str = "\033[93m"  # or \033[33m
        RED: str = "\033[91m"  # or \033[31m # or background \033[41m
        GREEN: str = "\033[92m"  # or \033[32m
        GRAY: str = "\033[90m"

    TAG_STYLES: ClassVar[dict[str, tuple[str, str]]] = {
        "TRACE": (ANSIColors.GRAY, "[TRACE]"),
        "DEBUG": (ANSIColors.CYAN, "[DEBUG]"),
        "WARNING": ("", "⚠️ "),
        "ERROR": ("", "❌ "),
        "CRITICAL": ("", "💥 "),
    }
