# src/apathetic_logging/logger_lib_snake.py
"""Snake case convenience methods for apathetic logging.Logger.

See https://docs.python.org/3/library/logging.html#logging.Logger for the
complete list of standard library Logger methods that are extended by this class.

Docstrings are adapted from the standard library logging.Logger code,
licensed under the Python Software Foundation License Version 2.
"""

from __future__ import annotations

import argparse
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from .logger import (
    ApatheticLogging_Internal_LoggerCore,
)


class ApatheticLogging_Internal_LibLoggerSnakeCase:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides snake_case convenience methods for apathetic Logger.

    This class contains snake_case wrapper methods for apathetic logging library
    Logger methods that use camelCase naming. These wrappers provide a more
    Pythonic interface that follows PEP 8 naming conventions while maintaining
    full compatibility with the underlying apathetic Logger methods.

    When mixed into Logger, it provides snake_case alternatives to apathetic
    Logger methods (e.g., `ensureHandlers` -> `ensure_handlers`,
    `determineLogLevel` -> `determine_log_level`, `addLevelName` ->
    `add_level_name`).
    """

    # --- Handler Management Methods ---

    def ensure_handlers(self, *args: Any, **kwargs: Any) -> None:
        """Ensure handlers are configured for this logger.

        Wrapper for Logger.ensureHandlers with snake_case naming.
        """
        self.ensureHandlers(*args, **kwargs)  # type: ignore[attr-defined]

    # --- Level Management Methods ---

    @staticmethod
    def add_level_name(level: int, level_name: str, *args: Any, **kwargs: Any) -> None:
        """Safely add a custom logging level name with validation.

        This is a wrapper around logging.addLevelName() that validates the level
        value to prevent NOTSET inheritance issues. Custom levels with values <= 0
        will inherit from the root logger, causing unexpected behavior.

        Also sets logging.<LEVEL_NAME> attribute for convenience, matching the
        pattern of built-in levels (logging.DEBUG, logging.INFO, etc.).

        Args:
            level: The numeric level value (must be > 0 for custom levels)
            level_name: The name to associate with this level
            *args: Additional positional arguments (for future-proofing)
            **kwargs: Additional keyword arguments (for future-proofing)

        Raises:
            ValueError: If level <= 0 (which would cause NOTSET inheritance)
            ValueError: If logging.<LEVEL_NAME> already exists with an invalid value
                (not a positive integer, or different from the provided level)

        Wrapper for Logger.addLevelName with snake_case naming.
        """
        return ApatheticLogging_Internal_LoggerCore.addLevelName(
            level, level_name, *args, **kwargs
        )

    def determine_log_level(
        self,
        *,
        args: argparse.Namespace | None = None,
        root_log_level: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Resolve log level from CLI → env → root config → default.

        Wrapper for Logger.determineLogLevel with snake_case naming.
        """
        return self.determineLogLevel(  # type: ignore[attr-defined,no-any-return]
            args=args, root_log_level=root_log_level, **kwargs
        )

    def resolve_level_name(
        self, level_name: str, *args: Any, **kwargs: Any
    ) -> int | None:
        """Resolve a level name to its numeric value.

        logging.getLevelNamesMapping() is only introduced in Python 3.11, so
        this method provides compatibility for earlier versions.

        Wrapper for Logger.resolveLevelName with snake_case naming.
        """
        return self.resolveLevelName(level_name, *args, **kwargs)  # type: ignore[attr-defined,no-any-return]

    # --- Logging Methods ---

    def error_if_not_debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an exception with the real traceback starting from the caller.

        Only shows full traceback if debug/trace is enabled.

        Wrapper for Logger.errorIfNotDebug with snake_case naming.
        """
        # Increment stacklevel to account for this wrapper frame
        if "stacklevel" in kwargs:
            kwargs["stacklevel"] = kwargs["stacklevel"] + 1
        else:
            kwargs["stacklevel"] = (
                ApatheticLogging_Internal_LoggerCore.DEFAULT_STACKLEVEL + 1
            )
        self.errorIfNotDebug(msg, *args, **kwargs)  # type: ignore[attr-defined]

    def critical_if_not_debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an exception with the real traceback starting from the caller.

        Only shows full traceback if debug/trace is enabled.

        Wrapper for Logger.criticalIfNotDebug with snake_case naming.
        """
        # Increment stacklevel to account for this wrapper frame
        if "stacklevel" in kwargs:
            kwargs["stacklevel"] = kwargs["stacklevel"] + 1
        else:
            kwargs["stacklevel"] = (
                ApatheticLogging_Internal_LoggerCore.DEFAULT_STACKLEVEL + 1
            )
        self.criticalIfNotDebug(msg, *args, **kwargs)  # type: ignore[attr-defined]

    def log_dynamic(
        self, level: str | int, msg: str, *args: Any, **kwargs: Any
    ) -> None:
        """Log a message with a dynamically resolved log level.

        Wrapper for Logger.logDynamic with snake_case naming.
        """
        self.logDynamic(level, msg, *args, **kwargs)  # type: ignore[attr-defined]

    # --- Context Manager Methods ---

    @contextmanager
    def use_level(
        self, level: str | int, *, minimum: bool = False, **kwargs: Any
    ) -> Generator[None, None, None]:
        """Use a context to temporarily log with a different log-level.

        Args:
            level: Log level to use (string name or numeric value)
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current level. This prevents downgrading
                from a more verbose level (e.g., TRACE) to a less verbose one
                (e.g., DEBUG). Defaults to False.
            **kwargs: Additional keyword arguments (for future-proofing)

        Yields:
            None: Context manager yields control to the with block

        Wrapper for Logger.useLevel with snake_case naming.
        """
        with self.useLevel(level, minimum=minimum, **kwargs):  # type: ignore[attr-defined]
            yield
