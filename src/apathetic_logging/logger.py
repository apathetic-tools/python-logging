# src/apathetic_logging/logger.py
"""Logger class for Apathetic Logging."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, TextIO, cast

from .constants import (
    ApatheticLogging_Priv_Constants,  # pyright: ignore[reportPrivateUsage]
)
from .dual_stream_handler import (
    ApatheticLogging_Priv_DualStreamHandler,  # pyright: ignore[reportPrivateUsage]
)
from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)
from .safe_trace import (
    ApatheticLogging_Priv_SafeTrace,  # pyright: ignore[reportPrivateUsage]
)
from .tag_formatter import (
    ApatheticLogging_Priv_TagFormatter,  # pyright: ignore[reportPrivateUsage]
)


class ApatheticLogging_Priv_Logger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the Logger nested class.

    This class contains the Logger implementation as a nested class.
    When mixed into apathetic_logging, it provides apathetic_logging.Logger.
    """

    class Logger(logging.Logger):
        """Logger for all Apathetic tools."""

        enable_color: bool = False

        _logging_module_extended: bool = False

        # if stdout or stderr are redirected, we need to repoint
        _last_stream_ids: tuple[TextIO, TextIO] | None = None

        def __init__(
            self,
            name: str,
            level: int = logging.NOTSET,
            *,
            enable_color: bool | None = None,
        ) -> None:
            # it is too late to call extend_logging_module

            # now let's init our logger
            super().__init__(name, level)

            # default level resolution
            if self.level == logging.NOTSET:
                self.setLevel(self.determine_log_level())

            # detect color support once per instance
            self.enable_color = (
                enable_color
                if enable_color is not None
                else type(self).determine_color_enabled()
            )

            self.propagate = False  # avoid duplicate root logs

            # handler attachment will happen in _log() with ensure_handlers()

        def ensure_handlers(self) -> None:
            if self._last_stream_ids is None or not self.handlers:
                rebuild = True
            else:
                last_stdout, last_stderr = self._last_stream_ids
                rebuild = last_stdout is not sys.stdout or last_stderr is not sys.stderr

            if rebuild:
                self.handlers.clear()
                h = ApatheticLogging_Priv_DualStreamHandler.DualStreamHandler()
                h.setFormatter(
                    ApatheticLogging_Priv_TagFormatter.TagFormatter("%(message)s")
                )
                h.enable_color = self.enable_color
                self.addHandler(h)
                self._last_stream_ids = (sys.stdout, sys.stderr)
                ApatheticLogging_Priv_SafeTrace.safe_trace(
                    "ensure_handlers()", f"rebuilt_handlers={self.handlers}"
                )

        def _log(  # type: ignore[override]
            self, level: int, msg: str, args: tuple[Any, ...], **kwargs: Any
        ) -> None:
            ApatheticLogging_Priv_SafeTrace.safe_trace(
                "_log",
                f"logger={self.name}",
                f"id={id(self)}",
                f"level={self.level_name}",
                f"msg={msg!r}",
            )
            self.ensure_handlers()
            super()._log(level, msg, args, **kwargs)

        def setLevel(self, level: int | str) -> None:  # noqa: N802
            """Case insensitive version that resolves string level names.

            Validates that custom levels (TEST, TRACE, MINIMAL, DETAIL, SILENT) are
            not set to 0, which would cause NOTSET inheritance from root logger.
            """
            # Resolve string to integer if needed
            if isinstance(level, str):
                level_str = level.upper()
                # Handle custom level names (TEST, TRACE, MINIMAL, DETAIL, SILENT)
                # directly
                if level_str == "TEST":
                    level = ApatheticLogging_Priv_Constants.TEST_LEVEL
                elif level_str == "TRACE":
                    level = ApatheticLogging_Priv_Constants.TRACE_LEVEL
                elif level_str == "DETAIL":
                    level = ApatheticLogging_Priv_Constants.DETAIL_LEVEL
                elif level_str == "MINIMAL":
                    level = ApatheticLogging_Priv_Constants.MINIMAL_LEVEL
                elif level_str == "SILENT":
                    level = ApatheticLogging_Priv_Constants.SILENT_LEVEL
                else:
                    # Try to resolve via logging module (for standard levels)
                    resolved = self.resolve_level_name(level_str)
                    # Fall back to standard logging level names if not resolved
                    level = resolved if resolved is not None else level_str

            # Validate any level <= 0 (prevents NOTSET inheritance)
            # Built-in levels (DEBUG=10, INFO=20, etc.) are all > 0, so they pass
            # _validate_level_positive() will raise if level <= 0
            if isinstance(level, int):
                level_name = logging.getLevelName(level) or str(level)
                self._validate_level_positive(level, level_name)

            super().setLevel(level)

        @classmethod
        def determine_color_enabled(cls) -> bool:
            """Return True if colored output should be enabled."""
            # Respect explicit overrides
            if "NO_COLOR" in os.environ:
                return False
            if os.getenv("FORCE_COLOR", "").lower() in {"1", "true", "yes"}:
                return True

            # Auto-detect: use color if output is a TTY
            return sys.stdout.isatty()

        @staticmethod
        def _validate_level_positive(level: int, level_name: str | None = None) -> None:
            """Validate that a level value is positive (> 0).

            Custom levels with values <= 0 will inherit from the root logger,
            causing NOTSET inheritance issues.

            Args:
                level: The numeric level value to validate
                level_name: Optional name for the level (for error messages).
                    If None, will attempt to get from logging.getLevelName()

            Raises:
                ValueError: If level <= 0

            Example:
                >>> Logger._validate_level_positive(5, "TRACE")
                >>> Logger._validate_level_positive(0, "TEST")
                ValueError: Level 'TEST' has value 0...
            """
            if level <= 0:
                if level_name is None:
                    level_name = logging.getLevelName(level) or str(level)
                msg = (
                    f"Level '{level_name}' has value {level}, "
                    "which is <= 0. This causes NOTSET inheritance from root logger. "
                    "Levels must be > 0."
                )
                raise ValueError(msg)

        @staticmethod
        def addLevelName(level: int, level_name: str) -> None:  # noqa: N802
            """Safely add a custom logging level name with validation.

            This is a wrapper around logging.addLevelName() that validates the level
            value to prevent NOTSET inheritance issues. Custom levels with values <= 0
            will inherit from the root logger, causing unexpected behavior.

            Also sets logging.<LEVEL_NAME> attribute for convenience, matching the
            pattern of built-in levels (logging.DEBUG, logging.INFO, etc.).

            Args:
                level: The numeric level value (must be > 0 for custom levels)
                level_name: The name to associate with this level

            Raises:
                ValueError: If level <= 0 (which would cause NOTSET inheritance)
                ValueError: If logging.<LEVEL_NAME> already exists with an invalid value
                    (not a positive integer, or different from the provided level)

            Example:
                >>> Logger.addLevelName(5, "TRACE")
                >>> # Now logging.TRACE = 5 (convenience attribute)
                >>> # logging.addLevelName(5, "TRACE")  # Equivalent, but unsafe
            """
            # Validate level is positive
            ApatheticLogging_Priv_Logger.Logger._validate_level_positive(  # noqa: SLF001
                level, level_name
            )

            # Check if attribute already exists and validate it
            existing_value = getattr(logging, level_name, None)
            if existing_value is not None:
                # If it exists, it must be a valid level value (positive integer)
                if not isinstance(existing_value, int):
                    msg = (
                        f"Cannot set logging.{level_name}: attribute already exists "
                        f"with non-integer value {existing_value!r}. "
                        "Level attributes must be integers."
                    )
                    raise ValueError(msg)
                # Validate existing value is positive
                ApatheticLogging_Priv_Logger.Logger._validate_level_positive(  # noqa: SLF001
                    existing_value, level_name
                )
                if existing_value != level:
                    msg = (
                        f"Cannot set logging.{level_name}: attribute already exists "
                        f"with different value {existing_value} "
                        f"(trying to set {level}). "
                        "Level attributes must match the level value."
                    )
                    raise ValueError(msg)
                # If it exists and matches, we can proceed (idempotent)

            logging.addLevelName(level, level_name)
            # Set convenience attribute matching built-in levels (logging.DEBUG, etc.)
            setattr(logging, level_name, level)

        @classmethod
        def extend_logging_module(cls) -> bool:
            """The return value tells you if we ran or not.
            If it is False and you're calling it via super(),
            you can likely skip your code too."""
            # Check if this specific class has already extended the module
            # (not inherited from base class)
            already_extended = getattr(cls, "_logging_module_extended", False)

            # Always set the logger class to cls, even if already extended.
            # This allows subclasses to override the logger class.
            logging.setLoggerClass(cls)

            # If already extended, skip the rest (level registration, etc.)
            if already_extended:
                return False
            cls._logging_module_extended = True

            # Sanity check: validate TAG_STYLES keys are in LEVEL_ORDER
            if __debug__:
                _tag_levels = set(ApatheticLogging_Priv_Constants.TAG_STYLES.keys())
                _known_levels = {
                    lvl.upper() for lvl in ApatheticLogging_Priv_Constants.LEVEL_ORDER
                }
                if not _tag_levels <= _known_levels:
                    _msg = "TAG_STYLES contains unknown levels"
                    raise AssertionError(_msg)

            # Register custom levels with validation
            # addLevelName() also sets logging.TEST, logging.TRACE, etc. attributes
            cls.addLevelName(ApatheticLogging_Priv_Constants.TEST_LEVEL, "TEST")
            cls.addLevelName(ApatheticLogging_Priv_Constants.TRACE_LEVEL, "TRACE")
            cls.addLevelName(ApatheticLogging_Priv_Constants.DETAIL_LEVEL, "DETAIL")
            cls.addLevelName(ApatheticLogging_Priv_Constants.MINIMAL_LEVEL, "MINIMAL")
            cls.addLevelName(ApatheticLogging_Priv_Constants.SILENT_LEVEL, "SILENT")

            return True

        def determine_log_level(
            self,
            *,
            args: argparse.Namespace | None = None,
            root_log_level: str | None = None,
        ) -> str:
            """Resolve log level from CLI → env → root config → default."""
            args_level = getattr(args, "log_level", None)
            if args_level is not None:
                # cast_hint would cause circular dependency
                return cast("str", args_level).upper()

            # Check registered environment variables, or fall back to "LOG_LEVEL"
            # Access registry via namespace class MRO to ensure correct resolution
            # in both installed and stitched builds
            namespace_module = sys.modules.get("apathetic_logging")
            if namespace_module is not None:
                namespace_class = getattr(namespace_module, "apathetic_logging", None)
                if namespace_class is not None:
                    # Use namespace class MRO to access registry
                    # (handles shadowed attributes correctly)
                    registered_env_vars = getattr(
                        namespace_class,
                        "registered_priv_log_level_env_vars",
                        None,
                    )
                    registered_default = getattr(
                        namespace_class,
                        "registered_priv_default_log_level",
                        None,
                    )
                else:
                    # Fallback to direct registry access
                    registry_cls = ApatheticLogging_Priv_Registry
                    registered_env_vars = (
                        registry_cls.registered_priv_log_level_env_vars
                    )
                    registered_default = registry_cls.registered_priv_default_log_level
            else:
                # Fallback to direct registry access
                registered_env_vars = (
                    ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars
                )
                registered_default = (
                    ApatheticLogging_Priv_Registry.registered_priv_default_log_level
                )

            env_vars_to_check = (
                registered_env_vars
                or ApatheticLogging_Priv_Constants.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
            )
            for env_var in env_vars_to_check:
                env_log_level = os.getenv(env_var)
                if env_log_level:
                    return env_log_level.upper()

            if root_log_level:
                return root_log_level.upper()

            # Use registered default, or fall back to module default
            default_level: str = (
                registered_default
                or ApatheticLogging_Priv_Constants.DEFAULT_APATHETIC_LOG_LEVEL
            )
            return default_level.upper()

        @property
        def level_name(self) -> str:
            """Return the current effective level name
            (see also: logging.getLevelName)."""
            return logging.getLevelName(self.getEffectiveLevel())

        def error_if_not_debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
            """Logs an exception with the real traceback starting from the caller.
            Only shows full traceback if debug/trace is enabled."""
            exc_info = kwargs.pop("exc_info", True)
            stacklevel = kwargs.pop("stacklevel", 2)  # skip helper frame
            if self.isEnabledFor(logging.DEBUG):
                self.exception(msg, *args, exc_info=exc_info, stacklevel=stacklevel)
            else:
                self.error(msg, *args)

        def critical_if_not_debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
            """Logs an exception with the real traceback starting from the caller.
            Only shows full traceback if debug/trace is enabled."""
            exc_info = kwargs.pop("exc_info", True)
            stacklevel = kwargs.pop("stacklevel", 2)  # skip helper frame
            if self.isEnabledFor(logging.DEBUG):
                self.exception(msg, *args, exc_info=exc_info, stacklevel=stacklevel)
            else:
                self.critical(msg, *args)

        def colorize(
            self, text: str, color: str, *, enable_color: bool | None = None
        ) -> str:
            if enable_color is None:
                enable_color = self.enable_color
            return (
                f"{color}{text}{ApatheticLogging_Priv_Constants.ANSIColors.RESET}"
                if enable_color
                else text
            )

        def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
            if self.isEnabledFor(ApatheticLogging_Priv_Constants.TRACE_LEVEL):
                self._log(
                    ApatheticLogging_Priv_Constants.TRACE_LEVEL, msg, args, **kwargs
                )

        def detail(self, msg: str, *args: Any, **kwargs: Any) -> None:
            """Log a detail-level message (more detailed than INFO)."""
            if self.isEnabledFor(ApatheticLogging_Priv_Constants.DETAIL_LEVEL):
                self._log(
                    ApatheticLogging_Priv_Constants.DETAIL_LEVEL, msg, args, **kwargs
                )

        def minimal(self, msg: str, *args: Any, **kwargs: Any) -> None:
            """Log a minimal-level message (less detailed than INFO)."""
            if self.isEnabledFor(ApatheticLogging_Priv_Constants.MINIMAL_LEVEL):
                self._log(
                    ApatheticLogging_Priv_Constants.MINIMAL_LEVEL, msg, args, **kwargs
                )

        def test(self, msg: str, *args: Any, **kwargs: Any) -> None:
            """Log a test-level message (most verbose, bypasses capture)."""
            if self.isEnabledFor(ApatheticLogging_Priv_Constants.TEST_LEVEL):
                self._log(
                    ApatheticLogging_Priv_Constants.TEST_LEVEL, msg, args, **kwargs
                )

        def resolve_level_name(self, level_name: str) -> int | None:
            """logging.getLevelNamesMapping() is only introduced in 3.11"""
            return getattr(logging, level_name.upper(), None)

        def log_dynamic(
            self, level: str | int, msg: str, *args: Any, **kwargs: Any
        ) -> None:
            # Resolve level
            if isinstance(level, str):
                level_no = self.resolve_level_name(level)
                if not isinstance(level_no, int):
                    self.error("Unknown log level: %r", level)
                    return
            elif isinstance(level, int):  # pyright: ignore[reportUnnecessaryIsInstance]
                level_no = level
            else:
                self.error("Invalid log level type: %r", type(level))
                return

            self._log(level_no, msg, args, **kwargs)

        @contextmanager
        def use_level(
            self, level: str | int, *, minimum: bool = False
        ) -> Generator[None, None, None]:
            """Use a context to temporarily log with a different log-level.

            Args:
                level: Log level to use (string name or numeric value)
                minimum: If True, only set the level if it's more verbose (lower
                    numeric value) than the current level. This prevents downgrading
                    from a more verbose level (e.g., TRACE) to a less verbose one
                    (e.g., DEBUG). Defaults to False.

            Yields:
                None: Context manager yields control to the with block
            """
            prev_level = self.level

            # Resolve level
            if isinstance(level, str):
                level_no = self.resolve_level_name(level)
                if not isinstance(level_no, int):
                    self.error("Unknown log level: %r", level)
                    # Yield control anyway so the 'with' block doesn't explode
                    yield
                    return
            elif isinstance(level, int):  # pyright: ignore[reportUnnecessaryIsInstance]
                level_no = level
            else:
                self.error("Invalid log level type: %r", type(level))
                yield
                return

            # Apply new level (only if more verbose when minimum=True)
            if minimum:
                # Only set if requested level is more verbose
                # (lower number) than current
                if level_no < prev_level:
                    self.setLevel(level_no)
                # Otherwise keep current level (don't downgrade)
            else:
                self.setLevel(level_no)

            try:
                yield
            finally:
                self.setLevel(prev_level)
