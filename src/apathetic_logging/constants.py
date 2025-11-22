# src/apathetic_logging/constants.py
"""Constants for Apathetic Logging."""

from __future__ import annotations

import logging
import os
from typing import ClassVar


class ApatheticLogging_Internal_Constants:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Constants for apathetic logging functionality.

    This class contains all constant values used by apathetic_logging.
    It's kept separate for organizational purposes.
    """

    DEFAULT_APATHETIC_LOG_LEVEL: str = "detail"
    """Default log level when no other source is found."""

    DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS: ClassVar[list[str]] = ["LOG_LEVEL"]
    """Default environment variable names to check for log level."""

    SAFE_TRACE_ENABLED: bool = os.getenv("SAFE_TRACE", "").lower() in {
        "1",
        "true",
        "yes",
    }
    """Enable safe trace diagnostics (controlled by SAFE_TRACE env var)."""

    NOTSET_LEVEL: int = logging.NOTSET
    """NOTSET level (0) - logger inherits level from parent."""

    # levels must be careful not to equal 0 to avoid NOTSET
    TEST_LEVEL: int = logging.DEBUG - 8
    """Most verbose level, bypasses capture."""

    TRACE_LEVEL: int = logging.DEBUG - 5
    """More verbose than DEBUG."""

    DETAIL_LEVEL: int = logging.INFO - 5
    """More detailed than INFO."""

    MINIMAL_LEVEL: int = logging.INFO + 5
    """Less detailed than INFO."""

    SILENT_LEVEL: int = logging.CRITICAL + 1
    """Disables all logging (one above the highest builtin level)."""

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
    """Ordered list of log level names from most to least verbose."""

    class ANSIColors:
        """A selection of ANSI color code constants.

        For a comprehensive reference on ANSI escape codes and color support,
        see: https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
        """

        RESET: str = "\033[0m"
        """Reset ANSI color codes."""

        CYAN: str = "\033[36m"
        """Cyan ANSI color code."""

        YELLOW: str = "\033[93m"  # or \033[33m
        """Yellow ANSI color code."""

        RED: str = "\033[91m"  # or \033[31m # or background \033[41m
        """Red ANSI color code."""

        GREEN: str = "\033[92m"  # or \033[32m
        """Green ANSI color code."""

        GRAY: str = "\033[90m"
        """Gray ANSI color code."""

    TAG_STYLES: ClassVar[dict[str, tuple[str, str]]] = {
        "TEST": (ANSIColors.GRAY, "[TEST]"),
        "TRACE": (ANSIColors.GRAY, "[TRACE]"),
        "DEBUG": (ANSIColors.CYAN, "[DEBUG]"),
        "WARNING": ("", "⚠️ "),
        "ERROR": ("", "❌ "),
        "CRITICAL": ("", "💥 "),
    }
    """Mapping of level names to (color_code, tag_text) tuples."""

    MIN_PYTHON_VERSION: tuple[int, int] = (3, 10)
    """Minimum supported Python version (major, minor)."""

    DEFAULT_PROPAGATE: bool = False
    """Default propagate setting for loggers.

    When False, loggers do not propagate messages to parent loggers,
    avoiding duplicate root logs.
    """
