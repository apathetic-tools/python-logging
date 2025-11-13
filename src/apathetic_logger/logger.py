"""Logger class for Apathetic Logger."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, TextIO, cast


# --- globals ---------------------------------------------------------------

# Note: _registered_log_level_env_vars and _registered_default_log_level
# are defined in namespace.py and accessed via _get_namespace_module() at runtime
# to avoid circular import issues


def _get_namespace_module() -> Any:
    """Get the namespace module at runtime.

    This avoids circular import issues by accessing the namespace
    through the module system after it's been created.
    """
    # Access through sys.modules to avoid circular import
    namespace_module = sys.modules.get("apathetic_logger.namespace")
    if namespace_module is None:
        # Fallback: import if not yet loaded

        namespace_module = sys.modules["apathetic_logger.namespace"]
    return namespace_module


def _get_namespace() -> Any:
    """Get the ApatheticLogger namespace at runtime."""
    return _get_namespace_module().ApatheticLogger


class _ApatheticLogger_Logger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the Logger nested class.

    This class contains the Logger implementation as a nested class.
    When mixed into ApatheticLogger, it provides ApatheticLogger.Logger.
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
                ns = _get_namespace()
                h = ns.DualStreamHandler()
                h.setFormatter(ns.TagFormatter("%(message)s"))
                h.enable_color = self.enable_color
                self.addHandler(h)
                self._last_stream_ids = (sys.stdout, sys.stderr)
                ns.TEST_TRACE("ensure_handlers()", f"rebuilt_handlers={self.handlers}")

        def _log(  # type: ignore[override]
            self, level: int, msg: str, args: tuple[Any, ...], **kwargs: Any
        ) -> None:
            ns = _get_namespace()
            ns.TEST_TRACE(
                "_log",
                f"logger={self.name}",
                f"id={id(self)}",
                f"level={self.level_name}",
                f"msg={msg!r}",
            )
            self.ensure_handlers()
            super()._log(level, msg, args, **kwargs)

        def setLevel(self, level: int | str) -> None:  # noqa: N802
            """Case insensitive version that handles custom level names."""
            if isinstance(level, str):
                level_upper = level.upper()
                # Handle custom level names (TRACE, SILENT) directly
                ns = _get_namespace()
                if level_upper == "TRACE":
                    level = ns.TRACE_LEVEL
                elif level_upper == "SILENT":
                    level = ns.SILENT_LEVEL
                else:
                    # Try to resolve via logging module (for standard levels)
                    resolved = self.resolve_level_name(level_upper)
                    # Fall back to standard logging level names if not resolved
                    level = resolved if resolved is not None else level_upper
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

        @classmethod
        def extend_logging_module(cls) -> bool:
            """The return value tells you if we ran or not.
            If it is False and you're calling it via super(),
            you can likely skip your code too."""
            # ensure module-level logging setup runs only once
            if cls._logging_module_extended:
                return False
            cls._logging_module_extended = True

            ns = _get_namespace()

            # Sanity check: validate TAG_STYLES keys are in LEVEL_ORDER
            if __debug__:
                _tag_levels = set(ns.TAG_STYLES.keys())
                _known_levels = {lvl.upper() for lvl in ns.LEVEL_ORDER}
                if not _tag_levels <= _known_levels:
                    _msg = "TAG_STYLES contains unknown levels"
                    raise AssertionError(_msg)

            logging.setLoggerClass(cls)

            logging.addLevelName(ns.TRACE_LEVEL, "TRACE")
            logging.addLevelName(ns.SILENT_LEVEL, "SILENT")

            logging.TRACE = ns.TRACE_LEVEL  # type: ignore[attr-defined]
            logging.SILENT = ns.SILENT_LEVEL  # type: ignore[attr-defined]

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
            ns = _get_namespace()
            namespace_module = _get_namespace_module()
            registered_env_vars = getattr(
                namespace_module, "_registered_log_level_env_vars", None
            )
            env_vars_to_check = (
                registered_env_vars or ns.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
            )
            for env_var in env_vars_to_check:
                env_log_level = os.getenv(env_var)
                if env_log_level:
                    return env_log_level.upper()

            if root_log_level:
                return root_log_level.upper()

            # Use registered default, or fall back to module default
            namespace_module = _get_namespace_module()
            registered_default = getattr(
                namespace_module, "_registered_default_log_level", None
            )
            default_level: str = registered_default or ns.DEFAULT_APATHETIC_LOG_LEVEL
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
            ns = _get_namespace()
            return f"{color}{text}{ns.ANSIColors.RESET}" if enable_color else text

        def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
            ns = _get_namespace()
            if self.isEnabledFor(ns.TRACE_LEVEL):
                self._log(ns.TRACE_LEVEL, msg, args, **kwargs)

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
