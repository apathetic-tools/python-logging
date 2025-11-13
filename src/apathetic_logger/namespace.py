# src/serger/utils/utils_logs.py
"""Shared Apathetic CLI logger implementation."""

from __future__ import annotations

import builtins
import importlib
import inspect
import logging
import sys
from collections.abc import Callable
from contextlib import suppress
from typing import Any, TextIO, cast

from .constants import _ApatheticLogger_Constants  # pyright: ignore[reportPrivateUsage]
from .logger import _ApatheticLogger_Logger  # pyright: ignore[reportPrivateUsage]
from .tag_formatter import (
    _ApatheticLogger_TagFormatter,  # pyright: ignore[reportPrivateUsage]
)


# --- globals ---------------------------------------------------------------

# Registry for configurable log level settings
# These must be module-level for global state management
_registered_log_level_env_vars: list[str] | None = None
_registered_default_log_level: str | None = None
_registered_logger_name: str | None = None

# Lazy, safe import — avoids patched time modules
#   in environments like pytest or eventlet
_real_time = importlib.import_module("time")


# --- Apathetic Logger Namespace -------------------------------------------


class ApatheticLogger(  # pyright: ignore[reportPrivateUsage]
    _ApatheticLogger_Constants,
    _ApatheticLogger_Logger,
    _ApatheticLogger_TagFormatter,
):
    """Namespace for apathetic logger functionality.

    All logger functionality is accessed via this namespace class to minimize
    global namespace pollution when the library is embedded in a stitched script.

    The Logger class is provided via the _ApatheticLogger_Logger mixin.
    The TagFormatter class is provided via the _ApatheticLogger_TagFormatter mixin.
    """

    class DualStreamHandler(logging.StreamHandler):  # type: ignore[type-arg]
        """Send info/debug/trace to stdout, everything else to stderr."""

        enable_color: bool = False

        def __init__(self) -> None:
            # default to stdout, overridden per record in emit()
            super().__init__()  # pyright: ignore[reportUnknownMemberType]

        def emit(self, record: logging.LogRecord) -> None:
            level = record.levelno
            if level >= logging.WARNING:
                self.stream = sys.stderr
            else:
                self.stream = sys.stdout

            # used by TagFormatter
            record.enable_color = getattr(self, "enable_color", False)

            super().emit(record)

    # --- Static Methods ----------------------------------------------------

    @staticmethod
    def safe_log(msg: str) -> None:
        """Emergency logger that never fails."""
        stream = cast("TextIO", sys.__stderr__)
        try:
            print(msg, file=stream)
        except Exception:  # noqa: BLE001
            # As final guardrail — never crash during crash reporting
            with suppress(Exception):
                stream.write(f"[INTERNAL] {msg}\n")

    @staticmethod
    def make_test_trace(icon: str = "🧵") -> Callable[..., Any]:
        def local_trace(label: str, *args: Any) -> Any:
            return ApatheticLogger.TEST_TRACE(label, *args, icon=icon)

        return local_trace

    @staticmethod
    def TEST_TRACE(label: str, *args: Any, icon: str = "🧵") -> None:  # noqa: N802
        """Emit a synchronized, flush-safe diagnostic line.

        Args:
            label: Short identifier or context string.
            *args: Optional values to append.
            icon: Emoji prefix/suffix for easier visual scanning.

        """
        if not ApatheticLogger.TEST_TRACE_ENABLED:
            return

        ts = _real_time.monotonic()
        # builtins.print more reliable than sys.stdout.write + sys.stdout.flush
        builtins.print(
            f"{icon} [TEST TRACE {ts:.6f}] {label}",
            *args,
            file=sys.__stderr__,
            flush=True,
        )

    @staticmethod
    def _extract_top_level_package(package_name: str | None) -> str | None:
        """Extract the top-level package name from a full package path.

        Args:
            package_name: Full package name (e.g., "serger.logs")

        Returns:
            Top-level package name (e.g., "serger") or None if package_name is None
        """
        if package_name is None:
            return None
        if "." in package_name:
            return package_name.split(".", 1)[0]
        return package_name

    @staticmethod
    def register_log_level_env_vars(env_vars: list[str]) -> None:
        """Register environment variable names to check for log level.

        The environment variables will be checked in order, and the first
        non-empty value found will be used.

        Args:
            env_vars: List of environment variable names to check
                (e.g., ["SERGER_LOG_LEVEL", "LOG_LEVEL"])

        Example:
            >>> from apathetic_logger import ApatheticLogger
            >>> ApatheticLogger.register_log_level_env_vars(
            ...     ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]
            ... )
        """
        global _registered_log_level_env_vars  # noqa: PLW0603
        _registered_log_level_env_vars = env_vars
        ApatheticLogger.TEST_TRACE(
            "register_log_level_env_vars() called",
            f"env_vars={env_vars}",
        )

    @staticmethod
    def register_default_log_level(default_level: str) -> None:
        """Register the default log level to use when no other source is found.

        Args:
            default_level: Default log level name (e.g., "info", "warning")

        Example:
            >>> from apathetic_logger import ApatheticLogger
            >>> ApatheticLogger.register_default_log_level("warning")
        """
        global _registered_default_log_level  # noqa: PLW0603
        _registered_default_log_level = default_level
        ApatheticLogger.TEST_TRACE(
            "register_default_log_level() called",
            f"default_level={default_level}",
        )

    @staticmethod
    def register_logger_name(logger_name: str | None = None) -> None:
        """Register a logger name for use by get_logger().

        This allows applications to specify which logger name to use.
        The actual logger instance is stored by Python's logging module
        via logging.getLogger(), so we only need to store the name.

        If logger_name is not provided, the top-level package is automatically
        extracted from this module's __package__ attribute. For example, if
        this module is in "serger.logs", it will default to "serger".

        Args:
            logger_name: The name of the logger to retrieve (e.g., "serger").
                If None, extracts the top-level package from __package__.

        Example:
            >>> # Explicit registration
            >>> from apathetic_logger import ApatheticLogger
            >>> ApatheticLogger.register_logger_name("myapp")

            >>> # Auto-infer from __package__
            >>> ApatheticLogger.register_logger_name()
            ...     # Uses top-level package from __package__
        """
        global _registered_logger_name  # noqa: PLW0603

        auto_inferred = False
        if logger_name is None:
            # Extract top-level package from this module's __package__
            package = globals().get("__package__")
            if package:
                logger_name = ApatheticLogger._extract_top_level_package(package)
                auto_inferred = True
            if logger_name is None:
                _msg = (
                    "Cannot auto-infer logger name: __package__ is not set. "
                    "Please call register_logger_name() with an explicit logger name."
                )
                raise RuntimeError(_msg)

        _registered_logger_name = logger_name
        ApatheticLogger.TEST_TRACE(
            "register_logger_name() called",
            f"name={logger_name}",
            f"auto_inferred={auto_inferred}",
        )

    @staticmethod
    def get_logger() -> ApatheticLogger.Logger:
        """Return the registered logger instance.

        Uses Python's built-in logging registry (logging.getLogger()) to retrieve
        the logger. If no logger name has been registered, attempts to auto-infer
        the logger name from the calling module's top-level package.

        Returns:
            The logger instance from logging.getLogger()
            (as ApatheticLogger.Logger type)

        Raises:
            RuntimeError: If called before a logger name has been registered and
                auto-inference fails.

        Note:
            This function is used internally by utils_logs.py. Applications
            should use their app-specific getter (e.g., get_app_logger()) for
            better type hints.
        """
        global _registered_logger_name  # noqa: PLW0603

        if _registered_logger_name is None:
            # Try to auto-infer from the calling module's package
            frame = inspect.currentframe()
            if frame is not None:
                try:
                    # Get the calling frame (skip get_logger itself)
                    caller_frame = frame.f_back
                    if caller_frame is not None:
                        caller_module = caller_frame.f_globals.get("__package__")
                        if caller_module:
                            inferred_name = ApatheticLogger._extract_top_level_package(
                                caller_module
                            )
                            if inferred_name:
                                _registered_logger_name = inferred_name
                                ApatheticLogger.TEST_TRACE(
                                    "get_logger() auto-inferred logger name",
                                    f"name={inferred_name}",
                                    f"from_module={caller_module}",
                                )
                finally:
                    del frame

        if _registered_logger_name is None:
            _msg = (
                "Logger name not registered and could not be auto-inferred. "
                "Call register_logger_name() or ensure your app's logs "
                "module is imported."
            )
            raise RuntimeError(_msg)

        logger = logging.getLogger(_registered_logger_name)
        typed_logger = cast("ApatheticLogger.Logger", logger)
        ApatheticLogger.TEST_TRACE(
            "get_logger() called",
            f"name={typed_logger.name}",
            f"id={id(typed_logger)}",
            f"level={typed_logger.level_name}",
            f"handlers={[type(h).__name__ for h in typed_logger.handlers]}",
        )
        return typed_logger


# --- Module-level validation -----------------------------------------------

# sanity check
if __debug__:
    _tag_levels = set(ApatheticLogger.TAG_STYLES.keys())
    _known_levels = {lvl.upper() for lvl in ApatheticLogger.LEVEL_ORDER}
    if not _tag_levels <= _known_levels:
        _msg = "TAG_STYLES contains unknown levels"
        raise AssertionError(_msg)
