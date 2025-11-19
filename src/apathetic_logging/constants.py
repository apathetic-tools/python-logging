# src/apathetic_logging/constants.py
"""Constants for Apathetic Logging."""

from __future__ import annotations

import logging
import os
from typing import ClassVar


class ApatheticLogging_Priv_Constants:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Constants for apathetic logging functionality.

    This class contains all constant values used by apathetic_logging.
    It's kept separate for organizational purposes.
    """

    DEFAULT_APATHETIC_LOG_LEVEL: str = "info"
    DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS: ClassVar[list[str]] = ["LOG_LEVEL"]

    # Flag for quick runtime enable/disable
    SAFE_TRACE_ENABLED: bool = os.getenv("SAFE_TRACE", "").lower() in {
        "1",
        "true",
        "yes",
    }

    # Logger levels
    # most verbose, bypasses capture (2, not 0 to avoid NOTSET)
    TEST_LEVEL: int = logging.DEBUG - 8
    TRACE_LEVEL: int = logging.DEBUG - 5
    # DEBUG      - builtin # verbose
    DETAIL_LEVEL: int = logging.INFO - 5
    # INFO       - builtin
    MINIMAL_LEVEL: int = logging.INFO + 5
    # WARNING    - builtin
    # ERROR      - builtin
    # CRITICAL   - builtin # quiet mode
    SILENT_LEVEL: int = logging.CRITICAL + 1  # one above the highest builtin level

    LEVEL_ORDER: ClassVar[list[str]] = [
        "test",  # most verbose, bypasses capture for debugging tests
        "trace",
        "debug",
        "detail",
        "info",
        "minimal",
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
        "TEST": (ANSIColors.GRAY, "[TEST]"),
        "TRACE": (ANSIColors.GRAY, "[TRACE]"),
        "DEBUG": (ANSIColors.CYAN, "[DEBUG]"),
        "DETAIL": (ANSIColors.CYAN, "[DETAIL]"),
        "MINIMAL": (ANSIColors.GREEN, "[MINIMAL]"),
        "WARNING": ("", "⚠️ "),
        "ERROR": ("", "❌ "),
        "CRITICAL": ("", "💥 "),
    }
