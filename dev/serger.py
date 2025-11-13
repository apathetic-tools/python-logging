#!/usr/bin/env python3
# Serger — Stitch your module into a single file.
# License: MIT-aNOAI
# Full text: https://github.com/apathetic-tools/serger/blob/main/LICENSE
# Version: 0.1.0
# Commit: unknown (local build)
# Build Date: 2025-11-13 17:58:07 UTC
# Repo: https://github.com/apathetic-tools/serger

# ruff: noqa: E402

from __future__ import annotations


"""
Serger — Stitch your module into a single file.
This single-file version is auto-generated from modular sources.
Version: 0.1.0
Commit: unknown (local build)
Built: 2025-11-13 17:58:07 UTC
"""

import argparse
import ast
import builtins
import contextlib
import graphlib
import importlib
import inspect
import json
import logging
import os
import platform
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import types
from collections import OrderedDict
from collections.abc import Callable, Generator, Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import get_close_matches
from fnmatch import fnmatchcase
from functools import lru_cache
from io import StringIO
from pathlib import Path
from types import UnionType
from typing import (
    Any,
    Literal,
    TextIO,
    TypedDict,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from typing_extensions import NotRequired


__version__ = "0.1.0"
__commit__ = "unknown (local build)"
__build_date__ = "2025-11-13 17:58:07 UTC"
__STANDALONE__ = True
__STITCH_SOURCE__ = "serger"
__package__ = "serger"


# === apathetic_logs.logs ===
# src/serger/utils/utils_logs.py
"""Shared Apathetic CLI logger implementation."""


# --- Constants ---------------------------------------------------------------

DEFAULT_APATHETIC_LOG_LEVEL: str = "info"
DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS: list[str] = ["LOG_LEVEL"]

# Flag for quick runtime enable/disable
TEST_TRACE_ENABLED = os.getenv("TEST_TRACE", "").lower() in {"1", "true", "yes"}

# Lazy, safe import — avoids patched time modules
#   in environments like pytest or eventlet
_real_time = importlib.import_module("time")

# ANSI Colors
RESET = "\033[0m"
CYAN = "\033[36m"
YELLOW = "\033[93m"  # or \033[33m
RED = "\033[91m"  # or \033[31m # or background \033[41m
GREEN = "\033[92m"  # or \033[32m
GRAY = "\033[90m"

# Logger levels
TRACE_LEVEL = logging.DEBUG - 5
# DEBUG      - builtin # verbose
# INFO       - builtin
# WARNING    - builtin
# ERROR      - builtin
# CRITICAL   - builtin # quiet mode
SILENT_LEVEL = logging.CRITICAL + 1  # one above the highest builtin level

LEVEL_ORDER = [
    "trace",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "silent",  # disables all logging
]

TAG_STYLES = {
    "TRACE": (GRAY, "[TRACE]"),
    "DEBUG": (CYAN, "[DEBUG]"),
    "WARNING": ("", "⚠️ "),
    "ERROR": ("", "❌ "),
    "CRITICAL": ("", "💥 "),
}

# sanity check
assert set(TAG_STYLES.keys()) <= {lvl.upper() for lvl in LEVEL_ORDER}, (  # noqa: S101
    "TAG_STYLES contains unknown levels"
)

# --- globals ---------------------------------------------------------------

# Registry for configurable log level settings
_registered_log_level_env_vars: list[str] | None = None
_registered_default_log_level: str | None = None


# --- Logging that bypasses streams -------------------------------------------------


def safe_log(msg: str) -> None:
    """Emergency logger that never fails."""
    stream = cast("TextIO", sys.__stderr__)
    try:
        print(msg, file=stream)
    except Exception:  # noqa: BLE001
        # As final guardrail — never crash during crash reporting
        with suppress(Exception):
            stream.write(f"[INTERNAL] {msg}\n")


# --- Logging for debugging tests -------------------------------------------------


def make_test_trace(icon: str = "🧵") -> Callable[..., Any]:
    def local_trace(label: str, *args: Any) -> Any:
        return TEST_TRACE(label, *args, icon=icon)

    return local_trace


def TEST_TRACE(label: str, *args: Any, icon: str = "🧵") -> None:  # noqa: N802
    """Emit a synchronized, flush-safe diagnostic line.

    Args:
        label: Short identifier or context string.
        *args: Optional values to append.
        icon: Emoji prefix/suffix for easier visual scanning.

    """
    if not TEST_TRACE_ENABLED:
        return

    ts = _real_time.monotonic()
    # builtins.print more reliable than sys.stdout.write + sys.stdout.flush
    builtins.print(
        f"{icon} [TEST TRACE {ts:.6f}] {label}",
        *args,
        file=sys.__stderr__,
        flush=True,
    )


# --- Apathetic logger -----------------------------------------------------


class ApatheticCLILogger(logging.Logger):
    """Logger for all Apathetic CLI tools."""

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
            rebuild = (last_stdout is not sys.stdout) or (last_stderr is not sys.stderr)

        if rebuild:
            self.handlers.clear()
            h = DualStreamHandler()
            h.setFormatter(TagFormatter("%(message)s"))
            h.enable_color = self.enable_color
            self.addHandler(h)
            self._last_stream_ids = (sys.stdout, sys.stderr)
            TEST_TRACE("ensure_handlers()", f"rebuilt_handlers={self.handlers}")

    def _log(  # type: ignore[override]
        self, level: int, msg: str, args: tuple[Any, ...], **kwargs: Any
    ) -> None:
        TEST_TRACE(
            "_log",
            f"logger={self.name}",
            f"id={id(self)}",
            f"level={self.level_name}",
            f"msg={msg!r}",
        )
        self.ensure_handlers()
        super()._log(level, msg, args, **kwargs)

    def setLevel(self, level: int | str) -> None:  # noqa: N802
        """Case insensitive version"""
        if isinstance(level, str):
            level = level.upper()
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

        logging.setLoggerClass(cls)

        logging.addLevelName(TRACE_LEVEL, "TRACE")
        logging.addLevelName(SILENT_LEVEL, "SILENT")

        logging.TRACE = TRACE_LEVEL  # type: ignore[attr-defined]
        logging.SILENT = SILENT_LEVEL  # type: ignore[attr-defined]

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
        env_vars_to_check = (
            _registered_log_level_env_vars or DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
        )
        for env_var in env_vars_to_check:
            env_log_level = os.getenv(env_var)
            if env_log_level:
                return env_log_level.upper()

        if root_log_level:
            return root_log_level.upper()

        # Use registered default, or fall back to module default
        default_level = _registered_default_log_level or DEFAULT_APATHETIC_LOG_LEVEL
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
        return f"{color}{text}{RESET}" if enable_color else text

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, msg, args, **kwargs)

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
            # Only set if requested level is more verbose (lower number) than current
            if level_no < prev_level:
                self.setLevel(level_no)
            # Otherwise keep current level (don't downgrade)
        else:
            self.setLevel(level_no)

        try:
            yield
        finally:
            self.setLevel(prev_level)


# --- Tag formatter ---------------------------------------------------------


class TagFormatter(logging.Formatter):
    def format(self: TagFormatter, record: logging.LogRecord) -> str:
        tag_color, tag_text = TAG_STYLES.get(record.levelname, ("", ""))
        msg = super().format(record)
        if tag_text:
            if getattr(record, "enable_color", False) and tag_color:
                prefix = f"{tag_color}{tag_text}{RESET}"
            else:
                prefix = tag_text
            return f"{prefix} {msg}"
        return msg


# --- DualStreamHandler ---------------------------------------------------------


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


# --- Logger registry ---------------------------------------------------------


# Registry to store the registered logger name
# The logging module itself acts as the registry via logging.getLogger()
_registered_logger_name: str | None = None


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


def register_log_level_env_vars(env_vars: list[str]) -> None:
    """Register environment variable names to check for log level.

    The environment variables will be checked in order, and the first
    non-empty value found will be used.

    Args:
        env_vars: List of environment variable names to check
            (e.g., ["SERGER_LOG_LEVEL", "LOG_LEVEL"])

    Example:
        >>> from apathetic_logs import register_log_level_env_vars
        >>> register_log_level_env_vars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])
    """
    global _registered_log_level_env_vars  # noqa: PLW0603
    _registered_log_level_env_vars = env_vars
    TEST_TRACE(
        "register_log_level_env_vars() called",
        f"env_vars={env_vars}",
    )


def register_default_log_level(default_level: str) -> None:
    """Register the default log level to use when no other source is found.

    Args:
        default_level: Default log level name (e.g., "info", "warning")

    Example:
        >>> from apathetic_logs import register_default_log_level
        >>> register_default_log_level("warning")
    """
    global _registered_default_log_level  # noqa: PLW0603
    _registered_default_log_level = default_level
    TEST_TRACE(
        "register_default_log_level() called",
        f"default_level={default_level}",
    )


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
        >>> from serger.meta import PROGRAM_PACKAGE
        >>> from serger.logs import register_logger_name
        >>> register_logger_name(PROGRAM_PACKAGE)

        >>> # Auto-infer from __package__
        >>> register_logger_name()  # Uses top-level package from __package__
    """
    global _registered_logger_name  # noqa: PLW0603

    auto_inferred = False
    if logger_name is None:
        # Extract top-level package from this module's __package__
        package = globals().get("__package__")
        if package:
            logger_name = _extract_top_level_package(package)
            auto_inferred = True
        if logger_name is None:
            _msg = (
                "Cannot auto-infer logger name: __package__ is not set. "
                "Please call register_logger_name() with an explicit logger name."
            )
            raise RuntimeError(_msg)

    _registered_logger_name = logger_name
    TEST_TRACE(
        "register_logger_name() called",
        f"name={logger_name}",
        f"auto_inferred={auto_inferred}",
    )


def get_logger() -> ApatheticCLILogger:
    """Return the registered logger instance.

    Uses Python's built-in logging registry (logging.getLogger()) to retrieve
    the logger. If no logger name has been registered, attempts to auto-infer
    the logger name from the calling module's top-level package.

    Returns:
        The logger instance from logging.getLogger() (as ApatheticCLILogger type)

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
                        inferred_name = _extract_top_level_package(caller_module)
                        if inferred_name:
                            _registered_logger_name = inferred_name
                            TEST_TRACE(
                                "get_logger() auto-inferred logger name",
                                f"name={inferred_name}",
                                f"from_module={caller_module}",
                            )
            finally:
                del frame

    if _registered_logger_name is None:
        _msg = (
            "Logger name not registered and could not be auto-inferred. "
            "Call register_logger_name() or ensure your app's logs module is imported."
        )
        raise RuntimeError(_msg)

    logger = logging.getLogger(_registered_logger_name)
    # Cast to ApatheticCLILogger - at runtime this will be AppLogger if registered
    typed_logger = cast("ApatheticCLILogger", logger)
    TEST_TRACE(
        "get_logger() called",
        f"name={typed_logger.name}",
        f"id={id(typed_logger)}",
        f"level={typed_logger.level_name}",
        f"handlers={[type(h).__name__ for h in typed_logger.handlers]}",
    )
    return typed_logger


# === apathetic_schema.schema ===
# src/serger/utils/utils_schema.py


# --- constants ----------------------------------------------------------


DEFAULT_HINT_CUTOFF: float = 0.75


# --- types ----------------------------------------------------------


class _SchErrAggEntry(TypedDict):
    msg: str
    contexts: list[str]


"""
severity, tag

Aggregator structure example:
{
  "strict_warnings": {
      "dry-run": {"msg": DRYRUN_MSG, "contexts": ["in build #0", "in build #2"]},
      ...
  },
  "warnings": { ... }
}
"""
SchemaErrorAggregator = dict[str, dict[str, dict[str, _SchErrAggEntry]]]


# --- dataclasses ------------------------------------------------------


@dataclass
class ValidationSummary:
    valid: bool
    errors: list[str]
    strict_warnings: list[str]
    warnings: list[str]
    strict: bool  # strictness somewhere in our config?


# --- constants ------------------------------------------------------

AGG_STRICT_WARN = "strict_warnings"
AGG_WARN = "warnings"

# --- helpers --------------------------------------------------------


def collect_msg(
    msg: str,
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    is_error: bool = False,
) -> None:
    """Route a message to the appropriate bucket.
    Errors are always fatal.
    Warnings may escalate to strict_warnings in strict mode.
    """
    if is_error:
        summary.errors.append(msg)
    elif strict:
        summary.strict_warnings.append(msg)
    else:
        summary.warnings.append(msg)


def flush_schema_aggregators(
    *,
    summary: ValidationSummary,
    agg: SchemaErrorAggregator,
) -> None:
    def _clean_context(ctx: str) -> str:
        """Normalize context strings by removing leading 'in' or 'on'."""
        ctx = ctx.strip()
        for prefix in ("in ", "on "):
            if ctx.lower().startswith(prefix):
                return ctx[len(prefix) :].strip()
        return ctx

    def _flush_one(
        bucket: dict[str, dict[str, Any]],
        *,
        strict: bool,
    ) -> None:
        for tag, entry in bucket.items():
            msg_tmpl = entry["msg"]
            contexts = [_clean_context(c) for c in entry["contexts"]]
            joined_ctx = ", ".join(contexts)
            rendered = msg_tmpl.format(keys=tag, ctx=f"in {joined_ctx}")
            collect_msg(rendered, strict=strict, summary=summary)
        bucket.clear()

    strict_bucket = agg.get(AGG_STRICT_WARN, {})
    warn_bucket = agg.get(AGG_WARN, {})

    if strict_bucket:
        summary.valid = False
        _flush_one(strict_bucket, strict=True)
    if warn_bucket:
        _flush_one(warn_bucket, strict=False)


# ---------------------------------------------------------------------------
# granular schema validator helpers (private and testable)
# ---------------------------------------------------------------------------


def _get_example_for_field(
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> str | None:
    """Get example for field if available in field_examples.

    Args:
        field_path: The full field path
            (e.g. "root.builds.*.include" or "root.watch_interval")
        field_examples: Optional dict mapping field patterns to example values.
        If None, returns None (no examples available).
    """
    if field_examples is None:
        return None

    # First, try exact match (O(1) lookup)
    if field_path in field_examples:
        return field_examples[field_path]

    # Then try wildcard matches
    for pattern, example in field_examples.items():
        if "*" in pattern and fnmatchcase_portable(field_path, pattern):
            return example

    return None


def _infer_type_label(
    expected_type: Any,
) -> str:
    """Return a readable label for logging (e.g. 'list[str]', 'BuildConfig')."""
    try:
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        # Unwrap NotRequired to get the actual type
        if origin is NotRequired and args:
            return _infer_type_label(args[0])

        if origin is list and args:
            return f"list[{getattr(args[0], '__name__', repr(args[0]))}]"
        if isinstance(expected_type, type):
            return expected_type.__name__
        return str(expected_type)
    except Exception:  # noqa: BLE001
        return repr(expected_type)


def _validate_scalar_value(
    context: str,
    key: str,
    val: Any,
    expected_type: Any,
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Validate a single non-container value against its expected type."""
    try:
        if safe_isinstance(val, expected_type):  # self-ref guard
            return True
    except Exception:  # noqa: BLE001
        # Defensive fallback — e.g. weird typing generics
        fallback_type = (
            expected_type if isinstance(expected_type, type) else type(expected_type)
        )
        if isinstance(val, fallback_type):
            return True

    exp_label = _infer_type_label(expected_type)
    example = _get_example_for_field(field_path, field_examples)
    exmsg = ""
    if example:
        exmsg = f" (e.g. {example})"

    msg = (
        f"{context}: key `{key}` expected {exp_label}{exmsg}, got {type(val).__name__}"
    )
    collect_msg(msg, summary=summary, strict=strict, is_error=True)
    return False


def _validate_list_value(
    context: str,
    key: str,
    val: Any,
    subtype: Any,
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Validate a homogeneous list value, delegating to scalar/TypedDict validators."""
    if not isinstance(val, list):
        exp_label = f"list[{_infer_type_label(subtype)}]"
        example = _get_example_for_field(field_path, field_examples)
        exmsg = ""
        if example:
            exmsg = f" (e.g. {example})"
        msg = (
            f"{context}: key `{key}` expected {exp_label}{exmsg},"
            f" got {type(val).__name__}"
        )
        collect_msg(
            msg,
            strict=strict,
            summary=summary,
            is_error=True,
        )
        return False

    # Treat val as a real list for static type checkers
    items = cast_hint(list[Any], val)

    # Empty list → fine, nothing to check
    if not items:
        return True

    valid = True
    for i, item in enumerate(items):
        # Detect TypedDict-like subtypes
        if (
            isinstance(subtype, type)
            and hasattr(subtype, "__annotations__")
            and hasattr(subtype, "__total__")
        ):
            if not isinstance(item, dict):
                collect_msg(
                    f"{context}: key `{key}` #{i + 1} expected an "
                    " object with named keys for "
                    f"{subtype.__name__}, got {type(item).__name__}",
                    strict=strict,
                    summary=summary,
                    is_error=True,
                )
                valid = False
                continue
            valid &= _validate_typed_dict(
                f"{context}.{key}[{i}]",
                item,
                subtype,
                strict=strict,
                summary=summary,
                prewarn=prewarn,
                field_path=f"{field_path}[{i}]",
                field_examples=field_examples,
            )
        else:
            valid &= _validate_scalar_value(
                context,
                f"{key}[{i}]",
                item,
                subtype,
                strict=strict,
                summary=summary,
                field_path=f"{field_path}[{i}]",
                field_examples=field_examples,
            )
    return valid


def _dict_unknown_keys(
    context: str,
    val: Any,
    schema: dict[str, Any],
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
) -> bool:
    # --- Unknown keys ---
    val_dict = cast("dict[str, Any]", val)
    unknown: list[str] = [k for k in val_dict if k not in schema and k not in prewarn]
    if unknown:
        joined = ", ".join(f"`{u}`" for u in unknown)

        location = context
        if "in top-level configuration." in location:
            location = "in " + location.split("in top-level configuration.")[-1]

        msg = f"Unknown key{plural(unknown)} {joined} {location}."

        hints: list[str] = []
        for k in unknown:
            close = get_close_matches(k, schema.keys(), n=1, cutoff=DEFAULT_HINT_CUTOFF)
            if close:
                hints.append(f"'{k}' → '{close[0]}'")
        if hints:
            msg += "\nHint: did you mean " + ", ".join(hints) + "?"

        collect_msg(msg.strip(), strict=strict, summary=summary)
        if strict:
            return False

    return True


def _dict_fields(
    context: str,
    val: Any,
    schema: dict[str, Any],
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
    ignore_keys: set[str],
    field_path: str,
    field_examples: dict[str, str] | None = None,
) -> bool:
    valid = True

    for field, expected_type in schema.items():
        if field not in val or field in prewarn or field in ignore_keys:
            # Optional or missing field → not a failure
            continue

        inner_val = val[field]
        origin = get_origin(expected_type)
        args = get_args(expected_type)
        exp_label = _infer_type_label(expected_type)
        current_field_path = f"{field_path}.{field}" if field_path else field

        if origin is list:
            subtype = args[0] if args else Any
            valid &= _validate_list_value(
                context,
                field,
                inner_val,
                subtype,
                strict=strict,
                summary=summary,
                prewarn=prewarn,
                field_path=current_field_path,
                field_examples=field_examples,
            )
        elif (
            isinstance(expected_type, type)
            and hasattr(expected_type, "__annotations__")
            and hasattr(expected_type, "__total__")
        ):
            # we don't pass ignore_keys down because
            # we don't recursively ignore these keys
            # and they have no depth syntax. Instead you
            # need to ignore the current level, then take ownership
            # and only validate what you want manually. calling validation
            # on anything that you aren't ignoring downstream.
            # rare case that is a lot of work, but keeps the rest
            # simple for now.
            if "in top-level configuration." in context:
                location = field
            else:
                location = f"{context}.{field}"
            valid &= _validate_typed_dict(
                location,
                inner_val,
                expected_type,
                strict=strict,
                summary=summary,
                prewarn=prewarn,
                field_path=current_field_path,
                field_examples=field_examples,
            )
        else:
            val_scalar = _validate_scalar_value(
                context,
                field,
                inner_val,
                expected_type,
                strict=strict,
                summary=summary,
                field_path=current_field_path,
                field_examples=field_examples,
            )
            if not val_scalar:
                collect_msg(
                    f"{context}: key `{field}` expected {exp_label}, "
                    f"got {type(inner_val).__name__}",
                    strict=strict,
                    summary=summary,
                    is_error=True,
                )
                valid = False

    return valid


def _validate_typed_dict(
    context: str,
    val: Any,
    typedict_cls: type[Any],
    *,
    strict: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str],
    ignore_keys: set[str] | None = None,
    field_path: str = "",
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Validate a dict against a TypedDict schema recursively.

    - Return False if val is not a dict
    - Recurse into its fields using _validate_scalar_value or _validate_list_value
    - Warn about unknown keys under strict=True
    """
    if ignore_keys is None:
        ignore_keys = set()

    if not isinstance(val, dict):
        collect_msg(
            f"{context}: expected an object with named keys for"
            f" {typedict_cls.__name__}, got {type(val).__name__}",
            strict=strict,
            summary=summary,
            is_error=True,
        )
        return False

    if not hasattr(typedict_cls, "__annotations__"):
        xmsg = (
            "Internal schema invariant violated: "
            f"{typedict_cls!r} has no __annotations__."
        )
        raise AssertionError(xmsg)

    schema = schema_from_typeddict(typedict_cls)
    valid = True

    # --- walk through all the fields recursively ---
    if not _dict_fields(
        context,
        val,
        schema,
        strict=strict,
        summary=summary,
        prewarn=prewarn,
        ignore_keys=ignore_keys,
        field_path=field_path,
        field_examples=field_examples,
    ):
        valid = False

    # --- Unknown keys ---
    if not _dict_unknown_keys(
        context,
        val,
        schema,
        strict=strict,
        summary=summary,
        prewarn=prewarn,
    ):
        valid = False

    return valid


# ---------------------------------------------------------------------------
# granular schema validator
# ---------------------------------------------------------------------------


# --- warn_keys_once -------------------------------------------


def warn_keys_once(
    tag: str,
    bad_keys: set[str],
    cfg: dict[str, Any],
    context: str,
    msg: str,
    *,
    strict_config: bool,
    summary: ValidationSummary,  # modified in function, not returned
    agg: SchemaErrorAggregator | None,
) -> tuple[bool, set[str]]:
    """Warn once for known bad keys (e.g. dry-run, root-only).

    agg indexes are: severity, tag, msg, context (list[str])

    Returns (valid, found_keys).
    """
    valid = True

    # Normalize keys to lowercase for case-insensitive matching
    bad_keys_lower = {k.lower(): k for k in bad_keys}
    cfg_keys_lower = {k.lower(): k for k in cfg}
    found_lower = bad_keys_lower & cfg_keys_lower.keys()

    if not found_lower:
        return True, set()

    # Recover original-case keys for display
    found = {cfg_keys_lower[k] for k in found_lower}

    if agg is not None:
        # record context for later aggregation
        severity = AGG_STRICT_WARN if strict_config else AGG_WARN
        bucket = cast_hint(dict[str, _SchErrAggEntry], agg.setdefault(severity, {}))

        default_entry: _SchErrAggEntry = {"msg": msg, "contexts": []}
        entry = bucket.setdefault(tag, default_entry)
        entry["contexts"].append(context)
    else:
        # immediate fallback
        collect_msg(
            f"{msg.format(keys=', '.join(sorted(found)), ctx=context)}",
            strict=strict_config,
            summary=summary,
        )

    if strict_config:
        valid = False

    return valid, found


# --- check_schema_conformance --------------------


def check_schema_conformance(
    cfg: dict[str, Any],
    schema: dict[str, Any],
    context: str,
    *,
    strict_config: bool,
    summary: ValidationSummary,  # modified in function, not returned
    prewarn: set[str] | None = None,
    ignore_keys: set[str] | None = None,
    base_path: str = "root",
    field_examples: dict[str, str] | None = None,
) -> bool:
    """Thin wrapper around _validate_typed_dict for root-level schema checks."""
    if prewarn is None:
        prewarn = set()
    if ignore_keys is None:
        ignore_keys = set()

    # Pretend schema is a TypedDict for uniformity
    class _AnonTypedDict(TypedDict):
        pass

    # Attach the schema dynamically to mimic schema_from_typeddict output
    _AnonTypedDict.__annotations__ = schema

    return _validate_typed_dict(
        context,
        cfg,
        _AnonTypedDict,
        strict=strict_config,
        summary=summary,
        prewarn=prewarn,
        ignore_keys=ignore_keys,
        field_path=base_path,
        field_examples=field_examples,
    )


# === apathetic_utils.system ===
# src/serger/utils/utils_system.py


# --- types --------------------------------------------------------------------


@dataclass
class CapturedOutput:
    """Captured stdout, stderr, and merged streams."""

    stdout: StringIO
    stderr: StringIO
    merged: StringIO

    def __str__(self) -> str:
        """Human-friendly representation (merged output)."""
        return self.merged.getvalue()

    def as_dict(self) -> dict[str, str]:
        """Return contents as plain strings for serialization."""
        return {
            "stdout": self.stdout.getvalue(),
            "stderr": self.stderr.getvalue(),
            "merged": self.merged.getvalue(),
        }


# --- system utilities --------------------------------------------------------


def get_sys_version_info() -> tuple[int, int, int] | tuple[int, int, int, str, int]:
    return sys.version_info


def is_running_under_pytest() -> bool:
    """Detect if code is running under pytest.

    Checks multiple indicators:
    - Environment variables set by pytest
    - Command-line arguments containing 'pytest'

    Returns:
        True if running under pytest, False otherwise
    """
    return (
        "pytest" in os.environ.get("_", "")
        or "PYTEST_CURRENT_TEST" in os.environ
        or any(
            "pytest" in arg
            for arg in sys.argv
            if isinstance(arg, str)  # pyright: ignore[reportUnnecessaryIsInstance]
        )
    )


def detect_runtime_mode() -> str:
    if getattr(sys, "frozen", False):
        return "frozen"
    if "__main__" in sys.modules and getattr(
        sys.modules["__main__"],
        __file__,
        "",
    ).endswith(".pyz"):
        return "zipapp"
    if "__STANDALONE__" in globals():
        return "standalone"
    return "installed"


@contextmanager
def capture_output() -> Iterator[CapturedOutput]:
    """Temporarily capture stdout and stderr.

    Any exception raised inside the block is re-raised with
    the captured output attached as `exc.captured_output`.

    Example:
    from serger.utils import capture_output
    from serger.cli import main

    with capture_output() as cap:
        exit_code = main(["--config", "my.cfg", "--dry-run"])

    result = {
        "exit_code": exit_code,
        "stdout": cap.stdout.getvalue(),
        "stderr": cap.stderr.getvalue(),
        "merged": cap.merged.getvalue(),
    }

    """
    merged = StringIO()

    class TeeStream(StringIO):
        def write(self, s: str) -> int:
            merged.write(s)
            return super().write(s)

    buf_out, buf_err = TeeStream(), TeeStream()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buf_out, buf_err

    cap = CapturedOutput(stdout=buf_out, stderr=buf_err, merged=merged)
    try:
        yield cap
    except Exception as e:
        # Attach captured output to the raised exception for API introspection
        e.captured_output = cap  # type: ignore[attr-defined]
        raise
    finally:
        sys.stdout, sys.stderr = old_out, old_err


# === apathetic_utils.text ===
# src/serger/utils/utils_text.py


def plural(obj: Any) -> str:
    """Return 's' if obj represents a plural count.

    Accepts ints, floats, and any object implementing __len__().
    Returns '' for singular or zero.
    """
    count: int | float
    try:
        count = len(obj)
    except TypeError:
        # fallback for numbers or uncountable types
        count = obj if isinstance(obj, (int, float)) else 0
    return "s" if count != 1 else ""


def remove_path_in_error_message(inner_msg: str, path: Path) -> str:
    """Remove redundant file path mentions (and nearby filler)
    from error messages.

    Useful when wrapping a lower-level exception that already
    embeds its own file reference, so the higher-level message
    can use its own path without duplication.

    Example:
        "Invalid JSONC syntax in /abs/path/config.jsonc: Expecting value"
        → "Invalid JSONC syntax: Expecting value"

    """
    # Normalize both path and name for flexible matching
    full_path = str(path)
    filename = path.name

    # Common redundant phrases we might need to remove
    candidates = [
        f"in {full_path}",
        f"in '{full_path}'",
        f'in "{full_path}"',
        f"in {filename}",
        f"in '{filename}'",
        f'in "{filename}"',
        full_path,
        filename,
    ]

    clean_msg = inner_msg
    for pattern in candidates:
        clean_msg = clean_msg.replace(pattern, "").strip(": ").strip()

    # Normalize leftover spaces and colons
    clean_msg = re.sub(r"\s{2,}", " ", clean_msg)
    clean_msg = re.sub(r"\s*:\s*", ": ", clean_msg)

    return clean_msg


# === apathetic_utils.types ===
# src/serger/utils/utils_types.py


T = TypeVar("T")


def cast_hint(_typ: type[T], value: Any) -> T:
    """Explicit cast that documents intent but is purely for type hinting.

    A drop-in replacement for `typing.cast`, meant for places where:
      - You want to silence mypy's redundant-cast warnings.
      - You want to signal "this narrowing is intentional."
      - You need IDEs (like Pylance) to retain strong inference on a value.

    Does not handle Union, Optional, or nested generics: stick to cast(),
      because unions almost always represent a meaningful type narrowing.

    This function performs *no runtime checks*.
    """
    return cast("T", value)


def schema_from_typeddict(td: type[Any]) -> dict[str, Any]:
    """Extract field names and their annotated types from a TypedDict."""
    return get_type_hints(td, include_extras=True)


def _isinstance_generics(  # noqa: PLR0911
    value: Any,
    origin: Any,
    args: tuple[Any, ...],
) -> bool:
    # Outer container check
    if not isinstance(value, origin):
        return False

    # Recursively check elements for known homogeneous containers
    if not args:
        return True

    # list[str]
    if origin is list and isinstance(value, list):
        subtype = args[0]
        items = cast_hint(list[Any], value)
        return all(safe_isinstance(v, subtype) for v in items)

    # dict[str, int]
    if origin is dict and isinstance(value, dict):
        key_t, val_t = args if len(args) == 2 else (Any, Any)  # noqa: PLR2004
        dct = cast_hint(dict[Any, Any], value)
        return all(
            safe_isinstance(k, key_t) and safe_isinstance(v, val_t)
            for k, v in dct.items()
        )

    # Tuple[str, int] etc.
    if origin is tuple and isinstance(value, tuple):
        subtypes = args
        tup = cast_hint(tuple[Any, ...], value)
        if len(subtypes) == len(tup):
            return all(
                safe_isinstance(v, t) for v, t in zip(tup, subtypes, strict=False)
            )
        if len(subtypes) == 2 and subtypes[1] is Ellipsis:  # noqa: PLR2004
            return all(safe_isinstance(v, subtypes[0]) for v in tup)
        return False

    return True  # e.g., other typing origins like set[], Iterable[]


def safe_isinstance(value: Any, expected_type: Any) -> bool:  # noqa: PLR0911
    """Like isinstance(), but safe for TypedDicts and typing generics.

    Handles:
      - typing.Union, Optional, Any
      - typing.NotRequired
      - TypedDict subclasses
      - list[...] with inner types
      - Defensive fallback for exotic typing constructs
    """
    # --- Always allow Any ---
    if expected_type is Any:
        return True

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # --- Handle NotRequired (extract inner type) ---
    if origin is NotRequired:
        # NotRequired[str] → validate as str
        if args:
            return safe_isinstance(value, args[0])
        return True

    # --- Handle Literals explicitly ---
    if origin is Literal:
        # Literal["x", "y"] → True if value equals any of the allowed literals
        return value in args

    # --- Handle Unions (includes Optional) ---
    if origin in {Union, UnionType}:
        # e.g. Union[str, int]
        return any(safe_isinstance(value, t) for t in args)

    # --- Handle special case: TypedDicts ---
    try:
        if (
            isinstance(expected_type, type)
            and hasattr(expected_type, "__annotations__")
            and hasattr(expected_type, "__total__")
        ):
            # Treat TypedDict-like as dict
            return isinstance(value, dict)
    except TypeError:
        # Not a class — skip
        pass

    # --- Handle generics like list[str], dict[str, int] ---
    if origin:
        return _isinstance_generics(value, origin, args)

    # --- Fallback for simple types ---
    try:
        return isinstance(value, expected_type)
    except TypeError:
        # Non-type or strange typing construct
        return False


# === serger.config.config_types ===
# src/serger/config/config_types.py


OriginType = Literal["cli", "config", "plugin", "default", "code", "gitignore", "test"]


# Post-processing configuration types
class ToolConfig(TypedDict, total=False):
    command: str  # executable name (optional - defaults to key if missing)
    args: list[str]  # command arguments (optional, replaces defaults)
    path: str  # custom executable path
    options: list[str]  # additional CLI arguments (appends to args)


class PostCategoryConfig(TypedDict, total=False):
    enabled: bool  # default: True
    priority: list[str]  # tool names in priority order
    tools: NotRequired[dict[str, ToolConfig]]  # per-tool overrides


class PostProcessingConfig(TypedDict, total=False):
    enabled: bool  # master switch, default: True
    category_order: list[str]  # order to run categories
    categories: NotRequired[dict[str, PostCategoryConfig]]  # category definitions


# Resolved types - all fields are guaranteed to be present with final values
class ToolConfigResolved(TypedDict):
    command: str  # executable name (defaults to tool_label if not specified)
    args: list[str]  # command arguments (always present)
    path: str | None  # custom executable path (None if not specified)
    options: list[str]  # additional CLI arguments (empty list if not specified)


class PostCategoryConfigResolved(TypedDict):
    enabled: bool  # always present
    priority: list[str]  # always present (may be empty)
    tools: dict[str, ToolConfigResolved]  # always present (may be empty dict)


class PostProcessingConfigResolved(TypedDict):
    enabled: bool
    category_order: list[str]
    categories: dict[str, PostCategoryConfigResolved]


class PathResolved(TypedDict):
    path: Path | str  # absolute or relative to `root`, or a pattern
    root: Path  # canonical origin directory for resolution
    pattern: NotRequired[str]  # the original pattern matching this path

    # meta only
    origin: OriginType  # provenance


class IncludeResolved(PathResolved):
    dest: NotRequired[Path]  # optional override for target name


class MetaBuildConfigResolved(TypedDict):
    # sources of parameters
    cli_root: Path
    config_root: Path


class IncludeConfig(TypedDict):
    path: str
    dest: NotRequired[str]


class BuildConfig(TypedDict, total=False):
    include: list[str | IncludeConfig]
    exclude: list[str]

    # optional per-build override
    strict_config: bool
    out: str
    respect_gitignore: bool
    log_level: str

    # Single-build convenience (propagated upward)
    watch_interval: float
    post_processing: PostProcessingConfig  # Post-processing configuration

    # Pyproject.toml integration
    use_pyproject: bool  # Whether to pull metadata from pyproject.toml
    pyproject_path: str  # Path to pyproject.toml (overrides root default)

    # Stitching configuration
    package: str  # Package name for imports (e.g., "serger")
    # Explicit module order for stitching (optional; auto-discovered if not provided)
    order: list[str]
    license_header: str  # License header text for stitched output
    display_name: str  # Display name for header (defaults to package)
    description: str  # Description for header (defaults to blank)
    repo: str  # Repository URL for header (optional)


class RootConfig(TypedDict, total=False):
    builds: list[BuildConfig]

    # Defaults that cascade into each build
    log_level: str
    out: str
    respect_gitignore: bool

    # runtime behavior
    strict_config: bool
    watch_interval: float
    post_processing: PostProcessingConfig  # Post-processing configuration

    # Pyproject.toml integration
    use_pyproject: bool  # Whether to pull metadata from pyproject.toml (default: true)
    pyproject_path: str  # Path to pyproject.toml (fallback for single builds)


class BuildConfigResolved(TypedDict):
    include: list[IncludeResolved]
    exclude: list[PathResolved]

    # optional per-build override
    strict_config: bool
    out: PathResolved
    respect_gitignore: bool
    log_level: str

    # runtime flag (CLI only, not persisted in normal configs)
    dry_run: bool

    # global provenance (optional, for audit/debug)
    __meta__: MetaBuildConfigResolved

    # Stitching fields (optional - present if this is a stitch build)
    package: NotRequired[str]
    order: NotRequired[list[str]]
    license_header: NotRequired[str]
    display_name: NotRequired[str]
    description: NotRequired[str]
    repo: NotRequired[str]
    post_processing: NotRequired[
        PostProcessingConfigResolved
    ]  # Post-processing configuration


class RootConfigResolved(TypedDict):
    builds: list[BuildConfigResolved]

    # runtime behavior
    log_level: str
    strict_config: bool
    watch_interval: float
    post_processing: PostProcessingConfigResolved


# === serger.constants ===
# src/serger/constants.py
"""Central constants used across the project."""


RUNTIME_MODES = {
    "standalone",  # single stitched file
    "installed",  # poetry-installed / pip-installed / importable
    "zipapp",  # .pyz bundle
}

# --- env keys ---
DEFAULT_ENV_LOG_LEVEL: str = "LOG_LEVEL"
DEFAULT_ENV_RESPECT_GITIGNORE: str = "RESPECT_GITINGORE"
DEFAULT_ENV_WATCH_INTERVAL: str = "WATCH_INTERVAL"

# --- program defaults ---
DEFAULT_LOG_LEVEL: str = "info"
DEFAULT_WATCH_INTERVAL: float = 1.0  # seconds
DEFAULT_RESPECT_GITIGNORE: bool = True

# --- config defaults ---
DEFAULT_STRICT_CONFIG: bool = True
DEFAULT_OUT_DIR: str = "dist"
DEFAULT_DRY_RUN: bool = False
DEFAULT_USE_PYPROJECT: bool = True

# --- post-processing defaults ---
DEFAULT_CATEGORY_ORDER: list[str] = ["static_checker", "formatter", "import_sorter"]

# Type: dict[str, dict[str, Any]] - matches PostCategoryConfig structure
# All tool commands are defined in tools dict for consistency (supports custom labels)
# Note: This is the raw default structure; it gets resolved to
# PostCategoryConfigResolved
DEFAULT_CATEGORIES: dict[str, dict[str, Any]] = {
    "static_checker": {
        "enabled": True,
        "priority": ["ruff"],
        "tools": {
            "ruff": {
                "args": ["check", "--fix"],
            },
        },
    },
    "formatter": {
        "enabled": True,
        "priority": ["ruff", "black"],
        "tools": {
            "ruff": {
                "args": ["format"],
            },
            "black": {
                "args": ["format"],
            },
        },
    },
    "import_sorter": {
        "enabled": True,
        "priority": ["ruff", "isort"],
        "tools": {
            "ruff": {
                "args": ["check", "--select", "I", "--fix"],
            },
            "isort": {
                "args": ["--fix"],
            },
        },
    },
}


# === serger.meta ===
# src/serger/meta.py

"""Centralized program identity constants for Serger."""


_BASE = "serger"

# CLI script name (the executable or `poetry run` entrypoint)
PROGRAM_SCRIPT = _BASE

# config file name
PROGRAM_CONFIG = _BASE

# Human-readable name for banners, help text, etc.
PROGRAM_DISPLAY = _BASE.replace("-", " ").title()

# Python package / import name
PROGRAM_PACKAGE = _BASE.replace("-", "_")

# Environment variable prefix (used for <APP>_BUILD_LOG_LEVEL, etc.)
PROGRAM_ENV = _BASE.replace("-", "_").upper()

# Short tagline or __DESCRIPTION for help screens and metadata
DESCRIPTION = "Stitch your module into a single file."


@dataclass(frozen=True)
class Metadata:
    """Lightweight result from get_metadata(), containing version and commit info."""

    version: str
    commit: str

    def __str__(self) -> str:
        return f"{self.version} ({self.commit})"


# === apathetic_utils.files ===
# src/serger/utils/utils_files.py


def _strip_jsonc_comments(text: str) -> str:  # noqa: PLR0912
    """Strip comments from JSONC while preserving string contents.

    Handles //, #, and /* */ comments without modifying content inside strings.
    """
    result: list[str] = []
    in_string = False
    in_escape = False
    i = 0
    while i < len(text):
        ch = text[i]

        # Handle escape sequences in strings
        if in_escape:
            result.append(ch)
            in_escape = False
            i += 1
            continue

        if ch == "\\" and in_string:
            result.append(ch)
            in_escape = True
            i += 1
            continue

        # Toggle string state
        if ch in ('"', "'") and (not in_string or text[i - 1 : i] != "\\"):
            in_string = not in_string
            result.append(ch)
            i += 1
            continue

        # If in a string, keep everything
        if in_string:
            result.append(ch)
            i += 1
            continue

        # Outside strings: handle comments
        # Check for // comment (but skip URLs like http://)
        if (
            ch == "/"
            and i + 1 < len(text)
            and text[i + 1] == "/"
            and not (i > 0 and text[i - 1] == ":")
        ):
            # Skip to end of line
            while i < len(text) and text[i] != "\n":
                i += 1
            if i < len(text):
                result.append("\n")
                i += 1
            continue

        # Check for # comment
        if ch == "#":
            # Skip to end of line
            while i < len(text) and text[i] != "\n":
                i += 1
            if i < len(text):
                result.append("\n")
                i += 1
            continue

        # Check for block comments /* ... */
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
            # Skip to end of block comment
            i += 2
            while i + 1 < len(text):
                if text[i] == "*" and text[i + 1] == "/":
                    i += 2
                    break
                i += 1
            continue

        # Regular character
        result.append(ch)
        i += 1

    return "".join(result)


def load_toml(path: Path, *, required: bool = False) -> dict[str, Any] | None:
    """Load and parse a TOML file, supporting Python 3.10 and 3.11+.

    Uses:
    - `tomllib` (Python 3.11+ standard library)
    - `tomli` (required for Python 3.10 - must be installed separately)

    Args:
        path: Path to TOML file
        required: If True, raise RuntimeError when tomli is missing on Python 3.10.
                  If False, return None when unavailable (caller handles gracefully).

    Returns:
        Parsed TOML data as a dictionary, or None if unavailable and not required

    Raises:
        FileNotFoundError: If the file doesn't exist
        RuntimeError: If required=True and neither tomllib nor tomli is available
        ValueError: If the file cannot be parsed
    """
    if not path.exists():
        xmsg = f"TOML file not found: {path}"
        raise FileNotFoundError(xmsg)

    # Try tomllib (Python 3.11+)
    try:
        import tomllib  # type: ignore[import-not-found] # noqa: PLC0415

        with path.open("rb") as f:
            return tomllib.load(f)  # type: ignore[no-any-return]
    except ImportError:
        pass

    # Try tomli (required for Python 3.10)
    try:
        import tomli  # type: ignore[import-not-found,unused-ignore] # noqa: PLC0415  # pyright: ignore[reportMissingImports]

        with path.open("rb") as f:
            return tomli.load(f)  # type: ignore[no-any-return,unused-ignore]  # pyright: ignore[reportUnknownReturnType]
    except ImportError:
        if required:
            xmsg = (
                "TOML parsing requires 'tomli' package on Python 3.10. "
                "Install it with: pip install tomli, or disable pyproject.toml support "
                "by setting 'use_pyproject: false' in your config."
            )
            raise RuntimeError(xmsg) from None
        return None


def load_jsonc(path: Path) -> dict[str, Any] | list[Any] | None:
    """Load JSONC (JSON with comments and trailing commas)."""
    logger = get_logger()
    logger.trace(f"[load_jsonc] Loading from {path}")

    if not path.exists():
        xmsg = f"JSONC file not found: {path}"
        raise FileNotFoundError(xmsg)

    if not path.is_file():
        xmsg = f"Expected a file: {path}"
        raise ValueError(xmsg)

    text = path.read_text(encoding="utf-8")
    text = _strip_jsonc_comments(text)

    # Remove trailing commas before } or ]
    text = re.sub(r",(?=\s*[}\]])", "", text)

    # Trim whitespace
    text = text.strip()

    if not text:
        # Empty or only comments → interpret as "no config"
        return None

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        xmsg = (
            f"Invalid JSONC syntax in {path}:"
            f" {e.msg} (line {e.lineno}, column {e.colno})"
        )
        raise ValueError(xmsg) from e

    # Guard against scalar roots (invalid config structure)
    if not isinstance(data, (dict, list)):
        xmsg = f"Invalid JSONC root type: {type(data).__name__}"
        raise ValueError(xmsg)  # noqa: TRY004

    # narrow type
    result = cast("dict[str, Any] | list[Any]", data)
    logger.trace(
        f"[load_jsonc] Loaded {type(result).__name__} with"
        f" {len(result) if hasattr(result, '__len__') else 'N/A'} items"
    )
    return result


# === apathetic_utils.paths ===
# src/serger/utils/utils_paths.py


def normalize_path_string(raw: str) -> str:
    r"""Normalize a user-supplied path string for cross-platform use.

    Industry-standard (Git/Node/Python) rules:
      - Treat both '/' and '\\' as valid separators and normalize all to '/'.
      - Replace escaped spaces ('\\ ') with real spaces.
      - Collapse redundant slashes (preserve protocol prefixes like 'file://').
      - Never resolve '.' or '..' or touch the filesystem.
      - Never raise for syntax; normalization is always possible.

    This is the pragmatic cross-platform normalization strategy used by
    Git, Node.js, and Python build tools.
    This function is purely lexical — it normalizes syntax, not filesystem state.
    """
    logger = get_logger()
    if not raw:
        return ""

    path = raw.strip()

    # Handle escaped spaces (common shell copy-paste)
    if "\\ " in path:
        fixed = path.replace("\\ ", " ")
        logger.warning("Normalizing escaped spaces in path: %r → %s", path, fixed)
        path = fixed

    # Normalize all backslashes to forward slashes
    path = path.replace("\\", "/")

    # Collapse redundant slashes (keep protocol //)
    collapsed_slashes = re.sub(r"(?<!:)//+", "/", path)
    if collapsed_slashes != path:
        logger.trace("Collapsed redundant slashes: %r → %r", path, collapsed_slashes)
        path = collapsed_slashes

    return path


def has_glob_chars(s: str) -> bool:
    return any(c in s for c in "*?[]")


def get_glob_root(pattern: str) -> Path:
    """Return the non-glob portion of a path like 'src/**/*.txt'.

    Normalizes paths to cross-platform.
    """
    if not pattern:
        return Path()

    # Normalize backslashes to forward slashes
    normalized = normalize_path_string(pattern)

    parts: list[str] = []
    for part in Path(normalized).parts:
        if re.search(r"[*?\[\]]", part):
            break
        parts.append(part)
    return Path(*parts) if parts else Path()


# === apathetic_utils.matching ===
# src/serger/utils/utils_matching.py


@lru_cache(maxsize=512)
def _compile_glob_recursive(pattern: str) -> re.Pattern[str]:
    """
    Compile a glob pattern to regex, backporting recursive '**' on Python < 3.11.
    This translator handles literals, ?, *, **, and [] classes without relying on
    slicing fnmatch.translate() output, avoiding unbalanced parentheses.
    Always case-sensitive.
    """

    def _escape_lit(ch: str) -> str:
        # Escape regex metacharacters
        if ch in ".^$+{}[]|()\\":
            return "\\" + ch
        return ch

    i = 0
    n = len(pattern)
    pieces: list[str] = []
    while i < n:
        ch = pattern[i]

        # Character class: copy through closing ']'
        if ch == "[":
            j = i + 1
            if j < n and pattern[j] in "!^":
                j += 1
            # allow leading ']' inside class as a literal
            if j < n and pattern[j] == "]":
                j += 1
            while j < n and pattern[j] != "]":
                j += 1
            if j < n and pattern[j] == "]":
                # whole class, keep as-is (regex already)
                pieces.append(pattern[i : j + 1])
                i = j + 1
            else:
                # unmatched '[', treat literally
                pieces.append("\\[")
                i += 1
            continue

        # Recursive glob
        if ch == "*" and i + 1 < n and pattern[i + 1] == "*":
            # Collapse a run of consecutive '*' to detect '**'
            k = i + 2
            while k < n and pattern[k] == "*":
                k += 1
            # Treat any run >= 2 as recursive
            pieces.append(".*")
            i = k
            continue

        # Single-segment glob
        if ch == "*":
            pieces.append("[^/]*")
            i += 1
            continue

        # Single character
        if ch == "?":
            pieces.append("[^/]")
            i += 1
            continue

        # Path separator or literal
        pieces.append(_escape_lit(ch))
        i += 1

    inner = "".join(pieces)
    return re.compile(f"(?s:{inner})\\Z")


def fnmatchcase_portable(path: str, pattern: str) -> bool:
    """
    Case-sensitive glob pattern matching with Python 3.10 '**' backport.

    Uses fnmatchcase (case-sensitive) as the base, with backported support
    for recursive '**' patterns on Python 3.10.

    Args:
        path: The path to match against the pattern
        pattern: The glob pattern to match

    Returns:
        True if the path matches the pattern, False otherwise.
    """
    if get_sys_version_info() >= (3, 11) or "**" not in pattern:
        return fnmatchcase(path, pattern)
    return bool(_compile_glob_recursive(pattern).match(path))


def is_excluded_raw(  # noqa: PLR0911
    path: Path | str,
    exclude_patterns: list[str],
    root: Path | str,
) -> bool:
    """Smart matcher for normalized inputs.

    - Treats 'path' as relative to 'root' unless already absolute.
    - If 'root' is a file, match directly.
    - Handles absolute or relative glob patterns.

    Note:
    The function does not require `root` to exist; if it does not,
    a debug message is logged and matching is purely path-based.
    """
    logger = get_logger()
    root = Path(root).resolve()
    path = Path(path)

    logger.trace(
        f"[is_excluded_raw] Checking path={path} against"
        f" {len(exclude_patterns)} patterns"
    )

    # the callee really should deal with this, otherwise we might spam
    if not Path(root).exists():
        logger.debug("Exclusion root does not exist: %s", root)

    # If the root itself is a file, treat that as a direct exclusion target.
    if root.is_file():
        # If the given path resolves exactly to that file, exclude it.
        full_path = path if path.is_absolute() else (root.parent / path)
        return full_path.resolve() == root.resolve()

    # If no exclude patterns, nothing else to exclude
    if not exclude_patterns:
        return False

    # Otherwise, treat as directory root.
    full_path = path if path.is_absolute() else (root / path)

    try:
        rel = str(full_path.relative_to(root)).replace("\\", "/")
    except ValueError:
        # Path lies outside the root; skip matching
        return False

    for pattern in exclude_patterns:
        pat = pattern.replace("\\", "/")

        logger.trace(f"[is_excluded_raw] Testing pattern {pattern!r} against {rel}")

        # If pattern is absolute and under root, adjust to relative form
        if pat.startswith(str(root)):
            try:
                pat_rel = str(Path(pat).relative_to(root)).replace("\\", "/")
            except ValueError:
                pat_rel = pat  # not under root; treat as-is
            if fnmatchcase_portable(rel, pat_rel):
                logger.trace(f"[is_excluded_raw] MATCHED pattern {pattern!r}")
                return True

        # Otherwise treat pattern as relative glob
        if fnmatchcase_portable(rel, pat):
            logger.trace(f"[is_excluded_raw] MATCHED pattern {pattern!r}")
            return True

        # Optional directory-only semantics
        if pat.endswith("/") and rel.startswith(pat.rstrip("/") + "/"):
            logger.trace(f"[is_excluded_raw] MATCHED pattern {pattern!r}")
            return True

    return False


# === serger.utils.utils_types ===
# src/serger/utils/utils_types.py


def _root_resolved(
    path: Path | str,
    root: Path | str,
    pattern: str | None,
    origin: OriginType,
) -> dict[str, object]:
    # Preserve raw string if available (to keep trailing slashes)
    raw_path = path if isinstance(path, str) else str(path)
    result: dict[str, object] = {
        "path": raw_path,
        "root": Path(root).resolve(),
        "origin": origin,
    }
    if pattern is not None:
        result["pattern"] = pattern
    return result


def make_pathresolved(
    path: Path | str,
    root: Path | str = ".",
    origin: OriginType = "code",
    *,
    pattern: str | None = None,
) -> PathResolved:
    """Quick helper to build a PathResolved entry."""
    # mutate class type
    return cast("PathResolved", _root_resolved(path, root, pattern, origin))


def make_includeresolved(
    path: Path | str,
    root: Path | str = ".",
    origin: OriginType = "code",
    *,
    pattern: str | None = None,
    dest: Path | str | None = None,
) -> IncludeResolved:
    """Create an IncludeResolved entry with optional dest override."""
    entry = _root_resolved(path, root, pattern, origin)
    if dest is not None:
        entry["dest"] = Path(dest)
    # mutate class type
    return cast("IncludeResolved", entry)


# === serger.logs ===
# src/serger/logs.py


# --- Our application logger -----------------------------------------------------


class AppLogger(ApatheticCLILogger):
    def determine_log_level(
        self,
        *,
        args: argparse.Namespace | None = None,
        root_log_level: str | None = None,
        build_log_level: str | None = None,
    ) -> str:
        """Resolve log level from CLI → env → root config → default."""
        args_level = getattr(args, "log_level", None)
        if args_level is not None and args_level:
            # cast_hint would cause circular dependency
            return cast("str", args_level).upper()

        env_log_level = os.getenv(
            f"{PROGRAM_ENV}_{DEFAULT_ENV_LOG_LEVEL}"
        ) or os.getenv(DEFAULT_ENV_LOG_LEVEL)
        if env_log_level:
            return env_log_level.upper()

        if build_log_level:
            return build_log_level.upper()

        if root_log_level:
            return root_log_level.upper()

        return DEFAULT_LOG_LEVEL.upper()


# --- Logger initialization ---------------------------------------------------

# Force the logging module to use our subclass globally.
# This must happen *before* any loggers are created.
# logging.setLoggerClass(AppLogger)

# Force registration of TRACE and SILENT levels
AppLogger.extend_logging_module()

# Register log level environment variables and default
# This must happen before any loggers are created so they use the registered values
register_log_level_env_vars(
    [f"{PROGRAM_ENV}_{DEFAULT_ENV_LOG_LEVEL}", DEFAULT_ENV_LOG_LEVEL]
)
register_default_log_level(DEFAULT_LOG_LEVEL)

# Now this will actually return an AppLogger instance.
# The logging module acts as the registry, so we just need to register the name.
_APP_LOGGER = cast("AppLogger", logging.getLogger(PROGRAM_PACKAGE))


# --- Convenience utils ---------------------------------------------------------


def get_app_logger() -> AppLogger:
    """Return the configured app logger.

    This is the app-specific logger getter that returns AppLogger type.
    Use this in application code instead of utils_logs.get_logger() for
    better type hints.
    """
    logger = cast("AppLogger", get_logger())
    TEST_TRACE(
        "get_logger() called",
        f"id={id(logger)}",
        f"name={logger.name}",
        f"level={logger.level_name}",
        f"handlers={[type(h).__name__ for h in logger.handlers]}",
    )
    return logger


# === serger.config.config_validate ===
# src/serger/config/config_validate.py


# --- constants ------------------------------------------------------

DRYRUN_KEYS = {"dry-run", "dry_run", "dryrun", "no-op", "no_op", "noop"}
DRYRUN_MSG = (
    "Ignored config key(s) {keys} {ctx}: this tool has no config option for it. "
    "Use the CLI flag '--dry-run' instead."
)

ROOT_ONLY_KEYS = {"watch_interval"}
ROOT_ONLY_MSG = "Ignored {keys} {ctx}: these options only apply at the root level."

# Field-specific type examples for better error messages
# Dict format: {field_pattern: example_value}
# Wildcard patterns (with *) are supported for matching multiple fields
FIELD_EXAMPLES: dict[str, str] = {
    "root.builds.*.include": '["src/", "lib/"]',
    "root.builds.*.out": '"dist/script.py"',
    "root.builds.*.display_name": '"MyProject"',
    "root.builds.*.description": '"A description of the project"',
    "root.builds.*.repo": '"https://github.com/user/project"',
    "root.watch_interval": "1.5",
    "root.log_level": '"debug"',
    "root.strict_config": "true",
}


# ---------------------------------------------------------------------------
# main validator
# ---------------------------------------------------------------------------


def _set_valid_and_return(
    *,
    flush: bool = True,
    summary: ValidationSummary,  # could be modified
    agg: SchemaErrorAggregator,  # could be modified
) -> ValidationSummary:
    if flush:
        flush_schema_aggregators(summary=summary, agg=agg)
    summary.valid = not summary.errors and not summary.strict_warnings
    return summary


def _validate_root(
    parsed_cfg: dict[str, Any],
    *,
    strict_arg: bool | None,
    summary: ValidationSummary,  # modified
    agg: SchemaErrorAggregator,  # modified
) -> ValidationSummary | None:
    logger = get_app_logger()
    logger.trace(f"[validate_root] Validating root with {len(parsed_cfg)} keys")

    strict_config: bool = summary.strict
    # --- Determine strictness from arg or root config or default ---
    strict_from_root: Any = parsed_cfg.get("strict_config")
    if strict_arg is not None and strict_arg:
        strict_config = strict_arg
    elif strict_arg is None and isinstance(strict_from_root, bool):
        strict_config = strict_from_root

    if strict_config:
        summary.strict = True

    # --- Validate root-level keys ---
    root_schema = schema_from_typeddict(RootConfig)
    prewarn_root: set[str] = set()
    ok, found = warn_keys_once(
        "dry-run",
        DRYRUN_KEYS,
        parsed_cfg,
        "in top-level configuration",
        DRYRUN_MSG,
        strict_config=strict_config,
        summary=summary,
        agg=agg,
    )
    prewarn_root |= found

    ok = check_schema_conformance(
        parsed_cfg,
        root_schema,
        "in top-level configuration",
        strict_config=strict_config,
        summary=summary,
        prewarn=prewarn_root,
        ignore_keys={"builds"},
        base_path="root",
        field_examples=FIELD_EXAMPLES,
    )
    if not ok and not (summary.errors or summary.strict_warnings):
        collect_msg(
            "Top-level configuration invalid.",
            strict=True,
            summary=summary,
            is_error=True,
        )

    return None


def _validate_builds(
    parsed_cfg: dict[str, Any],
    *,
    strict_arg: bool | None,
    summary: ValidationSummary,  # modified
    agg: SchemaErrorAggregator,  # modified
) -> ValidationSummary | None:
    logger = get_app_logger()
    builds_raw: Any = parsed_cfg.get("builds", [])
    logger.trace("[validate_builds] Validating builds")

    root_strict = summary.valid
    if not isinstance(builds_raw, list):
        collect_msg(
            "`builds` must be a list of builds.",
            strict=True,
            summary=summary,
            is_error=True,
        )
        return _set_valid_and_return(summary=summary, agg=agg)

    if not builds_raw:
        msg = "No `builds` key defined"
        if not (summary.errors or summary.strict_warnings):
            msg = msg + ";  continuing with empty configuration"
        else:
            msg = msg + "."
        collect_msg(
            msg,
            strict=False,
            summary=summary,
        )
        return _set_valid_and_return(summary=summary, agg=agg)

    builds = cast_hint(list[Any], builds_raw)
    build_schema = schema_from_typeddict(BuildConfig)

    for i, b in enumerate(builds):
        logger.trace(f"[validate_builds] Checking build #{i + 1}")
        if not isinstance(b, dict):
            collect_msg(
                f"Build #{i + 1} must be an object"
                " with named keys (not a list or value)",
                strict=True,
                summary=summary,
                is_error=True,
            )
            summary.valid = False
            continue
        b_dict = cast_hint(dict[str, Any], b)

        # strict from arg, build, or root
        strict_config = root_strict
        strict_from_build: Any = b_dict.get("strict_config")
        if strict_arg is not None:
            strict_config = strict_arg
        elif strict_arg is None and isinstance(strict_from_build, bool):
            strict_config = strict_from_build

        prewarn_build: set[str] = set()
        ok, found = warn_keys_once(
            "dry-run",
            DRYRUN_KEYS,
            b_dict,
            f"in build #{i + 1}",
            DRYRUN_MSG,
            strict_config=strict_config,
            summary=summary,
            agg=agg,
        )
        prewarn_build |= found

        ok, found = warn_keys_once(
            "root-only",
            ROOT_ONLY_KEYS,
            b_dict,
            f"in build #{i + 1}",
            ROOT_ONLY_MSG,
            strict_config=strict_config,
            summary=summary,
            agg=agg,
        )
        prewarn_build |= found

        ok = check_schema_conformance(
            b_dict,
            build_schema,
            f"in build #{i + 1}",
            strict_config=strict_config,
            summary=summary,
            prewarn=prewarn_build,
            base_path="root.builds.*",
            field_examples=FIELD_EXAMPLES,
        )
        if not ok and not (summary.errors or summary.strict_warnings):
            collect_msg(
                f"Build #{i + 1} schema invalid",
                strict=True,
                summary=summary,
                is_error=True,
            )
            summary.valid = False

    return None


def validate_config(
    parsed_cfg: dict[str, Any],
    *,
    strict: bool | None = None,
) -> ValidationSummary:
    """Validate normalized config. Returns True if valid.

    strict=True  →  warnings become fatal, but still listed separately
    strict=False →  warnings remain non-fatal

    The `strict_config` key in the root config (and optionally in each build)
    controls strictness. CLI flags are not considered.

    Returns a ValidationSummary object.
    """
    logger = get_app_logger()
    logger.trace(f"[validate_config] Starting validation (strict={strict})")

    summary = ValidationSummary(
        valid=True,
        errors=[],
        strict_warnings=[],
        warnings=[],
        strict=DEFAULT_STRICT_CONFIG,
    )
    agg: SchemaErrorAggregator = {}

    # --- Validate root structure ---
    ret = _validate_root(
        parsed_cfg,
        strict_arg=strict,
        summary=summary,
        agg=agg,
    )
    if ret is not None:
        return ret

    # --- Validate builds structure ---
    ret = _validate_builds(parsed_cfg, strict_arg=strict, summary=summary, agg=agg)
    if ret is not None:
        return ret

    # --- finalize result ---
    return _set_valid_and_return(
        summary=summary,
        agg=agg,
    )


# === serger.utils.utils_matching ===
# src/serger/utils/utils_matching.py


def is_excluded(path_entry: PathResolved, exclude_patterns: list[PathResolved]) -> bool:
    """High-level helper for internal use.
    Accepts PathResolved entries and delegates to the smart matcher.
    """
    logger = get_app_logger()
    path = path_entry["path"]
    root = path_entry["root"]
    # Patterns are always normalized to PathResolved["path"] under config_resolve
    patterns = [str(e["path"]) for e in exclude_patterns]
    result = is_excluded_raw(path, patterns, root)
    logger.trace(
        f"[is_excluded] path={path}, root={root},"
        f" patterns={len(patterns)}, excluded={result}"
    )
    return result


# === serger.utils.utils_modules ===
# src/serger/utils/utils_modules.py


def _non_glob_prefix(pattern: str) -> Path:
    """Return the non-glob leading portion of a pattern, as a Path."""
    parts: list[str] = []
    for part in Path(pattern).parts:
        if re.search(r"[*?\[\]]", part):
            break
        parts.append(part)
    return Path(*parts)


def _interpret_dest_for_module_name(  # noqa: PLR0911
    file_path: Path,
    include_root: Path,
    include_pattern: str,
    dest: Path | str,
) -> Path:
    """Interpret dest parameter to compute virtual destination path for module name.

    This adapts logic from _compute_dest() but returns a path that can be used
    for module name derivation, not an actual file system destination.

    Args:
        file_path: The actual source file path
        include_root: Root directory for the include pattern
        include_pattern: Original include pattern string
        dest: Dest parameter (can be pattern, relative path, or explicit override)

    Returns:
        Virtual destination path that should be used for module name derivation
    """
    logger = get_app_logger()
    dest_path = Path(dest)
    include_root_resolved = Path(include_root).resolve()
    file_path_resolved = file_path.resolve()

    logger.trace(
        f"[DEST_INTERPRET] file={file_path}, root={include_root}, "
        f"pattern={include_pattern!r}, dest={dest}",
    )

    # If dest is absolute, use it directly
    if dest_path.is_absolute():
        result = dest_path.resolve()
        logger.trace(f"[DEST_INTERPRET] absolute dest → {result}")
        return result

    # Treat trailing slashes as if they implied recursive includes
    if include_pattern.endswith("/"):
        include_pattern = include_pattern.rstrip("/")
        try:
            rel = file_path_resolved.relative_to(
                include_root_resolved / include_pattern,
            )
            result = dest_path / rel
            logger.trace(
                f"[DEST_INTERPRET] trailing-slash include → rel={rel}, result={result}",
            )
            return result  # noqa: TRY300
        except ValueError:
            logger.trace("[DEST_INTERPRET] trailing-slash fallback (ValueError)")
            return dest_path / file_path.name

    # Handle glob patterns
    if has_glob_chars(include_pattern):
        # Special case: if dest is just a simple name (no path parts) and pattern
        # is a single-level file glob like "a/*.py" (one directory part, then /*.py),
        # use dest directly (explicit override)
        # This handles the case where dest is meant to override the entire module name
        dest_parts = list(dest_path.parts)
        # Count directory parts before the glob (split by / and count non-glob parts)
        pattern_dir_parts = include_pattern.split("/")
        # Remove the glob part (last part containing *)
        non_glob_parts = [
            p
            for p in pattern_dir_parts
            if "*" not in p and "?" not in p and "[" not in p
        ]
        is_single_level_glob = (
            len(dest_parts) == 1
            and len(non_glob_parts) == 1
            and include_pattern.endswith("/*.py")
            and not include_pattern.endswith("/*")
        )
        if is_single_level_glob:
            logger.trace(
                f"[DEST_INTERPRET] explicit dest override → {dest_path}",
            )
            return dest_path

        # For glob patterns, strip non-glob prefix
        prefix = _non_glob_prefix(include_pattern)
        try:
            rel = file_path_resolved.relative_to(include_root_resolved / prefix)
            result = dest_path / rel
            logger.trace(
                f"[DEST_INTERPRET] glob include → prefix={prefix}, "
                f"rel={rel}, result={result}",
            )
            return result  # noqa: TRY300
        except ValueError:
            logger.trace("[DEST_INTERPRET] glob fallback (ValueError)")
            return dest_path / file_path.name

    # For literal includes, check if dest is a full path (ends with .py)
    # If so, use it directly; otherwise preserve structure relative to dest
    dest_str = str(dest_path)
    if dest_str.endswith(".py"):
        # Dest is a full path - use it directly
        logger.trace(
            f"[DEST_INTERPRET] literal include with full dest path → {dest_path}",
        )
        return dest_path

    # Dest is a directory prefix - preserve structure relative to dest
    try:
        rel = file_path_resolved.relative_to(include_root_resolved)
        result = dest_path / rel
        logger.trace(f"[DEST_INTERPRET] literal include → rel={rel}, result={result}")
        return result  # noqa: TRY300
    except ValueError:
        # Fallback when file_path isn't under include_root
        logger.trace(
            f"[DEST_INTERPRET] fallback (file not under root) → "
            f"using name={file_path.name}",
        )
        return dest_path / file_path.name


def derive_module_name(
    file_path: Path,
    package_root: Path,
    include: IncludeResolved | None = None,
) -> str:
    """Derive module name from file path for shim generation.

    Default behavior: Preserve directory structure from file path relative to
    package root. With dest: Preserve structure from dest path instead.

    Args:
        file_path: The file path to derive module name from
        package_root: Common root of all included files
        include: Optional include that produced this file (for dest access)

    Returns:
        Derived module name (e.g., "core.base" from "src/core/base.py")

    Raises:
        ValueError: If module name would be empty or invalid
    """
    logger = get_app_logger()
    file_path_resolved = file_path.resolve()
    package_root_resolved = package_root.resolve()

    # Check if include has dest override
    if include and include.get("dest"):
        dest_raw = include.get("dest")
        # dest is Path | None, but we know it's truthy from the if check
        if dest_raw is None:
            # This shouldn't happen due to the if check, but satisfy type checker
            dest: Path | str = Path()
        else:
            dest = dest_raw  # dest_raw is Path here
        include_root = Path(include["root"]).resolve()
        include_pattern = str(include["path"])

        # Use _interpret_dest_for_module_name to get virtual destination path
        dest_path = _interpret_dest_for_module_name(
            file_path_resolved,
            include_root,
            include_pattern,
            dest,
        )

        # Convert dest path to module name, preserving directory structure
        # custom/sub/foo.py → custom.sub.foo
        parts = list(dest_path.parts)
        if parts and parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]  # Remove .py extension
        elif parts and parts[-1].endswith("/"):
            # Trailing slash means directory - use as-is but might need adjustment
            parts[-1] = parts[-1].rstrip("/")

        # Filter out empty parts and join
        parts = [p for p in parts if p]
        if not parts:
            xmsg = f"Cannot derive module name from dest path: {dest_path}"
            raise ValueError(xmsg)

        module_name = ".".join(parts)
        logger.trace(
            f"[DERIVE] file={file_path}, dest={dest} → module={module_name}",
        )
        return module_name

    # Default: derive from file path relative to package root, preserving structure
    try:
        rel_path = file_path_resolved.relative_to(package_root_resolved)
    except ValueError:
        # File not under package root - use just filename
        logger.trace(
            f"[DERIVE] file={file_path} not under root={package_root}, using filename",
        )
        rel_path = Path(file_path.name)

    # Convert path to module name, preserving directory structure
    # path/to/file.py → path.to.file
    parts = list(rel_path.parts)
    if parts and parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]  # Remove .py extension

    # Filter out empty parts
    parts = [p for p in parts if p]
    if not parts:
        xmsg = f"Cannot derive module name from file path: {file_path}"
        raise ValueError(xmsg)

    module_name = ".".join(parts)
    logger.trace(f"[DERIVE] file={file_path} → module={module_name}")
    return module_name


# === serger.config.config_loader ===
# src/serger/config/config_loader.py


def can_run_configless(args: argparse.Namespace) -> bool:
    """To run without config we need at least --include
    or --add-include or a positional include.

    Since this is pre-args normalization we need to still check
    positionals and not assume the positional out doesn't improperly
    greed grab the include.
    """
    return bool(
        getattr(args, "include", None)
        or getattr(args, "add_include", None)
        or getattr(args, "positional_include", None)
        or getattr(args, "positional_out", None),
    )


def find_config(
    args: argparse.Namespace,
    cwd: Path,
    *,
    missing_level: str = "error",
) -> Path | None:
    """Locate a configuration file.

    missing_level: log-level for failing to find a configuration file.

    Search order:
      1. Explicit path from CLI (--config)
      2. Default candidates in the current working directory:
         .{PROGRAM_CONFIG}.py, .{PROGRAM_CONFIG}.jsonc, .{PROGRAM_CONFIG}.json

    Returns the first matching path, or None if no config was found.
    """
    # NOTE: We only have early no-config Log-Level
    logger = get_app_logger()

    level = logger.resolve_level_name(missing_level)
    if level is None:
        logger.error("Invalid log level name in find_config(): %s", missing_level)
        missing_level = "error"

    # --- 1. Explicit config path ---
    if getattr(args, "config", None):
        config = Path(args.config).expanduser().resolve()
        logger.trace(f"[find_config] Checking explicit path: {config}")
        if not config.exists():
            # Explicit path → hard failure
            xmsg = f"Specified config file not found: {config}"
            raise FileNotFoundError(xmsg)
        if config.is_dir():
            xmsg = f"Specified config path is a directory, not a file: {config}"
            raise ValueError(xmsg)
        return config

    # --- 2. Default candidate files (search current dir and parents) ---
    # Search from cwd up to filesystem root, returning first match (closest to cwd)
    current = cwd
    candidate_names = [
        f".{PROGRAM_CONFIG}.py",
        f".{PROGRAM_CONFIG}.jsonc",
        f".{PROGRAM_CONFIG}.json",
    ]
    found: list[Path] = []
    while True:
        for name in candidate_names:
            candidate = current / name
            if candidate.exists():
                found.append(candidate)
        if found:
            # Found at least one config file at this level
            break
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    if not found:
        # Expected absence — soft failure (continue)
        logger.log_dynamic(missing_level, f"No config file found in {cwd} or parents")
        return None

    # --- 3. Handle multiple matches at same level (prefer .py > .jsonc > .json) ---
    if len(found) > 1:
        # Prefer .py, then .jsonc, then .json
        priority = {".py": 0, ".jsonc": 1, ".json": 2}
        found_sorted = sorted(found, key=lambda p: priority.get(p.suffix, 99))
        names = ", ".join(p.name for p in found_sorted)
        logger.warning(
            "Multiple config files detected (%s); using %s.",
            names,
            found_sorted[0].name,
        )
        return found_sorted[0]
    return found[0]


def load_config(config_path: Path) -> dict[str, Any] | list[Any] | None:
    """Load configuration data from a file.

    Supports:
      - Python configs: .py files exporting either `config`, `builds`, or `includes`
      - JSON/JSONC configs: .json, .jsonc files

    Returns:
        The raw object defined in the config (dict, list, or None).
        Returns None for intentionally empty configs
          (e.g. empty files or `config = None`).

    Raises:
        ValueError if a .py config defines none of the expected variables.

    """
    # NOTE: We only have early no-config Log-Level
    logger = get_app_logger()
    logger.trace(f"[load_config] Loading from {config_path} ({config_path.suffix})")

    # --- Python config ---
    if config_path.suffix == ".py":
        config_globals: dict[str, Any] = {}

        # Allow local imports in Python configs (e.g. from ./helpers import foo)
        # This is safe because configs are trusted user code.
        parent_dir = str(config_path.parent)
        added_to_sys_path = parent_dir not in sys.path
        if added_to_sys_path:
            sys.path.insert(0, parent_dir)

        # Execute the python config file
        try:
            source = config_path.read_text(encoding="utf-8")
            exec(compile(source, str(config_path), "exec"), config_globals)  # noqa: S102
            logger.trace(
                f"[EXEC] globals after exec: {list(config_globals.keys())}",
            )
        except Exception as e:
            tb = traceback.format_exc()
            xmsg = (
                f"Error while executing Python config: {config_path.name}\n"
                f"{type(e).__name__}: {e}\n{tb}"
            )
            # Raise a generic runtime error for main() to catch and print cleanly
            raise RuntimeError(xmsg) from e
        finally:
            # Only remove if we actually inserted it
            if added_to_sys_path and sys.path[0] == parent_dir:
                sys.path.pop(0)

        for key in ("config", "builds", "includes"):
            if key in config_globals:
                result = config_globals[key]
                if not isinstance(result, (dict, list, type(None))):
                    xmsg = (
                        f"{key} in {config_path.name} must be a dict, list, or None"
                        f", not {type(result).__name__}"
                    )
                    raise TypeError(xmsg)

                # Explicitly narrow the loaded config to its expected union type.
                return cast("dict[str, Any] | list[Any] | None", result)

        xmsg = f"{config_path.name} did not define `config` or `builds` or `includes`"
        raise ValueError(xmsg)

    # JSONC / JSON fallback
    try:
        return load_jsonc(config_path)
    except ValueError as e:
        clean_msg = remove_path_in_error_message(str(e), config_path)
        xmsg = (
            f"Error while loading configuration file '{config_path.name}': {clean_msg}"
        )
        raise ValueError(xmsg) from e


def _parse_case_2_list_of_strings(
    raw_config: list[str],
) -> dict[str, Any]:
    # --- Case 2: naked list of strings → single build's include ---
    return {"builds": [{"include": list(raw_config)}]}


def _parse_case_3_list_of_dicts(
    raw_config: list[dict[str, Any]],
) -> dict[str, Any]:
    # --- Case 3: naked list of dicts (no root) → multi-build shorthand ---
    root: dict[str, Any]  # type it once
    builds = [dict(b) for b in raw_config]

    # Lift watch_interval from the first build that defines it (convenience),
    # then remove it from ALL builds to avoid ambiguity.
    first_watch = next(
        (b.get("watch_interval") for b in builds if "watch_interval" in b),
        None,
    )
    root = {"builds": builds}
    if first_watch is not None:
        root["watch_interval"] = first_watch
        for b in builds:
            b.pop("watch_interval", None)
    return root


def _parse_case_4_dict_multi_builds(
    raw_config: dict[str, Any],
    *,
    build_val: Any,
) -> dict[str, Any]:
    # --- Case 4: dict with "build(s)" key → root with multi-builds ---
    logger = get_app_logger()
    root = dict(raw_config)  # preserve all user keys

    # we might have a "builds" key that is a list, then nothing to do

    # If user used "build" with a list → coerce, warn
    if isinstance(build_val, list) and "builds" not in raw_config:
        logger.warning("Config key 'build' was a list — treating as 'builds'.")
        root["builds"] = build_val
        root.pop("build", None)

    return root


def _parse_case_5_dict_single_build(
    raw_config: dict[str, Any],
    *,
    builds_val: Any,
) -> dict[str, Any]:
    # --- Case 5: dict with "build(s)" key → root with single-build ---
    logger = get_app_logger()
    root = dict(raw_config)  # preserve all user keys

    # If user used "builds" with a dict → coerce, warn
    if isinstance(builds_val, dict):
        logger.warning("Config key 'builds' was a dict — treating as 'build'.")
        root["builds"] = [builds_val]
        # keep the 'builds' key — it's now properly normalized
    else:
        root["builds"] = [dict(root.pop("build"))]

    # no hoisting since they specified a root
    return root


def _parse_case_6_root_single_build(
    raw_config: dict[str, Any],
) -> dict[str, Any]:
    # --- Case 6: single build fields (hoist only shared keys) ---
    # The user gave a flat single-build config.
    # We move only the overlapping fields (shared between Root and Build)
    # up to the root; all build-only fields stay inside the build entry.
    build = dict(raw_config)
    hoisted: dict[str, Any] = {}

    # Keys on both Root and Build are what we want to hoist up
    root_keys = set(schema_from_typeddict(RootConfig))
    build_keys = set(schema_from_typeddict(BuildConfig))
    hoist_keys = root_keys & build_keys

    # Move shared keys to the root
    for k in hoist_keys:
        if k in build:
            hoisted[k] = build.pop(k)

    # Preserve any extra unknown root-level fields from raw_config
    for k, v in raw_config.items():
        if k not in hoisted:
            build.setdefault(k, v)

    # Construct normalized root
    root: dict[str, Any] = dict(hoisted)
    root["builds"] = [build]

    return root


def parse_config(  # noqa: PLR0911
    raw_config: dict[str, Any] | list[Any] | None,
) -> dict[str, Any] | None:
    """Normalize user config into canonical RootConfig shape (no filesystem work).

    Accepted forms:
      - #1 [] / {}                   → single build with `include` = []
      - #2 ["src/**", "assets/**"]   → single build with those includes
      - #3 [{...}, {...}]            → multi-build list
      - #4 {"builds": [...]}         → multi-build config (returned shape)
      - #5 {"build": {...}}          → single build config with root config
      - #6 {...}                     → single build config

     After normalization:
      - Always returns {"builds": [ ... ]} (at least one empty {} build).
      - Root-level defaults may be present:
          log_level, out, respect_gitignore, watch_interval.
      - Preserves all unknown keys for later validation.
    """
    # NOTE: This function only normalizes shape — it does NOT validate or restrict keys.
    #       Unknown keys are preserved for the validation phase.

    logger = get_app_logger()
    logger.trace(f"[parse_config] Parsing {type(raw_config).__name__}")

    # --- Case 1: empty config → one blank build ---
    # Includes None (empty file / config = None), [] (no builds), and {} (empty object)
    if not raw_config or raw_config == {}:  # handles None, [], {}
        return None

    # --- Case 2: naked list of strings → single build's include ---
    if isinstance(raw_config, list) and all(isinstance(x, str) for x in raw_config):
        logger.trace("[parse_config] Detected case: list of strings")
        return _parse_case_2_list_of_strings(raw_config)

    # --- Case 3: naked list of dicts (no root) → multi-build shorthand ---
    if isinstance(raw_config, list) and all(isinstance(x, dict) for x in raw_config):
        logger.trace("[parse_config] Detected case: list of dicts")
        return _parse_case_3_list_of_dicts(raw_config)

    # --- better error message for mixed lists ---
    if isinstance(raw_config, list):
        xmsg = (
            "Invalid mixed-type list: "
            "all elements must be strings or all must be objects."
        )
        raise TypeError(xmsg)

    # --- From here on, must be a dict ---
    # Defensive check: should be unreachable after list cases above,
    # but kept to guard against future changes or malformed input.
    if not isinstance(raw_config, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        xmsg = (
            f"Invalid top-level value: {type(raw_config).__name__} "
            "(expected object, list of objects, or list of strings)",
        )
        raise TypeError(xmsg)

    builds_val = raw_config.get("builds")
    build_val = raw_config.get("build")

    # --- Case 4: dict with "build(s)" key → root with multi-builds ---
    if isinstance(builds_val, list) or (
        isinstance(build_val, list) and "builds" not in raw_config
    ):
        return _parse_case_4_dict_multi_builds(
            raw_config,
            build_val=build_val,
        )

    # --- Case 5: dict with "build(s)" key → root with single-build ---
    if isinstance(build_val, dict) or isinstance(builds_val, dict):
        return _parse_case_5_dict_single_build(
            raw_config,
            builds_val=builds_val,
        )

    # --- Case 6: single build fields (hoist only shared keys) ---
    return _parse_case_6_root_single_build(
        raw_config,
    )


def _validation_summary(
    summary: ValidationSummary,
    config_path: Path,
) -> None:
    """Pretty-print a validation summary using the standard log() interface."""
    logger = get_app_logger()
    mode = "strict mode" if summary.strict else "lenient mode"

    # --- Build concise counts line ---
    counts: list[str] = []
    if summary.errors:
        counts.append(f"{len(summary.errors)} error{plural(summary.errors)}")
    if summary.strict_warnings:
        counts.append(
            f"{len(summary.strict_warnings)} strict warning"
            f"{plural(summary.strict_warnings)}",
        )
    if summary.warnings:
        counts.append(
            f"{len(summary.warnings)} normal warning{plural(summary.warnings)}",
        )
    counts_msg = f"\nFound {', '.join(counts)}." if counts else ""

    # --- Header (single icon) ---
    if not summary.valid:
        logger.error(
            "Failed to validate configuration file %s (%s).%s",
            config_path.name,
            mode,
            counts_msg,
        )
    elif counts:
        logger.warning(
            "Validated configuration file  %s (%s) with warnings.%s",
            config_path.name,
            mode,
            counts_msg,
        )
    else:
        logger.debug("Validated  %s (%s) successfully.", config_path.name, mode)

    # --- Detailed sections ---
    if summary.errors:
        msg_summary = "\n  • ".join(summary.errors)
        logger.error("\nErrors:\n  • %s", msg_summary)
    if summary.strict_warnings:
        msg_summary = "\n  • ".join(summary.strict_warnings)
        logger.error("\nStrict warnings (treated as errors):\n  • %s", msg_summary)
    if summary.warnings:
        msg_summary = "\n  • ".join(summary.warnings)
        logger.warning("\nWarnings (non-fatal):\n  • %s", msg_summary)


def load_and_validate_config(
    args: argparse.Namespace,
) -> tuple[Path, RootConfig, ValidationSummary] | None:
    """Find, load, parse, and validate the user's configuration.

    Also determines the effective log level (from CLI/env/config/default)
    early, so logging can initialize as soon as possible.

    Returns:
        (config_path, root_cfg, validation_summary)
        if a config file was found and valid, or None if no config was found.

    """
    logger = get_app_logger()
    # warn if cwd doesn't exist, edge case. We might still be able to run
    cwd = Path.cwd().resolve()
    if not cwd.exists():
        logger.warning("Working directory does not exist: %s", cwd)

    # --- Find config file ---
    cwd = Path.cwd().resolve()
    missing_level = "warning" if can_run_configless(args) else "error"
    config_path = find_config(args, cwd, missing_level=missing_level)
    if config_path is None:
        return None

    # --- Load the raw config (dict or list) ---
    raw_config = load_config(config_path)
    if raw_config is None:
        return None

    # --- Early peek for log_level before parsing ---
    # Handles:
    #   - Root configs with "log_level"
    #   - Single-build dicts with "log_level"
    # Skips empty, list, or multi-build roots.
    if isinstance(raw_config, dict):
        raw_log_level = raw_config.get("log_level")
        if isinstance(raw_log_level, str) and raw_log_level:
            logger.setLevel(
                logger.determine_log_level(args=args, root_log_level=raw_log_level)
            )

    # --- Parse structure into final form without types ---
    try:
        parsed_cfg = parse_config(raw_config)
    except TypeError as e:
        xmsg = f"Could not parse config {config_path.name}: {e}"
        raise TypeError(xmsg) from e
    if parsed_cfg is None:
        return None

    # --- Validate schema ---
    validation_result = validate_config(parsed_cfg)
    _validation_summary(validation_result, config_path)
    if not validation_result.valid:
        xmsg = f"Configuration file {config_path.name} contains validation errors."
        exception = ValueError(xmsg)
        exception.silent = True  # type: ignore[attr-defined]
        exception.data = validation_result  # type: ignore[attr-defined]
        raise exception

    # --- Upgrade to RootConfig type ---
    root_cfg: RootConfig = cast_hint(RootConfig, parsed_cfg)
    return config_path, root_cfg, validation_result


# === serger.config.config_resolve ===
# src/serger/config/config_resolve.py


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


@dataclass
class PyprojectMetadata:
    """Metadata extracted from pyproject.toml."""

    name: str = ""
    version: str = ""
    description: str = ""
    license_text: str = ""

    def has_any(self) -> bool:
        """Check if any metadata was found."""
        return bool(self.name or self.version or self.description or self.license_text)


def extract_pyproject_metadata(
    pyproject_path: Path, *, required: bool = False
) -> PyprojectMetadata | None:
    """Extract metadata from pyproject.toml file.

    Extracts name, version, description, and license from the [project] section.
    Uses load_toml() utility which supports Python 3.10 and 3.11+.

    Args:
        pyproject_path: Path to pyproject.toml file
        required: If True, raise RuntimeError when tomli is missing on Python 3.10.
                  If False, return None when unavailable.

    Returns:
        PyprojectMetadata with extracted fields (empty strings if not found),
        or None if unavailable

    Raises:
        RuntimeError: If required=True and TOML parsing is unavailable
    """
    if not pyproject_path.exists():
        return PyprojectMetadata()

    try:
        data = load_toml(pyproject_path, required=required)
        if data is None:
            # TOML parsing unavailable and not required
            return None
        project = data.get("project", {})
    except (FileNotFoundError, ValueError):
        # If parsing fails, return empty metadata
        return PyprojectMetadata()

    # Extract fields from parsed TOML
    name = project.get("name", "")
    version = project.get("version", "")
    description = project.get("description", "")

    # Handle license (can be string or dict with "file" key)
    license_text = ""
    license_val = project.get("license")
    if isinstance(license_val, str):
        license_text = license_val
    elif isinstance(license_val, dict) and "file" in license_val:
        file_val = license_val.get("file")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
        if isinstance(file_val, str):
            filename = file_val
        else:
            filename = str(file_val) if file_val is not None else "LICENSE"  # pyright: ignore[reportUnknownArgumentType]
        license_text = f"See {filename} if distributed alongside this script"

    return PyprojectMetadata(
        name=name if isinstance(name, str) else "",
        version=version if isinstance(version, str) else "",
        description=description if isinstance(description, str) else "",
        license_text=license_text,
    )


def _should_use_pyproject(
    build_cfg: BuildConfig,
    root_cfg: RootConfig | None,
    num_builds: int,
) -> bool:
    """Determine if pyproject.toml should be used for this build.

    Args:
        build_cfg: Build config
        root_cfg: Root config (may be None)
        num_builds: Number of builds in root config

    Returns:
        True if pyproject.toml should be used, False otherwise
    """
    build_use_pyproject = build_cfg.get("use_pyproject")
    root_use_pyproject = (root_cfg or {}).get("use_pyproject")
    build_pyproject_path = build_cfg.get("pyproject_path")

    # Determine if this build has opted in
    build_opted_in = False
    if isinstance(build_use_pyproject, bool):
        build_opted_in = build_use_pyproject
    elif build_pyproject_path:
        # Specifying a path is an implicit opt-in
        build_opted_in = True

    if num_builds > 1:
        # Multi-build: build must explicitly opt-in
        return build_opted_in

    # Single build: use root/default settings unless build explicitly opts out
    if isinstance(build_use_pyproject, bool):
        return build_use_pyproject
    if build_pyproject_path:
        return True
    # Use root setting or default
    if isinstance(root_use_pyproject, bool):
        return root_use_pyproject
    return DEFAULT_USE_PYPROJECT


def _resolve_pyproject_path(
    build_cfg: BuildConfig,
    root_cfg: RootConfig | None,
    config_dir: Path,
) -> Path:
    """Resolve the path to pyproject.toml file.

    Args:
        build_cfg: Build config
        root_cfg: Root config (may be None)
        config_dir: Config directory for path resolution

    Returns:
        Resolved path to pyproject.toml
    """
    build_pyproject_path = build_cfg.get("pyproject_path")
    root_pyproject_path = (root_cfg or {}).get("pyproject_path")

    if build_pyproject_path:
        # Build-level path takes precedence
        return (config_dir / build_pyproject_path).resolve()
    if root_pyproject_path:
        # Root-level path
        return (config_dir / root_pyproject_path).resolve()
    # Default: config_dir / "pyproject.toml" (project root)
    return config_dir / "pyproject.toml"


def _is_explicitly_requested(
    build_cfg: BuildConfig,
    root_cfg: RootConfig | None,
) -> bool:
    """Check if pyproject.toml was explicitly requested (not just default).

    Args:
        build_cfg: Build config
        root_cfg: Root config (may be None)

    Returns:
        True if explicitly requested, False if just default behavior
    """
    build_use_pyproject = build_cfg.get("use_pyproject")
    root_use_pyproject = (root_cfg or {}).get("use_pyproject")
    build_pyproject_path = build_cfg.get("pyproject_path")
    root_pyproject_path = (root_cfg or {}).get("pyproject_path")

    return (
        isinstance(build_use_pyproject, bool)
        or build_pyproject_path is not None
        or isinstance(root_use_pyproject, bool)
        or root_pyproject_path is not None
    )


def _extract_pyproject_metadata_safe(
    pyproject_path: Path,
    *,
    explicitly_requested: bool,
) -> PyprojectMetadata:
    """Extract metadata from pyproject.toml with error handling.

    Args:
        pyproject_path: Path to pyproject.toml
        explicitly_requested: Whether pyproject was explicitly requested

    Returns:
        PyprojectMetadata object (may be empty if unavailable)

    Raises:
        RuntimeError: If explicitly requested and TOML parsing unavailable
    """
    logger = get_app_logger()

    try:
        metadata = extract_pyproject_metadata(
            pyproject_path, required=explicitly_requested
        )
    except RuntimeError as e:
        # If explicitly requested and TOML parsing unavailable, re-raise
        if explicitly_requested:
            xmsg = (
                "pyproject.toml support was explicitly requested but "
                f"TOML parsing is unavailable. {e!s}"
            )
            raise RuntimeError(xmsg) from e
        # If not explicitly requested, this shouldn't happen (should return None)
        raise

    if metadata is None:
        # TOML parsing unavailable but not explicitly requested - warn and skip
        logger.warning(
            "pyproject.toml found but TOML parsing unavailable "
            "(Python 3.10 requires 'tomli'). "
            "Skipping metadata extraction. Install 'tomli' to enable, "
            "or explicitly set 'use_pyproject: false' to disable this warning."
        )
        # Create empty metadata object
        metadata = PyprojectMetadata()

    return metadata


def _apply_metadata_fields(
    resolved_cfg: dict[str, Any],
    metadata: PyprojectMetadata,
    pyproject_path: Path,
) -> None:
    """Apply extracted metadata fields to resolved config.

    Args:
        resolved_cfg: Mutable resolved config dict (modified in place)
        metadata: Extracted metadata
        pyproject_path: Path to pyproject.toml (for logging)
    """
    logger = get_app_logger()

    # Fill in missing fields (only if not already set in config)
    if metadata.version and not resolved_cfg.get("version"):
        # Note: version is not a build config field, but we'll store it
        # for use in build.py later
        resolved_cfg["_pyproject_version"] = metadata.version

    if metadata.name and not resolved_cfg.get("display_name"):
        resolved_cfg["display_name"] = metadata.name

    if metadata.description and not resolved_cfg.get("description"):
        resolved_cfg["description"] = metadata.description

    if metadata.license_text and not resolved_cfg.get("license_header"):
        resolved_cfg["license_header"] = metadata.license_text

    if metadata.has_any():
        logger.trace(f"[resolve_build_config] Extracted metadata from {pyproject_path}")


def _apply_pyproject_metadata(
    resolved_cfg: dict[str, Any],
    *,
    build_cfg: BuildConfig,
    root_cfg: RootConfig | None,
    config_dir: Path,
    num_builds: int,
) -> None:
    """Extract and apply pyproject.toml metadata to resolved config.

    Handles all the logic for determining when to use pyproject.toml,
    path resolution, and filling in missing fields.

    Args:
        resolved_cfg: Mutable resolved config dict (modified in place)
        build_cfg: Original build config
        root_cfg: Root config (may be None)
        config_dir: Config directory for path resolution
        num_builds: Number of builds in the root config
    """
    if not _should_use_pyproject(build_cfg, root_cfg, num_builds):
        return

    pyproject_path = _resolve_pyproject_path(build_cfg, root_cfg, config_dir)
    explicitly_requested = _is_explicitly_requested(build_cfg, root_cfg)

    metadata = _extract_pyproject_metadata_safe(
        pyproject_path, explicitly_requested=explicitly_requested
    )
    _apply_metadata_fields(resolved_cfg, metadata, pyproject_path)


def _load_gitignore_patterns(path: Path) -> list[str]:
    """Read .gitignore and return non-comment patterns."""
    patterns: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                patterns.append(clean_line)
    return patterns


def _merge_post_processing(  # noqa: C901, PLR0912, PLR0915
    build_cfg: PostProcessingConfig | None,
    root_cfg: PostProcessingConfig | None,
) -> PostProcessingConfig:
    """Deep merge post-processing configs: build-level → root-level → default.

    Args:
        build_cfg: Build-level post-processing config (may be None)
        root_cfg: Root-level post-processing config (may be None)

    Returns:
        Merged post-processing config
    """
    # Start with defaults
    merged: PostProcessingConfig = {
        "enabled": True,
        "category_order": list(DEFAULT_CATEGORY_ORDER),
        "categories": {
            cat: {
                "enabled": bool(cfg.get("enabled", True)),
                "priority": (
                    list(cast("list[str]", cfg["priority"]))
                    if isinstance(cfg.get("priority"), list)
                    else []
                ),
            }
            for cat, cfg in DEFAULT_CATEGORIES.items()
        },
    }

    # Merge root-level config
    if root_cfg:
        if "enabled" in root_cfg:
            merged["enabled"] = root_cfg["enabled"]
        if "category_order" in root_cfg:
            merged["category_order"] = list(root_cfg["category_order"])

        if "categories" in root_cfg:
            if "categories" not in merged:
                merged["categories"] = {}
            for cat_name, cat_cfg in root_cfg["categories"].items():
                if cat_name not in merged["categories"]:
                    merged["categories"][cat_name] = {}
                # Merge category config
                merged_cat = merged["categories"][cat_name]
                if "enabled" in cat_cfg:
                    merged_cat["enabled"] = cat_cfg["enabled"]
                if "priority" in cat_cfg:
                    merged_cat["priority"] = list(cat_cfg["priority"])
                if "tools" in cat_cfg:
                    if "tools" not in merged_cat:
                        merged_cat["tools"] = {}
                    # Tool options replace (don't merge)
                    for tool_name, tool_override in cat_cfg["tools"].items():
                        root_override_dict: dict[str, object] = {}
                        if "command" in tool_override:
                            root_override_dict["command"] = tool_override["command"]
                        if "args" in tool_override:
                            root_override_dict["args"] = list(tool_override["args"])
                        if "path" in tool_override:
                            root_override_dict["path"] = tool_override["path"]
                        if "options" in tool_override:
                            root_override_dict["options"] = list(
                                tool_override["options"]
                            )
                        merged_cat["tools"][tool_name] = cast_hint(
                            ToolConfig, root_override_dict
                        )

    # Merge build-level config (overrides root)
    if build_cfg:
        if "enabled" in build_cfg:
            merged["enabled"] = build_cfg["enabled"]
        if "category_order" in build_cfg:
            merged["category_order"] = list(build_cfg["category_order"])

        if "categories" in build_cfg:
            if "categories" not in merged:
                merged["categories"] = {}
            for cat_name, cat_cfg in build_cfg["categories"].items():
                if cat_name not in merged["categories"]:
                    merged["categories"][cat_name] = {}
                # Merge category config
                merged_cat = merged["categories"][cat_name]
                if "enabled" in cat_cfg:
                    merged_cat["enabled"] = cat_cfg["enabled"]
                if "priority" in cat_cfg:
                    merged_cat["priority"] = list(cat_cfg["priority"])
                if "tools" in cat_cfg:
                    if "tools" not in merged_cat:
                        merged_cat["tools"] = {}
                    # Tool options replace (don't merge)
                    for tool_name, tool_override in cat_cfg["tools"].items():
                        build_override_dict: dict[str, object] = {}
                        if "command" in tool_override:
                            build_override_dict["command"] = tool_override["command"]
                        if "args" in tool_override:
                            build_override_dict["args"] = list(tool_override["args"])
                        if "path" in tool_override:
                            build_override_dict["path"] = tool_override["path"]
                        if "options" in tool_override:
                            build_override_dict["options"] = list(
                                tool_override["options"]
                            )
                        merged_cat["tools"][tool_name] = cast_hint(
                            ToolConfig, build_override_dict
                        )

    return merged


def resolve_post_processing(  # noqa: PLR0912, C901
    build_cfg: BuildConfig,
    root_cfg: RootConfig | None,
) -> PostProcessingConfigResolved:
    """Resolve post-processing configuration with cascade and validation.

    Args:
        build_cfg: Build config
        root_cfg: Root config (may be None)

    Returns:
        Resolved post-processing configuration
    """
    logger = get_app_logger()

    # Extract configs
    build_post = build_cfg.get("post_processing")
    root_post = (root_cfg or {}).get("post_processing")

    # Merge configs
    merged = _merge_post_processing(
        build_post if isinstance(build_post, dict) else None,
        root_post if isinstance(root_post, dict) else None,
    )

    # Validate category_order - warn on invalid category names
    valid_categories = set(DEFAULT_CATEGORIES.keys())
    category_order = merged.get("category_order", DEFAULT_CATEGORY_ORDER)
    invalid_categories = [cat for cat in category_order if cat not in valid_categories]
    if invalid_categories:
        logger.warning(
            "Invalid category names in post_processing.category_order: %s. "
            "Valid categories are: %s",
            invalid_categories,
            sorted(valid_categories),
        )

    # Helper function to resolve a ToolConfig to ToolConfigResolved with all fields
    def _resolve_tool_config(
        tool_label: str, tool_config: ToolConfig | dict[str, Any]
    ) -> ToolConfigResolved:
        """Resolve a ToolConfig to ToolConfigResolved with all fields populated."""
        # Ensure we have a dict (ToolConfig is a TypedDict, which is a dict)
        tool_dict = cast("dict[str, Any]", tool_config)

        # Args is required - if not present, this is an error
        if "args" not in tool_dict:
            xmsg = f"Tool config for {tool_label} is missing required 'args' field"
            raise ValueError(xmsg)

        resolved: ToolConfigResolved = {
            "command": tool_dict.get("command", tool_label),
            "args": list(tool_dict["args"]),
            "path": tool_dict.get("path"),
            "options": list(tool_dict.get("options", [])),
        }
        return resolved

    # Build resolved config with all categories (even if not in category_order)
    resolved_categories: dict[str, PostCategoryConfigResolved] = {}
    for cat_name, default_cat in DEFAULT_CATEGORIES.items():
        # Start with defaults
        enabled_val = default_cat.get("enabled", True)
        priority_val = default_cat.get("priority", [])
        priority_list = (
            list(cast("list[str]", priority_val))
            if isinstance(priority_val, list)
            else []
        )

        # Build tools dict from defaults
        tools_dict: dict[str, ToolConfigResolved] = {}
        if "tools" in default_cat:
            for tool_name, tool_override in default_cat["tools"].items():
                tools_dict[tool_name] = _resolve_tool_config(tool_name, tool_override)

        # Apply merged config if present
        if "categories" in merged and cat_name in merged["categories"]:
            merged_cat = merged["categories"][cat_name]
            if "enabled" in merged_cat:
                enabled_val = merged_cat["enabled"]
            if "priority" in merged_cat:
                priority_list = list(merged_cat["priority"])
            if "tools" in merged_cat:
                # Merge tools: user config overrides defaults
                for tool_name, tool_override in merged_cat["tools"].items():
                    # Merge with existing tool config if present, otherwise use override
                    existing_tool_raw: ToolConfigResolved | dict[str, Any] = (
                        tools_dict.get(tool_name, {})
                    )
                    existing_tool: dict[str, Any] = cast(
                        "dict[str, Any]", existing_tool_raw
                    )
                    merged_tool: dict[str, Any] = dict(existing_tool)
                    # Update with user override (may be partial)
                    if isinstance(tool_override, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
                        merged_tool.update(tool_override)
                    tools_dict[tool_name] = _resolve_tool_config(tool_name, merged_tool)

        # Fallback: ensure all tools in priority are in tools dict
        # If a tool is in priority but not in tools, look it up from DEFAULT_CATEGORIES
        default_tools = default_cat.get("tools", {})
        for tool_label in priority_list:
            if tool_label not in tools_dict and tool_label in default_tools:
                # Copy from defaults as fallback
                default_override = default_tools[tool_label]
                tools_dict[tool_label] = _resolve_tool_config(
                    tool_label, default_override
                )

        # Empty priority = disabled
        if not priority_list:
            enabled_val = False

        resolved_cat: PostCategoryConfigResolved = {
            "enabled": bool(enabled_val) if isinstance(enabled_val, bool) else True,
            "priority": priority_list,
            "tools": tools_dict,
        }

        resolved_categories[cat_name] = resolved_cat

    resolved: PostProcessingConfigResolved = {
        "enabled": merged.get("enabled", True),
        "category_order": list(category_order),
        "categories": resolved_categories,
    }

    return resolved


def _parse_include_with_dest(
    raw: str, context_root: Path
) -> tuple[IncludeResolved, bool]:
    """Parse include string with optional :dest suffix.

    Returns:
        (IncludeResolved, has_dest) tuple
    """
    has_dest = False
    path_str = raw
    dest_str = None

    # Handle "path:dest" format - split on last colon
    if ":" in raw:
        parts = raw.rsplit(":", 1)
        path_part, dest_part = parts[0], parts[1]

        # Check if this is a Windows drive letter (C:, D:, etc.)
        # Drive letters are 1-2 chars, possibly with backslash
        is_drive_letter = len(path_part) <= 2 and (  # noqa: PLR2004
            len(path_part) == 1 or path_part.endswith("\\")
        )

        if not is_drive_letter:
            # Valid dest separator found
            path_str = path_part
            dest_str = dest_part
            has_dest = True

    # Normalize the path
    root, rel = _normalize_path_with_root(path_str, context_root)
    inc = make_includeresolved(rel, root, "cli")

    if has_dest and dest_str:
        inc["dest"] = Path(dest_str)

    return inc, has_dest


def _normalize_path_with_root(
    raw: Path | str,
    context_root: Path | str,
) -> tuple[Path, Path | str]:
    """Normalize a user-provided path (from CLI or config).

    - If absolute → treat that path as its own root.
      * `/abs/path/**` → root=/abs/path, rel="**"
      * `/abs/path/`   → root=/abs/path, rel="**"  (treat as contents)
      * `/abs/path`    → root=/abs/path, rel="."   (treat as literal)
    - If relative → root = context_root, path = raw (preserve string form)
    """
    logger = get_app_logger()
    raw_path = Path(raw)
    rel: Path | str

    # --- absolute path case ---
    if raw_path.is_absolute():
        # Split out glob or trailing slash intent
        raw_str = str(raw)
        if raw_str.endswith("/**"):
            root = Path(raw_str[:-3]).resolve()
            rel = "**"
        elif raw_str.endswith("/"):
            root = Path(raw_str[:-1]).resolve()
            rel = "**"  # treat directory as contents
        elif has_glob_chars(raw_str):
            # Extract root directory (part before first glob char)
            # Find the last path separator before any glob character
            glob_chars = ["*", "?", "[", "{"]
            glob_pos = min(
                (raw_str.find(c) for c in glob_chars if c in raw_str),
                default=len(raw_str),
            )
            # Find the last / before the glob
            path_before_glob = raw_str[:glob_pos]
            last_slash = path_before_glob.rfind("/")
            if last_slash >= 0:
                root = Path(path_before_glob[:last_slash] or "/").resolve()
                rel = raw_str[last_slash + 1 :]  # Pattern part after root
            else:
                # No slash found, treat entire path as root
                root = Path("/").resolve()
                rel = raw_str.removeprefix("/")
        else:
            root = raw_path.resolve()
            rel = "."
    else:
        root = Path(context_root).resolve()
        # preserve literal string if user provided one
        rel = raw if isinstance(raw, str) else Path(raw)

    logger.trace(f"Normalized: raw={raw!r} → root={root}, rel={rel}")
    return root, rel


# --------------------------------------------------------------------------- #
# main per-build resolver
# --------------------------------------------------------------------------- #


def _resolve_includes(  # noqa: PLR0912
    resolved_cfg: dict[str, Any],
    *,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
) -> list[IncludeResolved]:
    logger = get_app_logger()
    logger.trace(
        f"[resolve_includes] Starting with"
        f" {len(resolved_cfg.get('include', []))} config includes"
    )

    includes: list[IncludeResolved] = []

    if getattr(args, "include", None):
        # Full override → relative to cwd
        for raw in args.include:
            inc, _ = _parse_include_with_dest(raw, cwd)
            includes.append(inc)

    elif "include" in resolved_cfg:
        # From config → relative to config_dir
        # Type narrowing: resolved_cfg is dict[str, Any], narrow the include list
        include_list: list[str | dict[str, str]] = cast(
            "list[str | dict[str, str]]", resolved_cfg["include"]
        )
        for raw in include_list:
            # Handle both string and object formats
            if isinstance(raw, dict):
                # Object format: {"path": "...", "dest": "..."}
                path_str = raw.get("path", "")
                dest_str = raw.get("dest")
                root, rel = _normalize_path_with_root(path_str, config_dir)
                inc = make_includeresolved(rel, root, "config")
                if dest_str:
                    # dest is relative to output dir, no normalization
                    inc["dest"] = Path(dest_str)
                includes.append(inc)
            else:
                # String format: "path/to/files"
                root, rel = _normalize_path_with_root(raw, config_dir)
                includes.append(make_includeresolved(rel, root, "config"))

    # Add-on includes (extend, not override)
    if getattr(args, "add_include", None):
        for raw in args.add_include:
            inc, _ = _parse_include_with_dest(raw, cwd)
            includes.append(inc)

    # unique path+root
    seen_inc: set[tuple[Path | str, Path]] = set()
    unique_inc: list[IncludeResolved] = []
    for i in includes:
        key = (i["path"], i["root"])
        if key not in seen_inc:
            seen_inc.add(key)
            unique_inc.append(i)

            # Check root existence
            if not i["root"].exists():
                logger.warning(
                    "Include root does not exist: %s (origin: %s)",
                    i["root"],
                    i["origin"],
                )

            # Check path existence
            if not has_glob_chars(str(i["path"])):
                full_path = i["root"] / i["path"]  # absolute paths override root
                if not full_path.exists():
                    logger.warning(
                        "Include path does not exist: %s (origin: %s)",
                        full_path,
                        i["origin"],
                    )

    return unique_inc


def _resolve_excludes(
    resolved_cfg: dict[str, Any],
    *,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
    root_cfg: RootConfig | None,
) -> list[PathResolved]:
    logger = get_app_logger()
    logger.trace(
        f"[resolve_excludes] Starting with"
        f" {len(resolved_cfg.get('exclude', []))} config excludes"
    )

    excludes: list[PathResolved] = []

    def _add_excludes(paths: list[str], context: Path, origin: OriginType) -> None:
        # Exclude patterns (from CLI, config, or gitignore) should stay literal
        excludes.extend(make_pathresolved(raw, context, origin) for raw in paths)

    if getattr(args, "exclude", None):
        # Full override → relative to cwd
        # Keep CLI-provided exclude patterns as-is (do not resolve),
        # since glob patterns like "*.tmp" should match relative paths
        # beneath the include root, not absolute paths.
        _add_excludes(args.exclude, cwd, "cli")
    elif "exclude" in resolved_cfg:
        # From config → relative to config_dir
        _add_excludes(resolved_cfg["exclude"], config_dir, "config")

    # Add-on excludes (extend, not override)
    if getattr(args, "add_exclude", None):
        _add_excludes(args.add_exclude, cwd, "cli")

    # --- Merge .gitignore patterns into excludes if enabled ---
    # Determine whether to respect .gitignore
    if getattr(args, "respect_gitignore", None) is not None:
        respect_gitignore = args.respect_gitignore
    elif "respect_gitignore" in resolved_cfg:
        respect_gitignore = resolved_cfg["respect_gitignore"]
    else:
        # fallback — true by default, overridden by root config if needed
        respect_gitignore = (root_cfg or {}).get(
            "respect_gitignore",
            DEFAULT_RESPECT_GITIGNORE,
        )

    if respect_gitignore:
        gitignore_path = config_dir / ".gitignore"
        patterns = _load_gitignore_patterns(gitignore_path)
        if patterns:
            logger.trace(
                f"Adding {len(patterns)} .gitignore patterns from {gitignore_path}",
            )
        _add_excludes(patterns, config_dir, "gitignore")

    resolved_cfg["respect_gitignore"] = respect_gitignore

    # unique path+root
    seen_exc: set[tuple[Path | str, Path]] = set()
    unique_exc: list[PathResolved] = []
    for ex in excludes:
        key = (ex["path"], ex["root"])
        if key not in seen_exc:
            seen_exc.add(key)
            unique_exc.append(ex)

    return unique_exc


def _resolve_output(
    resolved_cfg: dict[str, Any],
    *,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
) -> PathResolved:
    logger = get_app_logger()
    logger.trace("[resolve_output] Resolving output directory")

    if getattr(args, "out", None):
        # Full override → relative to cwd
        root, rel = _normalize_path_with_root(args.out, cwd)
        out_wrapped = make_pathresolved(rel, root, "cli")
    elif "out" in resolved_cfg:
        # From config → relative to config_dir
        root, rel = _normalize_path_with_root(resolved_cfg["out"], config_dir)
        out_wrapped = make_pathresolved(rel, root, "config")
    else:
        root, rel = _normalize_path_with_root(DEFAULT_OUT_DIR, cwd)
        out_wrapped = make_pathresolved(rel, root, "default")

    return out_wrapped


def resolve_build_config(
    build_cfg: BuildConfig,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
    root_cfg: RootConfig | None = None,
) -> BuildConfigResolved:
    """Resolve a single BuildConfig into a BuildConfigResolved.

    Applies CLI overrides, normalizes paths, merges gitignore behavior,
    and attaches provenance metadata.
    """
    logger = get_app_logger()
    logger.trace("[resolve_build_config] Starting resolution for build config")

    # Make a mutable copy
    resolved_cfg: dict[str, Any] = dict(build_cfg)

    # root provenance for all resolutions
    meta: MetaBuildConfigResolved = {
        "cli_root": cwd,
        "config_root": config_dir,
    }

    # --- Includes ---------------------------
    resolved_cfg["include"] = _resolve_includes(
        resolved_cfg,
        args=args,
        config_dir=config_dir,
        cwd=cwd,
    )
    logger.trace(
        f"[resolve_build_config] Resolved {len(resolved_cfg['include'])} include(s)"
    )

    # --- Excludes ---------------------------
    resolved_cfg["exclude"] = _resolve_excludes(
        resolved_cfg,
        args=args,
        config_dir=config_dir,
        cwd=cwd,
        root_cfg=root_cfg,
    )
    logger.trace(
        f"[resolve_build_config] Resolved {len(resolved_cfg['exclude'])} exclude(s)"
    )

    # --- Output ---------------------------
    resolved_cfg["out"] = _resolve_output(
        resolved_cfg,
        args=args,
        config_dir=config_dir,
        cwd=cwd,
    )

    # ------------------------------
    # Log level
    # ------------------------------
    build_log = resolved_cfg.get("log_level")
    root_log = (root_cfg or {}).get("log_level")
    resolved_cfg["log_level"] = logger.determine_log_level(
        args=args, root_log_level=root_log, build_log_level=build_log
    )

    # ------------------------------
    # Strict config
    # ------------------------------
    # Cascade: build-level → root-level → default
    build_strict = resolved_cfg.get("strict_config")
    root_strict = (root_cfg or {}).get("strict_config")
    if isinstance(build_strict, bool):
        resolved_cfg["strict_config"] = build_strict
    elif isinstance(root_strict, bool):
        resolved_cfg["strict_config"] = root_strict
    else:
        resolved_cfg["strict_config"] = DEFAULT_STRICT_CONFIG

    # ------------------------------
    # Post-processing
    # ------------------------------
    # Cascade: build-level → root-level → default
    resolved_cfg["post_processing"] = resolve_post_processing(build_cfg, root_cfg)

    # ------------------------------
    # Pyproject.toml metadata
    # ------------------------------
    num_builds = len((root_cfg or {}).get("builds", []))
    _apply_pyproject_metadata(
        resolved_cfg,
        build_cfg=build_cfg,
        root_cfg=root_cfg,
        config_dir=config_dir,
        num_builds=num_builds,
    )

    # ------------------------------
    # Attach provenance
    # ------------------------------
    resolved_cfg["__meta__"] = meta
    return cast_hint(BuildConfigResolved, resolved_cfg)


# --------------------------------------------------------------------------- #
# root-level resolver
# --------------------------------------------------------------------------- #


def resolve_config(
    root_input: RootConfig,
    args: argparse.Namespace,
    config_dir: Path,
    cwd: Path,
) -> RootConfigResolved:
    """Fully resolve a loaded RootConfig into a ready-to-run RootConfigResolved.

    If invoked standalone, ensures the global logger reflects the resolved log level.
    If called after load_and_validate_config(), this is a harmless no-op re-sync."""
    logger = get_app_logger()
    root_cfg = cast_hint(RootConfig, dict(root_input))

    builds_input = root_cfg.get("builds", [])
    logger.trace(
        f"[resolve_config] Resolving root config with {len(builds_input)} build(s)"
    )

    # ------------------------------
    # Watch interval
    # ------------------------------
    env_watch = os.getenv(DEFAULT_ENV_WATCH_INTERVAL)
    if getattr(args, "watch", None) is not None:
        watch_interval = args.watch
    elif env_watch is not None:
        try:
            watch_interval = float(env_watch)
        except ValueError:
            logger.warning(
                "Invalid %s=%r, using default.", DEFAULT_ENV_WATCH_INTERVAL, env_watch
            )
            watch_interval = DEFAULT_WATCH_INTERVAL
    else:
        watch_interval = root_cfg.get("watch_interval", DEFAULT_WATCH_INTERVAL)

    logger.trace(f"[resolve_config] Watch interval resolved to {watch_interval}s")

    # ------------------------------
    # Log level
    # ------------------------------
    #  log_level: arg -> env -> build -> root -> default
    root_log = root_cfg.get("log_level")
    log_level = logger.determine_log_level(args=args, root_log_level=root_log)

    # --- sync runtime ---
    logger.setLevel(log_level)

    # ------------------------------
    # Resolve builds
    # ------------------------------
    resolved_builds = [
        resolve_build_config(b, args, config_dir, cwd, root_cfg) for b in builds_input
    ]

    # ------------------------------
    # Post-processing
    # ------------------------------
    # For root-level, create a dummy build config to use the same resolution function
    dummy_build: BuildConfig = {}
    post_processing = resolve_post_processing(dummy_build, root_cfg)

    resolved_root: RootConfigResolved = {
        "builds": resolved_builds,
        "strict_config": root_cfg.get("strict_config", False),
        "watch_interval": watch_interval,
        "log_level": log_level,
        "post_processing": post_processing,
    }

    return resolved_root


# === serger.verify_script ===
# src/serger/verify_script.py
"""Script verification and post-processing utilities.

This module provides functions for verifying stitched Python scripts,
including compilation checks, ruff formatting, and execution validation.
"""


def verify_compiles(file_path: Path) -> bool:
    """Verify that a Python file compiles without syntax errors.

    Args:
        file_path: Path to Python file to check

    Returns:
        True if file compiles successfully, False otherwise
    """
    logger = get_app_logger()
    try:
        py_compile.compile(str(file_path), doraise=True)
    except py_compile.PyCompileError as e:
        lineno = getattr(e, "lineno", "unknown")
        logger.debug("Compilation error at line %s: %s", lineno, e.msg)
        return False
    except FileNotFoundError:
        logger.debug("File not found: %s", file_path)
        return False
    else:
        logger.debug("File compiles successfully: %s", file_path)
        return True


def find_tool_executable(
    tool_name: str,
    custom_path: str | None = None,
) -> str | None:
    """Find tool executable, checking custom_path first, then PATH.

    Args:
        tool_name: Name of the tool to find
        custom_path: Optional custom path to the executable

    Returns:
        Path to executable if found, None otherwise
    """
    if custom_path:
        path = Path(custom_path)
        if path.exists() and path.is_file():
            return str(path.resolve())
        # If custom path doesn't exist, fall back to PATH

    return shutil.which(tool_name)


def build_tool_command(
    tool_label: str,
    _category: str,
    file_path: Path,
    _tool_override: ToolConfigResolved | None = None,
    tools_dict: dict[str, ToolConfigResolved] | None = None,
) -> list[str] | None:
    """Build the full command to execute a tool.

    Args:
        tool_label: Tool name or custom label (simple tool name or custom instance)
        _category: Category name (static_checker, formatter, import_sorter) -
            unused, kept for API compatibility
        file_path: Path to the file to process
        _tool_override: Optional tool override config (deprecated, unused)
        tools_dict: Dict of resolved tool configs keyed by label
            (includes defaults from resolved config)

    Returns:
        Command list if tool is available, None otherwise
    """
    # Look up tool in tools_dict (includes defaults from resolved config)
    if tools_dict and tool_label in tools_dict:
        tool_config = tools_dict[tool_label]
        actual_tool_name = tool_config["command"]
        base_args = tool_config["args"]
        extra = tool_config["options"]
        custom_path = tool_config["path"]
    else:
        # Tool not found in tools_dict - not supported
        # (All tools should be in tools dict, including defaults)
        return None

    # Find executable
    executable = find_tool_executable(actual_tool_name, custom_path=custom_path)
    if not executable:
        return None

    return [executable, *base_args, *extra, str(file_path)]


def execute_post_processing(
    file_path: Path,
    config: PostProcessingConfigResolved,
) -> None:
    """Execute post-processing tools on a file according to configuration.

    Args:
        file_path: Path to the file to process
        config: Resolved post-processing configuration
    """
    logger = get_app_logger()

    if not config["enabled"]:
        logger.debug("Post-processing disabled, skipping")
        return

    # Track executed commands for deduplication
    executed_commands: set[tuple[str, ...]] = set()

    # Process categories in order
    for category_name in config["category_order"]:
        if category_name not in config["categories"]:
            continue

        category = config["categories"][category_name]
        if not category["enabled"]:
            logger.debug("Category %s is disabled, skipping", category_name)
            continue

        priority = category["priority"]
        if not priority:
            logger.debug("Category %s has empty priority, skipping", category_name)
            continue

        # Try tools in priority order
        tool_ran = False
        tools_dict = category["tools"]
        for tool_label in priority:
            # Tool should be in tools dict (guaranteed by resolution)
            tool_config = (
                tools_dict.get(tool_label) if tool_label in tools_dict else None
            )
            command = build_tool_command(
                tool_label, category_name, file_path, tool_config, tools_dict
            )

            if command is None:
                logger.debug(
                    "Tool %s not available or doesn't support category %s",
                    tool_label,
                    category_name,
                )
                continue

            # Deduplicate: skip if we've already run this exact command
            command_tuple = tuple(command)
            if command_tuple in executed_commands:
                logger.debug("Skipping duplicate command: %s", " ".join(command))
                continue

            # Execute command
            logger.debug("Running %s for category %s", tool_label, category_name)
            try:
                result = subprocess.run(  # noqa: S603
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    logger.debug(
                        "%s completed successfully for category %s",
                        tool_label,
                        category_name,
                    )
                    tool_ran = True
                    executed_commands.add(command_tuple)
                    break  # Success, move to next category
                logger.debug(
                    "%s exited with code %d: %s",
                    tool_label,
                    result.returncode,
                    result.stderr or result.stdout,
                )
            except Exception as e:  # noqa: BLE001
                logger.debug("Error running %s: %s", tool_label, e)

        if not tool_ran:
            logger.debug(
                "No tool succeeded for category %s (tried: %s)",
                category_name,
                priority,
            )


def verify_executes(file_path: Path) -> bool:
    """Verify that a Python script can be executed (basic sanity check).

    First tries to run the script with --help (common CLI flag), then falls back
    to compilation check if that fails. This provides a lightweight execution
    verification without requiring full functionality testing.

    Args:
        file_path: Path to Python script to check

    Returns:
        True if script executes without immediate errors, False otherwise
    """
    logger = get_app_logger()

    # Check if file exists first
    if not file_path.exists():
        logger.debug("File does not exist: %s", file_path)
        return False

    # First, try to actually execute the script with --help
    # This verifies the script can run, not just compile
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(file_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # Exit code 0 or 2 (help typically exits with 0 or 2)
        if result.returncode in (0, 2):
            logger.debug("Script executes successfully (--help): %s", file_path)
            return True
        # If --help fails, try --version as fallback
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(file_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode in (0, 2):
            logger.debug("Script executes successfully (--version): %s", file_path)
            return True
    except Exception as e:  # noqa: BLE001
        logger.debug("Error running script with --help/--version: %s", e)

    # Fallback: verify it compiles (lightweight check)
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            logger.debug("Script compiles successfully: %s", file_path)
            return True
        logger.debug(
            "Script execution check failed: %s", result.stderr or result.stdout
        )
    except Exception as e:  # noqa: BLE001
        logger.debug("Error during compilation check: %s", e)

    return False


def post_stitch_processing(
    out_path: Path,
    *,
    post_processing: PostProcessingConfigResolved | None = None,
) -> None:
    """Post-process a stitched file with tools, compilation checks, and verification.

    This function:
    1. Compiles the file before post-processing
    2. Runs configured post-processing tools (static checker, formatter, import sorter)
    3. Compiles the file after post-processing
    4. Reverts changes if compilation fails after processing but succeeded before
    5. Runs a basic execution sanity check

    Args:
        out_path: Path to the stitched Python file
        post_processing: Post-processing configuration (if None, skips post-processing)

    Raises:
        RuntimeError: If compilation fails and cannot be reverted
    """
    logger = get_app_logger()
    logger.debug("Starting post-stitch processing for %s", out_path)

    # Compile before post-processing
    compiled_before = verify_compiles(out_path)
    if not compiled_before:
        logger.warning(
            "Stitched file does not compile before post-processing. "
            "Skipping post-processing and continuing."
        )
        # Still try to verify it executes
        verify_executes(out_path)
        return

    # Save original content in case we need to revert
    original_content = out_path.read_text(encoding="utf-8")

    # Run post-processing if configured
    processing_ran = False
    if post_processing:
        execute_post_processing(out_path, post_processing)
        processing_ran = True
        logger.debug("Post-processing completed")
    else:
        logger.debug("Post-processing skipped (no configuration)")

    # Compile after post-processing
    compiled_after = verify_compiles(out_path)
    if not compiled_after and compiled_before and processing_ran:
        # Revert if it compiled before but not after processing
        logger.warning(
            "File no longer compiles after post-processing. Reverting changes."
        )
        out_path.write_text(original_content, encoding="utf-8")
        out_path.chmod(0o755)
        # Verify it compiles after revert
        if not verify_compiles(out_path):
            xmsg = (
                "File does not compile after reverting post-processing changes. "
                "This indicates a problem with the original stitched file."
            )
            raise RuntimeError(xmsg)
    elif not compiled_after:
        # It didn't compile after, but either it didn't compile before
        # or processing didn't run, so we can't revert
        xmsg = "Stitched file does not compile after post-processing"
        raise RuntimeError(xmsg)

    # Run execution sanity check
    verify_executes(out_path)

    logger.debug("Post-stitch processing completed successfully")


# === serger.stitch ===
# src/serger/stitch.py
"""Stitching logic for combining multiple Python modules into a single file.

This module handles the core functionality for stitching together modular
Python source files into a single executable script. It includes utilities for
import handling, code analysis, and assembly.
"""


def extract_version(pyproject_path: Path) -> str:
    """Extract version string from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml file

    Returns:
        Version string, or "unknown" if not found
    """
    if not pyproject_path.exists():
        return "unknown"
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']', text)
    return match.group(1) if match else "unknown"


def extract_commit(root_path: Path) -> str:
    """Extract git commit hash.

    Only embeds commit hash if in CI or release tag context.

    Args:
        root_path: Project root directory

    Returns:
        Short commit hash, or "unknown (local build)" if not in CI
    """
    logger = get_app_logger()
    # Only embed commit hash if in CI or release tag context
    if not (os.getenv("CI") or os.getenv("GIT_TAG") or os.getenv("GITHUB_REF")):
        return "unknown (local build)"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            cwd=root_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        logger.warning("git rev-parse failed: %s", e.stderr.strip())
    except FileNotFoundError:
        logger.warning("git not available in environment")

    return "unknown"


def split_imports(  # noqa: C901, PLR0915
    text: str,
    package_names: list[str],
) -> tuple[list[str], str]:
    """Extract external imports and body text using AST.

    Separates internal package imports from external imports, removing all
    imports from the function body (they'll be collected and deduplicated).
    Recursively finds imports at all levels, including inside functions.

    Args:
        text: Python source code
        package_names: List of package names to treat as internal
            (e.g., ["serger", "other"])

    Returns:
        Tuple of (external_imports, body_text) where external_imports is a
        list of import statement strings, and body_text is the source with
        all imports removed
    """
    logger = get_app_logger()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        logger.exception("Failed to parse file")
        return [], text

    lines = text.splitlines(keepends=True)
    external_imports: list[str] = []
    all_import_ranges: list[tuple[int, int]] = []

    def find_parent(
        node: ast.AST,
        tree: ast.AST,
        target_type: type[ast.AST] | tuple[type[ast.AST], ...],
    ) -> ast.AST | None:
        """Find if a node is inside a specific parent type by tracking parent nodes."""
        # Build a mapping of child -> parent
        parent_map: dict[ast.AST, ast.AST] = {}

        def build_parent_map(parent: ast.AST) -> None:
            """Recursively build parent mapping."""
            for child in ast.iter_child_nodes(parent):
                parent_map[child] = parent
                build_parent_map(child)

        build_parent_map(tree)

        # Walk up the parent chain to find target type
        current: ast.AST | None = node
        while current is not None:
            if isinstance(current, target_type):
                # Type checker can't infer the specific type from isinstance check
                # We know it's the target_type due to the isinstance check
                return current  # mypy: ignore[return-value]
            current = parent_map.get(current)
        return None

    def has_no_move_comment(snippet: str) -> bool:
        """Check if import has a # serger: no-move comment."""
        # Look for # serger: no-move or # serger:no-move (with or without space)
        pattern = r"#\s*serger\s*:\s*no-move"
        return bool(re.search(pattern, snippet, re.IGNORECASE))

    def collect_imports(node: ast.AST) -> None:  # noqa: PLR0912
        """Recursively collect all import nodes from the AST."""
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno)
            snippet = "".join(lines[start:end])

            # Check for # serger: no-move comment
            if has_no_move_comment(snippet):
                # Keep import in place - don't add to external_imports or ranges
                return

            # --- Determine whether it's internal ---
            is_internal = False
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if node.level > 0:
                    is_internal = True
                else:
                    # Check if module is exactly a package name or starts with one
                    for pkg in package_names:
                        if mod == pkg or mod.startswith(f"{pkg}."):
                            is_internal = True
                            break
            else:
                # Check if any alias starts with any of the package names
                for pkg in package_names:
                    if any(
                        alias.name == pkg or alias.name.startswith(f"{pkg}.")
                        for alias in node.names
                    ):
                        is_internal = True
                        break

            # Check if import is inside if TYPE_CHECKING block
            type_checking_block = find_parent(node, tree, ast.If)
            if (
                type_checking_block
                and isinstance(type_checking_block, ast.If)
                and isinstance(type_checking_block.test, ast.Name)
                and type_checking_block.test.id == "TYPE_CHECKING"
                and len(type_checking_block.body) == 1
            ):
                # If this is the only statement in the if block, remove entire block
                type_start = type_checking_block.lineno - 1
                type_end = getattr(
                    type_checking_block, "end_lineno", type_checking_block.lineno
                )
                all_import_ranges.append((type_start, type_end))
                return  # Skip this import, entire block will be removed

            # Always remove internal imports (they break in stitched mode)
            if is_internal:
                all_import_ranges.append((start, end))
            else:
                # External: hoist module-level to top, keep function-local in place
                is_module_level = not find_parent(
                    node, tree, (ast.FunctionDef, ast.AsyncFunctionDef)
                )
                if is_module_level:
                    # Module-level external import - hoist to top section
                    import_text = snippet.strip()
                    if import_text:
                        if not import_text.endswith("\n"):
                            import_text += "\n"
                        external_imports.append(import_text)
                        all_import_ranges.append((start, end))
                # Function-local external imports stay in place (not added to ranges)

        # Recursively visit child nodes
        for child in ast.iter_child_nodes(node):
            collect_imports(child)

    # Collect all imports recursively
    for node in tree.body:
        collect_imports(node)

    # --- Remove *all* import lines from the body ---
    skip = {i for s, e in all_import_ranges for i in range(s, e)}
    body = "".join(line for i, line in enumerate(lines) if i not in skip)

    return external_imports, body


def strip_redundant_blocks(text: str) -> str:
    """Remove shebangs and __main__ guards from module code.

    Args:
        text: Python source code

    Returns:
        Source code with shebangs and __main__ blocks removed
    """
    text = re.sub(r"^#!.*\n", "", text)
    text = re.sub(
        r"(?s)\n?if\s+__name__\s*==\s*[\"']__main__[\"']\s*:\s*\n.*?$",
        "",
        text,
    )

    return text.strip()


@dataclass
class ModuleSymbols:
    """Top-level symbols extracted from a Python module."""

    functions: set[str]
    classes: set[str]
    assignments: set[str]


def _extract_top_level_symbols(code: str) -> ModuleSymbols:
    """Extract top-level symbols from Python source code.

    Parses AST once and extracts functions, classes, and assignments.

    Args:
        code: Python source code to parse

    Returns:
        ModuleSymbols containing sets of function, class, and assignment names
    """
    functions: set[str] = set()
    classes: set[str] = set()
    assignments: set[str] = set()

    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.add(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.add(node.name)
            elif isinstance(node, ast.Assign):
                # only consider simple names like x = ...
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                for target in targets:
                    assignments.add(target)
    except (SyntaxError, ValueError):
        # If code doesn't parse, return empty sets
        pass

    return ModuleSymbols(
        functions=functions,
        classes=classes,
        assignments=assignments,
    )


def detect_name_collisions(
    module_symbols: dict[str, ModuleSymbols],
) -> None:
    """Detect top-level name collisions across modules.

    Checks for functions, classes, and simple assignments that would
    conflict when stitched together.

    Args:
        module_symbols: Dict mapping module names to their extracted symbols

    Raises:
        RuntimeError: If collisions are detected
    """
    # list of harmless globals we don't mind having overwritten
    ignore = {
        "__all__",
        "__version__",
        "__author__",
        "__path__",
        "__package__",
        "__commit__",
    }

    symbols: dict[str, str] = {}  # name -> module
    collisions: list[tuple[str, str, str]] = []

    for mod, symbols_data in module_symbols.items():
        # Check all symbol types (functions, classes, assignments)
        all_names = (
            symbols_data.functions | symbols_data.classes | symbols_data.assignments
        )

        for name in all_names:
            # skip known harmless globals
            if name in ignore:
                continue

            prev = symbols.get(name)
            if prev:
                collisions.append((name, prev, mod))
            else:
                symbols[name] = mod

    if collisions:
        collision_list = ", ".join(f"{name!r}" for name, _, _ in collisions)
        msg = f"Top-level name collisions detected: {collision_list}"
        raise RuntimeError(msg)


def verify_all_modules_listed(
    file_paths: list[Path], order_paths: list[Path], exclude_paths: list[Path]
) -> None:
    """Ensure all included files are listed in order or exclude paths.

    Args:
        file_paths: List of all included file paths
        order_paths: List of file paths in stitch order
        exclude_paths: List of file paths to exclude

    Raises:
        RuntimeError: If unlisted files are found
    """
    file_set = set(file_paths)
    order_set = set(order_paths)
    exclude_set = set(exclude_paths)
    known = order_set | exclude_set
    unknown = file_set - known

    if unknown:
        unknown_list = ", ".join(str(p) for p in sorted(unknown))
        msg = f"Unlisted source files detected: {unknown_list}"
        raise RuntimeError(msg)


def compute_module_order(  # noqa: C901, PLR0912, PLR0915
    file_paths: list[Path],
    package_root: Path,
    package_name: str,
    file_to_include: dict[Path, IncludeResolved],
) -> list[Path]:
    """Compute correct module order based on import dependencies.

    Uses topological sorting of internal imports to determine the correct
    order for stitching.

    Args:
        file_paths: List of file paths in initial order
        package_root: Common root of all included files
        package_name: Root package name
        file_to_include: Mapping of file path to its include (for dest access)

    Returns:
        Topologically sorted list of file paths

    Raises:
        RuntimeError: If circular imports are detected
    """
    logger = get_app_logger()
    # Map file paths to derived module names
    file_to_module: dict[Path, str] = {}
    module_to_file: dict[str, Path] = {}
    for file_path in file_paths:
        include = file_to_include.get(file_path)
        module_name = derive_module_name(file_path, package_root, include)
        file_to_module[file_path] = module_name
        module_to_file[module_name] = file_path

    # Detect all packages from module names (for multi-package support)
    detected_packages: set[str] = {package_name}  # Always include configured package
    for module_name in file_to_module.values():
        if "." in module_name:
            pkg = module_name.split(".", 1)[0]
            detected_packages.add(pkg)

    # Build dependency graph using derived module names
    deps: dict[str, set[str]] = {file_to_module[fp]: set() for fp in file_paths}

    for file_path in file_paths:
        module_name = file_to_module[file_path]
        if not file_path.exists():
            continue

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                # Handle relative imports (node.level > 0)
                if node.level > 0:
                    # Resolve relative import to absolute module name
                    # e.g., from .constants in serger.actions -> serger.constants
                    current_parts = module_name.split(".")
                    # Go up 'level' levels from current module
                    if node.level > len(current_parts):
                        # Relative import goes beyond package root, skip
                        continue
                    base_parts = current_parts[: -node.level]
                    if node.module:
                        # Append the module name
                        mod_parts = node.module.split(".")
                        resolved_mod = ".".join(base_parts + mod_parts)
                    else:
                        # from . import something - use base only
                        resolved_mod = ".".join(base_parts)
                    mod = resolved_mod
                else:
                    # Absolute import
                    mod = node.module or ""

                # Check if import starts with any detected package, or if it's a
                # relative import that resolved to a module name without package prefix
                matched_package = None
                is_relative_resolved = node.level > 0 and mod and "." not in mod

                for pkg in detected_packages:
                    # Match only if mod equals pkg or starts with pkg + "."
                    # This prevents false matches where a module name happens to
                    # start with a package name (e.g., "foo_bar" matching "foo")
                    if mod == pkg or mod.startswith(pkg + "."):
                        matched_package = pkg
                        break

                logger.trace(
                    "[DEPS] %s imports %s: mod=%s, matched_package=%s, "
                    "is_relative_resolved=%s",
                    module_name,
                    node.module or "",
                    mod,
                    matched_package,
                    is_relative_resolved,
                )

                # If relative import resolved to a simple name (no dots), check if it
                # matches any module name directly (for same-package imports)
                if not matched_package and is_relative_resolved:
                    # Check if the resolved module name matches any module directly
                    logger.trace(
                        "[DEPS] Relative import in %s: resolved_mod=%s, checking deps",
                        module_name,
                        mod,
                    )
                    for dep_module in deps:
                        # Match if dep_module equals mod or starts with mod.
                        if (
                            dep_module == mod or dep_module.startswith(mod + ".")
                        ) and dep_module != module_name:
                            logger.trace(
                                "[DEPS] Found dependency: %s -> %s (from %s)",
                                module_name,
                                dep_module,
                                mod,
                            )
                            deps[module_name].add(dep_module)
                    continue  # Skip the package-based matching below

                if matched_package:
                    # Handle nested imports: package.core.base -> core.base
                    # Remove package prefix and check if it matches any module
                    mod_suffix = (
                        mod[len(matched_package) + 1 :]
                        if mod.startswith(matched_package + ".")
                        else mod[len(matched_package) :]
                        if mod == matched_package
                        else ""
                    )
                    if mod_suffix:
                        # Check if this matches any derived module name
                        # Match both the suffix (for same-package imports)
                        # and full module name (for cross-package imports)
                        for dep_module in deps:
                            # Match if: dep_module equals mod_suffix or mod
                            # or dep_module starts with mod_suffix or mod
                            prefix_tuple = (mod_suffix + ".", mod + ".")
                            matches = dep_module in (
                                mod_suffix,
                                mod,
                            ) or dep_module.startswith(prefix_tuple)
                            if matches and dep_module != module_name:
                                deps[module_name].add(dep_module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    # Check if import starts with any detected package
                    matched_package = None
                    for pkg in detected_packages:
                        if mod.startswith(pkg):
                            matched_package = pkg
                            break

                    if matched_package:
                        # Handle nested imports
                        mod_suffix = (
                            mod[len(matched_package) + 1 :]
                            if mod.startswith(matched_package + ".")
                            else mod[len(matched_package) :]
                            if mod == matched_package
                            else ""
                        )
                        if mod_suffix:
                            # Check if this matches any derived module name
                            # Match both the suffix (for same-package imports)
                            # and full module name (for cross-package imports)
                            for dep_module in deps:
                                prefix_tuple = (mod_suffix + ".", mod + ".")
                                matches = dep_module in (
                                    mod_suffix,
                                    mod,
                                ) or dep_module.startswith(prefix_tuple)
                                if matches and dep_module != module_name:
                                    deps[module_name].add(dep_module)

    # detect circular imports first
    try:
        sorter = graphlib.TopologicalSorter(deps)
        topo_modules = list(sorter.static_order())
    except graphlib.CycleError as e:
        msg = f"Circular dependency detected: {e.args[1] if e.args else 'unknown'}"
        raise RuntimeError(msg) from e

    # Convert back to file paths
    topo_paths = [module_to_file[mod] for mod in topo_modules if mod in module_to_file]
    return topo_paths


def suggest_order_mismatch(
    order_paths: list[Path],
    package_root: Path,
    package_name: str,
    file_to_include: dict[Path, IncludeResolved],
    topo_paths: list[Path] | None = None,
) -> None:
    """Warn if module order violates dependencies.

    Args:
        order_paths: List of file paths in intended order
        package_root: Common root of all included files
        package_name: Root package name
        file_to_include: Mapping of file path to its include (for dest access)
        topo_paths: Optional pre-computed topological order. If provided,
                    skips recomputing the order. If None, computes it via
                    compute_module_order.
    """
    logger = get_app_logger()
    if topo_paths is None:
        topo_paths = compute_module_order(
            order_paths, package_root, package_name, file_to_include
        )

    # compare order_paths to topological sort
    mismatched = [
        p
        for p in order_paths
        if p in topo_paths and topo_paths.index(p) != order_paths.index(p)
    ]
    if mismatched:
        logger.warning("Possible module misordering detected:")

        for p in mismatched:
            include = file_to_include.get(p)
            module_name = derive_module_name(p, package_root, include)
            logger.warning("  - %s appears before one of its dependencies", module_name)
        topo_modules = [
            derive_module_name(p, package_root, file_to_include.get(p))
            for p in topo_paths
        ]
        logger.warning("Suggested order: %s", ", ".join(topo_modules))


def verify_no_broken_imports(final_text: str, package_names: list[str]) -> None:
    """Verify all internal imports have been resolved in stitched script.

    Args:
        final_text: Final stitched script text
        package_names: List of all package names to check
            (e.g., ["serger", "apathetic_logs"])

    Raises:
        RuntimeError: If unresolved imports remain
    """
    broken: set[str] = set()

    for package_name in package_names:
        # Pattern for nested imports: package.core.base or package.core
        # Matches: import package.module or import package.sub.module
        import_pattern = re.compile(rf"\bimport {re.escape(package_name)}\.([\w.]+)")
        # Pattern for from imports: from package.core import base or
        # from package.core.base import something
        from_pattern = re.compile(
            rf"\bfrom {re.escape(package_name)}\.([\w.]+)\s+import"
        )
        # Pattern for top-level package imports: from package import ...
        top_level_pattern = re.compile(rf"\bfrom {re.escape(package_name)}\s+import")

        # Check import statements
        for m in import_pattern.finditer(final_text):
            mod_suffix = m.group(1)
            full_module_name = f"{package_name}.{mod_suffix}"
            # Check if module is in the stitched output
            # Header format: # === module_name === (may contain dots)
            # Try both full module name and just the suffix (for backward compat)
            header_pattern_full = re.compile(
                rf"# === {re.escape(full_module_name)} ==="
            )
            header_pattern_suffix = re.compile(rf"# === {re.escape(mod_suffix)} ===")
            if not header_pattern_full.search(
                final_text
            ) and not header_pattern_suffix.search(final_text):
                broken.add(full_module_name)

        # Check from ... import statements
        for m in from_pattern.finditer(final_text):
            mod_suffix = m.group(1)
            full_module_name = f"{package_name}.{mod_suffix}"
            # Check if module is in the stitched output
            # Try both full module name and just the suffix (for backward compat)
            header_pattern_full = re.compile(
                rf"# === {re.escape(full_module_name)} ==="
            )
            header_pattern_suffix = re.compile(rf"# === {re.escape(mod_suffix)} ===")
            if not header_pattern_full.search(
                final_text
            ) and not header_pattern_suffix.search(final_text):
                broken.add(full_module_name)

        # Check top-level package imports: from package import ...
        for _m in top_level_pattern.finditer(final_text):
            # For top-level imports, check if the package itself exists
            # This would be in a header like # === package === or
            # # === package.__init__ ===
            # OR it could be created via shims (when __init__.py is excluded)
            header_pattern = re.compile(
                rf"# === {re.escape(package_name)}(?:\.__init__)? ==="
            )
            # Check for shim-created package:
            # Old pattern: _pkg = 'package_name' followed by sys.modules[_pkg] = _mod
            # New pattern: _create_pkg_module('package_name')
            # Handle both single and double quotes (formatter may change them)
            escaped_name = re.escape(package_name)
            shim_pattern_old = re.compile(
                rf"_pkg\s*=\s*(?:['\"]){escaped_name}(?:['\"]).*?"
                rf"sys\.modules\[_pkg\]\s*=\s*_mod",
                re.DOTALL,
            )
            shim_pattern_new = re.compile(
                rf"_create_pkg_module\s*\(\s*(?:['\"]){escaped_name}(?:['\"])"
            )
            if (
                not header_pattern.search(final_text)
                and not shim_pattern_old.search(final_text)
                and not shim_pattern_new.search(final_text)
            ):
                broken.add(package_name)

    if broken:
        broken_list = ", ".join(sorted(broken))
        msg = f"Unresolved internal imports: {broken_list}"
        raise RuntimeError(msg)


def _find_package_root_for_file(file_path: Path) -> Path | None:
    """Find the package root for a file by walking up looking for __init__.py.

    Starting from the file's directory, walks up the directory tree while
    we find __init__.py files. The topmost directory with __init__.py is
    the package root.

    Args:
        file_path: Path to the Python file

    Returns:
        Path to the package root directory, or None if not found
    """
    logger = get_app_logger()
    current_dir = file_path.parent.resolve()
    last_package_dir: Path | None = None

    logger.trace(
        "[PKG_ROOT] Finding package root for %s, starting from %s",
        file_path.name,
        current_dir,
    )

    # Walk up from the file's directory
    while True:
        # Check if current directory has __init__.py
        init_file = current_dir / "__init__.py"
        if init_file.exists():
            # This directory is part of a package
            last_package_dir = current_dir
            logger.trace(
                "[PKG_ROOT] Found __init__.py at %s (package root so far: %s)",
                current_dir,
                last_package_dir,
            )
        else:
            # This directory doesn't have __init__.py, so we've gone past the package
            # Return the last directory that had __init__.py
            logger.trace(
                "[PKG_ROOT] No __init__.py at %s, package root: %s",
                current_dir,
                last_package_dir,
            )
            return last_package_dir

        # Move up one level
        parent = current_dir.parent
        if parent == current_dir:
            # Reached filesystem root
            logger.trace(
                "[PKG_ROOT] Reached filesystem root, package root: %s",
                last_package_dir,
            )
            return last_package_dir
        current_dir = parent


def force_mtime_advance(path: Path, seconds: float = 1.0, max_tries: int = 50) -> None:
    """Reliably bump a file's mtime, preserving atime and nanosecond precision.

    Ensures the change is visible before returning, even on lazy filesystems.
    We often can't use os.sleep or time.sleep because we monkeypatch it.

    Args:
        path: Path to file whose mtime to advance
        seconds: How many seconds to advance mtime
        max_tries: Maximum number of attempts

    Raises:
        AssertionError: If mtime could not be advanced after max_tries
    """
    real_time = importlib.import_module("time")  # immune to monkeypatch
    old_m = path.stat().st_mtime_ns
    ns_bump = int(seconds * 1_000_000_000)
    new_m: int = old_m

    for _attempt in range(max_tries):
        st = path.stat()
        os.utime(path, ns=(int(st.st_atime_ns), int(st.st_mtime_ns + ns_bump)))
        os.sync()  # flush kernel metadata

        new_m = path.stat().st_mtime_ns
        if new_m > old_m:
            return  # ✅ success
        real_time.sleep(0.00001)  # 10 µs pause before recheck

    xmsg = (
        f"bump_mtime({path}) failed to advance mtime after {max_tries} attempts "
        f"(old={old_m}, new={new_m})",
    )
    raise AssertionError(xmsg)


def _collect_modules(
    file_paths: list[Path],
    package_root: Path,
    package_name: str,
    file_to_include: dict[Path, IncludeResolved],
) -> tuple[dict[str, str], OrderedDict[str, None], list[str], list[str]]:
    """Collect and process module sources from file paths.

    Args:
        file_paths: List of file paths to stitch (in order)
        package_root: Common root of all included files
        package_name: Root package name
        file_to_include: Mapping of file path to its include (for dest access)

    Returns:
        Tuple of (module_sources, all_imports, parts, derived_module_names)
    """
    logger = get_app_logger()
    all_imports: OrderedDict[str, None] = OrderedDict()
    module_sources: dict[str, str] = {}
    parts: list[str] = []
    derived_module_names: list[str] = []

    # Reserve imports for shim system and main entry point
    all_imports.setdefault("import sys\n", None)  # For shim system and main()
    all_imports.setdefault("import types\n", None)  # For shim system (ModuleType)

    # First pass: collect all module names to detect packages
    all_module_names: list[str] = []
    for file_path in file_paths:
        if not file_path.exists():
            logger.warning("Skipping missing file: %s", file_path)
            continue
        include = file_to_include.get(file_path)
        module_name = derive_module_name(file_path, package_root, include)
        all_module_names.append(module_name)

    # Detect all packages from module names
    detected_packages: set[str] = {package_name}  # Always include configured package
    for module_name in all_module_names:
        if "." in module_name:
            pkg = module_name.split(".", 1)[0]
            detected_packages.add(pkg)

    # Convert to sorted list for consistent behavior
    package_names_list = sorted(detected_packages)

    for file_path in file_paths:
        if not file_path.exists():
            logger.warning("Skipping missing file: %s", file_path)
            continue

        # Derive module name from file path
        include = file_to_include.get(file_path)
        module_name = derive_module_name(file_path, package_root, include)
        derived_module_names.append(module_name)

        module_text = file_path.read_text(encoding="utf-8")
        module_text = strip_redundant_blocks(module_text)
        module_sources[f"{module_name}.py"] = module_text

        # Extract imports - pass all detected package names
        external_imports, module_body = split_imports(module_text, package_names_list)
        for imp in external_imports:
            all_imports.setdefault(imp, None)

        # Create module section - use derived module name in header
        header = f"# === {module_name} ==="
        parts.append(f"\n{header}\n{module_body.strip()}\n\n")

        logger.trace("Processed module: %s (from %s)", module_name, file_path)

    return module_sources, all_imports, parts, derived_module_names


def _format_header_line(
    *,
    display_name: str,
    description: str,
    package_name: str,
) -> str:
    """Format the header text based on config values.

    Rules:
    - Both provided: "DisplayName — Description"
    - Only name: "DisplayName"
    - Nothing: "package_name"
    - Only description: "package_name — Description"

    Args:
        display_name: Optional display name from config
        description: Optional description from config
        package_name: Package name (fallback)

    Returns:
        Formatted header text (without "# " prefix or trailing newline)
    """
    # Use display_name if provided, otherwise fall back to package_name
    name = display_name.strip() if display_name else package_name
    desc = description.strip() if description else ""

    if name and desc:
        return f"{name} — {desc}"
    if name:
        return f"{name}"
    # default to package_name
    return f"{package_name}"


def _build_final_script(  # noqa: C901, PLR0912, PLR0913, PLR0915
    *,
    package_name: str,
    all_imports: OrderedDict[str, None],
    parts: list[str],
    order_names: list[str],
    all_function_names: set[str],
    order_paths: list[Path] | None = None,
    package_root: Path | None = None,
    file_to_include: dict[Path, IncludeResolved] | None = None,
    license_header: str,
    version: str,
    commit: str,
    build_date: str,
    display_name: str = "",
    description: str = "",
    repo: str = "",
) -> tuple[str, list[str]]:
    """Build the final stitched script.

    Args:
        package_name: Root package name
        all_imports: Collected external imports
        parts: Module code sections
        order_names: List of module names (for shim generation)
        all_function_names: Set of all function names from all modules
            (used to detect if main() function exists)
        order_paths: Optional list of file paths corresponding to order_names
        package_root: Optional common root of all included files
        file_to_include: Optional mapping of file path to its include
        license_header: License header text
        version: Version string
        commit: Commit hash
        build_date: Build timestamp
        display_name: Optional display name for header
        description: Optional description for header
        repo: Optional repository URL for header

    Returns:
        Final script text
    """
    logger = get_app_logger()
    logger.debug("Building final script...")

    # Separate __future__ imports
    future_imports: OrderedDict[str, None] = OrderedDict()
    for imp in list(all_imports.keys()):
        if imp.strip().startswith("from __future__"):
            future_imports.setdefault(imp, None)
            del all_imports[imp]

    future_block = "".join(future_imports.keys())
    import_block = "".join(all_imports.keys())

    # Generate import shims
    # Group modules by their immediate parent package
    # For "serger.utils.utils_text", the parent package is "serger.utils"
    # For "serger.cli", the parent package is "serger"
    # Include all modules (matching installed package behavior)
    #
    # IMPORTANT: Module names in order_names are relative to package_root
    # (e.g., "utils.utils_text"), but shims need full paths
    # (e.g., "serger.utils.utils_text").
    # Prepend package_name to all module names for shim generation.
    # Note: If specific modules should be excluded, use the 'exclude' config option
    shim_names_raw = list(order_names)

    # Detect packages by looking at file system structure (__init__.py files)
    # This is more reliable than guessing from module names
    # Map module names to their actual package roots
    module_to_package_root: dict[str, Path | None] = {}
    detected_packages: set[str] = {package_name}  # Always include configured package

    if order_paths and package_root and file_to_include:
        logger.trace(
            "[PKG_DETECT] Detecting packages from file system structure "
            "(__init__.py files)"
        )
        # Create mapping from module names to file paths
        name_to_path: dict[str, Path] = {}
        for file_path in order_paths:
            include = file_to_include.get(file_path)
            module_name = derive_module_name(file_path, package_root, include)
            name_to_path[module_name] = file_path

        # For each module, find its package root by walking up looking for __init__.py
        for module_name in shim_names_raw:
            if module_name in name_to_path:
                file_path = name_to_path[module_name]
                file_pkg_root = _find_package_root_for_file(file_path)
                module_to_package_root[module_name] = file_pkg_root

                # Determine if this file is from a different package
                # A file is from a different package if its package root is:
                # 1. Not the same as package_root, AND
                # 2. Not a subdirectory of package_root
                #    (i.e., it's a sibling or unrelated)
                if file_pkg_root and file_pkg_root != package_root:
                    try:
                        # Check if file_pkg_root is a subdirectory of package_root
                        rel_path = file_pkg_root.relative_to(package_root)
                        # If it's a direct child (one level deep), it might be
                        # a sibling package like pkg1/ and pkg2/ under a common root
                        if len(rel_path.parts) == 1:
                            # It's a direct child - check if it's a different package
                            # by comparing the package root name to package_name
                            pkg_name_from_path = file_pkg_root.name
                            if (
                                pkg_name_from_path
                                and pkg_name_from_path != package_name
                            ):
                                logger.trace(
                                    "[PKG_DETECT] Detected separate package %s "
                                    "(sibling of %s) from file %s",
                                    pkg_name_from_path,
                                    package_name,
                                    file_path,
                                )
                                detected_packages.add(pkg_name_from_path)
                            else:
                                logger.trace(
                                    "[PKG_DETECT] %s is subpackage of %s "
                                    "(file_pkg_root=%s, package_root=%s)",
                                    module_name,
                                    package_name,
                                    file_pkg_root,
                                    package_root,
                                )
                        # If it's deeper (len > 1), it's a subpackage
                        else:
                            logger.trace(
                                "[PKG_DETECT] %s is nested subpackage of %s (depth=%d)",
                                module_name,
                                package_name,
                                len(rel_path.parts),
                            )
                    except ValueError:
                        # file_pkg_root is not under package_root,
                        # so it's a different package
                        # Extract package name from the file's package root
                        pkg_name_from_path = file_pkg_root.name
                        if pkg_name_from_path and pkg_name_from_path != package_name:
                            logger.trace(
                                "[PKG_DETECT] Detected separate package %s "
                                "(unrelated to %s) from file %s",
                                pkg_name_from_path,
                                package_name,
                                file_path,
                            )
                            detected_packages.add(pkg_name_from_path)
                elif file_pkg_root == package_root:
                    logger.trace(
                        "[PKG_DETECT] %s is in main package %s",
                        module_name,
                        package_name,
                    )
                else:
                    logger.trace(
                        "[PKG_DETECT] %s: no package root found (file_pkg_root=None)",
                        module_name,
                    )

    # Also detect packages from module names
    # (as fallback when __init__.py detection fails)
    # Only do this if we didn't successfully detect packages from file system
    # (i.e., if module_to_package_root is empty or all values are None)
    if not module_to_package_root or all(
        v is None for v in module_to_package_root.values()
    ):
        logger.debug(
            "Package detection: __init__.py files not found, "
            "falling back to module name detection"
        )
        # Fallback: detect packages from module names
        for module_name in shim_names_raw:
            if "." in module_name:
                pkg = module_name.split(".", 1)[0]
                # Only add if it's clearly a different package (not a subpackage)
                # We can't reliably distinguish, so be conservative and only add
                # if it's different from package_name
                if pkg != package_name:
                    logger.trace(
                        "[PKG_DETECT] Fallback: detected package %s "
                        "from module name %s",
                        pkg,
                        module_name,
                    )
                    detected_packages.add(pkg)

    # Prepend package_name to create full module paths
    # Module names are relative to package_root, so we need to prepend package_name
    # to get the full import path
    # (e.g., "utils.utils_text" -> "serger.utils.utils_text")
    # However, if module names already start with package_name or another package,
    # don't double-prefix (for multi-package scenarios)
    shim_names: list[str] = []
    for name in shim_names_raw:
        # If name already equals package_name, it's the root module itself
        if name == package_name:
            full_name = package_name
        # If name already starts with package_name, use it as-is
        elif name.startswith(f"{package_name}."):
            full_name = name
        # If name contains dots and starts with a different detected package,
        # it's from another package (multi-package scenario) - use as-is
        elif "." in name:
            first_part = name.split(".", 1)[0]
            # If first part is a detected package different from package_name,
            # it's from another package - use as-is
            if first_part in detected_packages and first_part != package_name:
                full_name = name
            else:
                # Likely a subpackage - prepend package_name
                full_name = f"{package_name}.{name}"
        else:
            # Top-level module under package: prepend package_name
            full_name = f"{package_name}.{name}"
        shim_names.append(full_name)

    # Group modules by their parent package
    # parent_package -> list of (module_name, is_direct_child)
    # is_direct_child means the module is directly under this package
    # (not nested deeper)
    packages: dict[str, list[tuple[str, bool]]] = {}
    # parent_pkg -> [(module_name, is_direct)]

    for module_name in shim_names:
        if "." not in module_name:
            # Top-level module, parent is the root package
            parent = package_name
            is_direct = True
        else:
            # Find the parent package (everything except the last component)
            name_parts = module_name.split(".")
            parent = ".".join(name_parts[:-1])
            is_direct = True  # This module is directly under its parent

        if parent not in packages:
            packages[parent] = []
        packages[parent].append((module_name, is_direct))

    # Collect all package names (both intermediate and top-level)
    all_packages: set[str] = set()
    for module_name in shim_names:
        name_parts = module_name.split(".")
        # Add all package prefixes
        # (e.g., for "serger.utils.utils_text" add "serger" and "serger.utils")
        for i in range(1, len(name_parts)):
            pkg = ".".join(name_parts[:i])
            all_packages.add(pkg)
        # Also add the top-level package if module has dots
        if "." in module_name:
            all_packages.add(name_parts[0])
    # Add root package if not already present
    all_packages.add(package_name)

    # Sort packages by depth (shallowest first) to create parents before children
    sorted_packages = sorted(all_packages, key=lambda p: p.count("."))

    # Generate shims for each package
    # Each package gets its own module object to maintain proper isolation
    shim_blocks: list[str] = []
    shim_blocks.append("# --- import shims for single-file runtime ---")
    # Note: types and sys are imported at the top level (see all_imports)

    # Helper function to create/register package modules
    shim_blocks.append("def _create_pkg_module(pkg_name: str) -> types.ModuleType:")
    shim_blocks.append(
        '    """Create or get a package module and set up parent relationships."""'
    )
    shim_blocks.append("    _mod = sys.modules.get(pkg_name)")
    shim_blocks.append("    if not _mod:")
    shim_blocks.append("        _mod = types.ModuleType(pkg_name)")
    shim_blocks.append("        _mod.__package__ = pkg_name")
    shim_blocks.append("        sys.modules[pkg_name] = _mod")
    shim_blocks.append("    # Set up parent-child relationships for nested packages")
    shim_blocks.append("    if '.' in pkg_name:")
    shim_blocks.append("        _parent_pkg = '.'.join(pkg_name.split('.')[:-1])")
    shim_blocks.append("        _child_name = pkg_name.split('.')[-1]")
    shim_blocks.append("        _parent = sys.modules.get(_parent_pkg)")
    shim_blocks.append("        if _parent:")
    shim_blocks.append("            setattr(_parent, _child_name, _mod)")
    shim_blocks.append("    return _mod")
    shim_blocks.append("")

    shim_blocks.append(
        "def _setup_pkg_modules(pkg_name: str, module_names: list[str]) -> None:"
    )
    shim_blocks.append(
        '    """Set up package module attributes and register submodules."""'
    )
    shim_blocks.append("    _mod = sys.modules.get(pkg_name)")
    shim_blocks.append("    if not _mod:")
    shim_blocks.append("        return")
    shim_blocks.append("    # Copy attributes from all modules under this package")
    shim_blocks.append("    _globals = globals()")
    shim_blocks.append("    for _key, _value in _globals.items():")
    shim_blocks.append("        setattr(_mod, _key, _value)")
    shim_blocks.append("    # Register all modules under this package")
    shim_blocks.append("    for _name in module_names:")
    shim_blocks.append("        sys.modules[_name] = _mod")
    shim_blocks.append("    # Set submodules as attributes on parent package")
    shim_blocks.append("    for _name in module_names:")
    shim_blocks.append(
        "        if _name != pkg_name and _name.startswith(pkg_name + '.'):"
    )
    shim_blocks.append("            _submodule_name = _name.split('.')[-1]")
    shim_blocks.append("            if not hasattr(_mod, _submodule_name):")
    shim_blocks.append("                setattr(_mod, _submodule_name, _mod)")
    shim_blocks.append(
        "            elif isinstance(getattr(_mod, _submodule_name, None), "
        "types.ModuleType):"
    )
    shim_blocks.append("                setattr(_mod, _submodule_name, _mod)")
    shim_blocks.append("")

    # First pass: Create all package modules and set up parent-child relationships
    shim_blocks.extend(
        f"_create_pkg_module({pkg_name!r})" for pkg_name in sorted_packages
    )

    shim_blocks.append("")

    # Second pass: Copy attributes and register modules
    # Process in any order since all modules are now created
    for pkg_name in sorted_packages:
        if pkg_name not in packages:
            continue  # Skip packages that don't have any modules

        module_names_for_pkg = [name for name, _ in packages[pkg_name]]
        # Module names already have full paths (with package_name prefix),
        # but ensure they're correctly formatted for registration
        # If name equals pkg_name, it's the root module itself
        full_module_names = [
            (
                name
                if (name == pkg_name or name.startswith(f"{pkg_name}."))
                else f"{pkg_name}.{name}"
            )
            for name in module_names_for_pkg
        ]
        module_names_str = ", ".join(repr(name) for name in full_module_names)
        shim_blocks.append(f"_setup_pkg_modules({pkg_name!r}, [{module_names_str}])")

    shim_text = "\n".join(shim_blocks)

    # Generate formatted header line
    header_line = _format_header_line(
        display_name=display_name,
        description=description,
        package_name=package_name,
    )

    # Build license/header section
    # Prefix each line of the license header with "# " if provided
    license_section = ""
    if license_header:
        lines = license_header.strip().split("\n")
        prefixed_lines = [f"# {line}" for line in lines]
        license_section = "\n".join(prefixed_lines) + "\n"
    repo_line = f"# Repo: {repo}\n" if repo else ""

    # Check if main() function exists in the stitched code
    # Use the pre-collected function names to avoid parsing again
    has_main = "main" in all_function_names

    # Only add __main__ block if main() function exists
    main_block = ""
    if has_main:
        main_block = "\nif __name__ == '__main__':\n    sys.exit(main(sys.argv[1:]))\n"

    script_text = (
        "#!/usr/bin/env python3\n"
        f"# {header_line}\n"
        f"{license_section}"
        f"# Version: {version}\n"
        f"# Commit: {commit}\n"
        f"# Build Date: {build_date}\n"
        f"{repo_line}"
        "\n# ruff: noqa: E402\n"
        "\n"
        f"{future_block}\n"
        '"""\n'
        f"{header_line}\n"
        "This single-file version is auto-generated from modular sources.\n"
        f"Version: {version}\n"
        f"Commit: {commit}\n"
        f"Built: {build_date}\n"
        '"""\n\n'
        f"{import_block}\n"
        "\n"
        # constants come *after* imports to avoid breaking __future__ rules
        f"__version__ = {json.dumps(version)}\n"
        f"__commit__ = {json.dumps(commit)}\n"
        f"__build_date__ = {json.dumps(build_date)}\n"
        f"__STANDALONE__ = True\n"
        f"__STITCH_SOURCE__ = {json.dumps(PROGRAM_PACKAGE)}\n"
        f"__package__ = {json.dumps(package_name)}\n"
        "\n"
        "\n" + "\n".join(parts) + "\n"
        f"{shim_text}\n"
        f"{main_block}"
    )

    # Return script text and detected packages (sorted for consistency)
    return script_text, sorted(detected_packages)


def stitch_modules(  # noqa: PLR0915, PLR0912, C901
    *,
    config: dict[str, object],
    file_paths: list[Path],
    package_root: Path,
    file_to_include: dict[Path, IncludeResolved],
    out_path: Path,
    license_header: str = "",
    version: str = "unknown",
    commit: str = "unknown",
    build_date: str = "unknown",
    post_processing: PostProcessingConfigResolved | None = None,
) -> None:
    """Orchestrate stitching of multiple Python modules into a single file.

    This is the main entry point for the stitching process. It coordinates all
    stitching utilities to produce a single, self-contained Python script from
    modular sources.

    The function:
    1. Validates configuration completeness
    2. Verifies all modules are listed and dependencies are consistent
    3. Collects and deduplicates external imports
    4. Assembles modules in correct order
    5. Detects name collisions
    6. Generates final script with metadata
    7. Verifies the output compiles
    8. Optionally runs post-processing tools (static checker, formatter, import sorter)

    Args:
        config: BuildConfigResolved with stitching fields (package, order).
                Must include 'package' field for stitching. 'order' is optional
                and will be auto-discovered via topological sort if not provided.
        file_paths: List of file paths to stitch (in order)
        package_root: Common root of all included files
        file_to_include: Mapping of file path to its include (for dest access)
        out_path: Path where final stitched script should be written
        license_header: Optional license header text for generated script
        version: Version string to embed in script metadata
        commit: Commit hash to embed in script metadata
        build_date: Build timestamp to embed in script metadata
        post_processing: Post-processing configuration (if None, skips post-processing)

    Raises:
        RuntimeError: If any validation or stitching step fails
        AssertionError: If mtime advancing fails
    """
    logger = get_app_logger()

    package_name_raw = config.get("package", "unknown")
    order_paths_raw = config.get("order", [])
    exclude_paths_raw = config.get("exclude_names", [])

    # Type guards for mypy/pyright
    if not isinstance(package_name_raw, str):
        msg = "Config 'package' must be a string"
        raise TypeError(msg)
    if not isinstance(order_paths_raw, list):
        msg = "Config 'order' must be a list"
        raise TypeError(msg)
    if not isinstance(exclude_paths_raw, list):
        msg = "Config 'exclude_names' must be a list"
        raise TypeError(msg)

    # Cast to known types after type guards
    package_name = package_name_raw
    # order and exclude_names are already resolved to Path objects in run_build()
    # Convert to Path objects explicitly

    order_paths: list[Path] = []
    for item in order_paths_raw:  # pyright: ignore[reportUnknownVariableType]
        if isinstance(item, str):
            order_paths.append(Path(item))
        elif isinstance(item, Path):
            order_paths.append(item)

    exclude_paths: list[Path] = []
    for item in exclude_paths_raw:  # pyright: ignore[reportUnknownVariableType]
        if isinstance(item, str):
            exclude_paths.append(Path(item))
        elif isinstance(item, Path):
            exclude_paths.append(item)

    if not package_name or package_name == "unknown":
        msg = "Config must specify 'package' for stitching"
        raise RuntimeError(msg)

    if not order_paths:
        msg = (
            "No modules found for stitching. "
            "Either specify 'order' in config or ensure 'include' patterns match files."
        )
        raise RuntimeError(msg)

    logger.info("Starting stitch process for package: %s", package_name)

    # --- Validation Phase ---
    logger.debug("Validating module listing...")
    verify_all_modules_listed(file_paths, order_paths, exclude_paths)

    logger.debug("Checking module order consistency...")
    # Use pre-computed topological order if available (from auto-discovery)
    topo_paths_raw = config.get("topo_paths")
    topo_paths: list[Path] | None = None
    if topo_paths_raw is not None and isinstance(topo_paths_raw, list):
        topo_paths = []
        # Type narrowing: after isinstance check, cast to help type inference
        for item in cast("list[str | Path]", topo_paths_raw):
            if isinstance(item, str):
                topo_paths.append(Path(item))
            elif isinstance(item, Path):  # pyright: ignore[reportUnnecessaryIsInstance]
                topo_paths.append(item)
    suggest_order_mismatch(
        order_paths, package_root, package_name, file_to_include, topo_paths
    )

    # --- Collection Phase ---
    logger.debug("Collecting module sources...")
    module_sources, all_imports, parts, derived_module_names = _collect_modules(
        order_paths, package_root, package_name, file_to_include
    )

    # --- Parse AST once for all modules ---
    # Extract symbols (functions, classes, assignments) from all modules
    # This avoids parsing AST multiple times
    logger.debug("Extracting symbols from modules...")
    module_symbols: dict[str, ModuleSymbols] = {}
    all_function_names: set[str] = set()
    for mod_name, source in module_sources.items():
        symbols = _extract_top_level_symbols(source)
        module_symbols[mod_name] = symbols
        all_function_names.update(symbols.functions)

    # --- Collision Detection ---
    logger.debug("Detecting name collisions...")
    detect_name_collisions(module_symbols)

    # --- Final Assembly ---
    # Extract display configuration
    display_name_raw = config.get("display_name", "")
    description_raw = config.get("description", "")
    repo_raw = config.get("repo", "")

    # Type guards
    if not isinstance(display_name_raw, str):
        display_name_raw = ""
    if not isinstance(description_raw, str):
        description_raw = ""
    if not isinstance(repo_raw, str):
        repo_raw = ""

    final_script, detected_packages = _build_final_script(
        package_name=package_name,
        all_imports=all_imports,
        parts=parts,
        order_names=derived_module_names,
        all_function_names=all_function_names,
        order_paths=order_paths,
        package_root=package_root,
        file_to_include=file_to_include,
        license_header=license_header,
        version=version,
        commit=commit,
        build_date=build_date,
        display_name=display_name_raw,
        description=description_raw,
        repo=repo_raw,
    )

    # --- Verification ---
    logger.debug("Verifying assembled script...")
    verify_no_broken_imports(final_script, detected_packages)

    # --- Output ---
    logger.debug("Writing output file: %s", out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(final_script, encoding="utf-8")
    out_path.chmod(0o755)

    # Advance mtime to ensure visibility across filesystems
    logger.debug("Advancing mtime...")
    force_mtime_advance(out_path)

    # Post-processing: tools, compilation checks, and verification
    post_stitch_processing(out_path, post_processing=post_processing)

    logger.info(
        "Successfully stitched %d modules into %s",
        len(parts),
        out_path,
    )


# === serger.build ===
# src/serger/build.py


# --------------------------------------------------------------------------- #
# File collection functions (Phase 1)
# --------------------------------------------------------------------------- #


def expand_include_pattern(include: IncludeResolved) -> list[Path]:
    """Expand a single include pattern to a list of matching Python files.

    Args:
        include: Resolved include pattern with root and path

    Returns:
        List of resolved absolute paths to matching .py files
    """
    logger = get_app_logger()
    src_pattern = str(include["path"])
    root = Path(include["root"]).resolve()
    matches: list[Path] = []

    if src_pattern.endswith("/") and not has_glob_chars(src_pattern):
        logger.trace(
            f"[MATCH] Treating as trailing-slash directory include → {src_pattern!r}",
        )
        root_dir = root / src_pattern.rstrip("/")
        if root_dir.exists():
            all_files = [p for p in root_dir.rglob("*") if p.is_file()]
            matches = [p for p in all_files if p.suffix == ".py"]
        else:
            logger.trace(f"[MATCH] root_dir does not exist: {root_dir}")

    elif src_pattern.endswith("/**"):
        logger.trace(f"[MATCH] Treating as recursive include → {src_pattern!r}")
        root_dir = root / src_pattern.removesuffix("/**")
        if root_dir.exists():
            all_files = [p for p in root_dir.rglob("*") if p.is_file()]
            matches = [p for p in all_files if p.suffix == ".py"]
        else:
            logger.trace(f"[MATCH] root_dir does not exist: {root_dir}")

    elif has_glob_chars(src_pattern):
        logger.trace(f"[MATCH] Using glob() for pattern {src_pattern!r}")
        # Make pattern relative to root if it's absolute
        pattern_path = Path(src_pattern)
        if pattern_path.is_absolute():
            try:
                # Try to make it relative to root
                src_pattern = str(pattern_path.relative_to(root))
            except ValueError:
                # If pattern is not under root, use just the pattern name
                src_pattern = pattern_path.name
        all_matches = list(root.glob(src_pattern))
        matches = [p for p in all_matches if p.is_file() and p.suffix == ".py"]
        logger.trace(f"[MATCH] glob found {len(matches)} .py file(s)")

    else:
        logger.trace(f"[MATCH] Treating as literal include {root / src_pattern}")
        candidate = root / src_pattern
        if candidate.is_file() and candidate.suffix == ".py":
            matches = [candidate]

    # Resolve all paths to absolute
    resolved_matches = [p.resolve() for p in matches]

    for i, m in enumerate(resolved_matches):
        logger.trace(f"[MATCH]   {i + 1:02d}. {m}")

    return resolved_matches


def collect_included_files(
    includes: list[IncludeResolved],
    excludes: list[PathResolved],
) -> tuple[list[Path], dict[Path, IncludeResolved]]:
    """Expand all include patterns and apply excludes.

    Args:
        includes: List of resolved include patterns
        excludes: List of resolved exclude patterns

    Returns:
        Tuple of (filtered file paths, mapping of file to its include)
    """
    logger = get_app_logger()
    all_files: set[Path] = set()
    # Track which include produced each file (for dest parameter and exclude checking)
    file_to_include: dict[Path, IncludeResolved] = {}

    # Expand all includes
    for inc in includes:
        matches = expand_include_pattern(inc)
        for match in matches:
            all_files.add(match)
            file_to_include[match] = inc  # Store the include for dest access

    logger.trace(
        f"[COLLECT] Found {len(all_files)} file(s) from {len(includes)} include(s)",
    )

    # Apply excludes - each exclude has its own root!
    filtered: list[Path] = []
    for file_path in all_files:
        # Check file against all excludes, using each exclude's root
        is_excluded = False
        for exc in excludes:
            exclude_root = Path(exc["root"]).resolve()
            exclude_patterns = [str(exc["path"])]
            if is_excluded_raw(file_path, exclude_patterns, exclude_root):
                logger.trace(f"[COLLECT] Excluded {file_path} by pattern {exc['path']}")
                is_excluded = True
                break
        if not is_excluded:
            filtered.append(file_path)

    logger.trace(f"[COLLECT] After excludes: {len(filtered)} file(s)")

    return sorted(filtered), file_to_include


def _normalize_order_pattern(entry: str, config_root: Path) -> str:
    """Normalize an order entry pattern relative to config_root.

    Args:
        entry: Order entry (path, relative or absolute)
        config_root: Root directory for resolving relative paths

    Returns:
        Normalized pattern string relative to config_root
    """
    pattern_path = Path(entry)
    if pattern_path.is_absolute():
        try:
            return str(pattern_path.relative_to(config_root))
        except ValueError:
            return pattern_path.name
    return entry


def _collect_recursive_files(
    root_dir: Path,
    included_set: set[Path],
    explicitly_ordered: set[Path],
) -> list[Path]:
    """Collect Python files recursively from a directory.

    Args:
        root_dir: Directory to search recursively
        included_set: Set of included file paths to filter by
        explicitly_ordered: Set of already-ordered paths to exclude

    Returns:
        List of matching file paths
    """
    if not root_dir.exists():
        return []
    all_files = [p for p in root_dir.rglob("*") if p.is_file()]
    return [
        p.resolve()
        for p in all_files
        if p.suffix == ".py"
        and p.resolve() in included_set
        and p.resolve() not in explicitly_ordered
    ]


def _collect_glob_files(
    pattern_str: str,
    config_root: Path,
    included_set: set[Path],
    explicitly_ordered: set[Path],
) -> list[Path]:
    """Collect Python files matching a glob pattern.

    Args:
        pattern_str: Glob pattern string
        config_root: Root directory for glob
        included_set: Set of included file paths to filter by
        explicitly_ordered: Set of already-ordered paths to exclude

    Returns:
        List of matching file paths
    """
    all_matches = list(config_root.glob(pattern_str))
    return [
        p.resolve()
        for p in all_matches
        if p.is_file()
        and p.suffix == ".py"
        and p.resolve() in included_set
        and p.resolve() not in explicitly_ordered
    ]


def _handle_literal_file_path(
    entry: str,
    pattern_str: str,
    config_root: Path,
    included_set: set[Path],
    explicitly_ordered: set[Path],
    resolved: list[Path],
) -> bool:
    """Handle a literal file path entry.

    Args:
        entry: Original order entry string
        pattern_str: Normalized pattern string
        config_root: Root directory for resolving paths
        included_set: Set of included file paths
        explicitly_ordered: Set of already-ordered paths
        resolved: List to append resolved paths to

    Returns:
        True if handled as literal file, False if should continue pattern matching
    """
    logger = get_app_logger()
    candidate = config_root / pattern_str
    if candidate.exists() and candidate.is_dir():
        # Directory without trailing slash - treat as recursive
        return False

    # Treat as literal file path
    if candidate.is_absolute():
        path = candidate.resolve()
    else:
        path = (config_root / pattern_str).resolve()

    if path not in included_set:
        xmsg = (
            f"Order entry {entry!r} resolves to {path}, which is not in included files"
        )
        raise ValueError(xmsg)

    if path in explicitly_ordered:
        logger.warning(
            "Order entry %r (→ %s) appears multiple times in order list",
            entry,
            path,
        )
    else:
        resolved.append(path)
        explicitly_ordered.add(path)
        logger.trace("[ORDER] %r → %s", entry, path)
    return True


def resolve_order_paths(
    order: list[str],
    included_files: list[Path],
    config_root: Path,
) -> list[Path]:
    """Resolve order entries (paths) to actual file paths.

    Supports multiple pattern formats:
    - Explicit file paths: "src/serger/utils.py"
    - Non-recursive glob: "src/serger/*" (matches direct children only)
    - Recursive directory: "src/serger/" (trailing slash = recursive)
    - Recursive pattern: "src/serger/**" (explicit recursive)
    - Directory without slash: "src/serger" (if directory exists, recursive)

    Wildcard patterns are expanded to match all remaining files in included_files
    that haven't been explicitly ordered yet. Matched files are sorted alphabetically.

    Args:
        order: List of order entries (paths, relative or absolute, or glob patterns)
        included_files: List of included file paths to validate against
        config_root: Root directory for resolving relative paths

    Returns:
        Ordered list of resolved file paths

    Raises:
        ValueError: If an order entry resolves to a path not in included files
    """
    logger = get_app_logger()
    included_set = set(included_files)
    resolved: list[Path] = []
    explicitly_ordered: set[Path] = set()

    for entry in order:
        pattern_str = _normalize_order_pattern(entry, config_root)
        matching_files: list[Path] = []

        # Handle different directory pattern formats
        # (matching expand_include_pattern behavior)
        if pattern_str.endswith("/") and not has_glob_chars(pattern_str):
            # Trailing slash directory: "src/serger/" → recursive match
            logger.trace("[ORDER] Treating as trailing-slash directory: %r", entry)
            root_dir = config_root / pattern_str.rstrip("/")
            matching_files = _collect_recursive_files(
                root_dir, included_set, explicitly_ordered
            )
            if not matching_files:
                logger.trace("[ORDER] Directory does not exist: %s", root_dir)

        elif pattern_str.endswith("/**"):
            # Explicit recursive pattern: "src/serger/**" → recursive match
            logger.trace("[ORDER] Treating as recursive pattern: %r", entry)
            root_dir = config_root / pattern_str.removesuffix("/**")
            matching_files = _collect_recursive_files(
                root_dir, included_set, explicitly_ordered
            )
            if not matching_files:
                logger.trace("[ORDER] Directory does not exist: %s", root_dir)

        elif has_glob_chars(pattern_str):
            # Glob pattern: "src/serger/*" → non-recursive glob
            logger.trace("[ORDER] Expanding glob pattern: %r", entry)
            matching_files = _collect_glob_files(
                pattern_str, config_root, included_set, explicitly_ordered
            )

        else:
            # Literal path (no glob chars, no trailing slash)
            candidate = config_root / pattern_str
            if candidate.exists() and candidate.is_dir():
                # Directory without trailing slash: "src/serger" → recursive match
                logger.trace("[ORDER] Treating as directory: %r", entry)
                matching_files = _collect_recursive_files(
                    candidate, included_set, explicitly_ordered
                )
            # Try to handle as literal file path
            elif _handle_literal_file_path(
                entry,
                pattern_str,
                config_root,
                included_set,
                explicitly_ordered,
                resolved,
            ):
                continue  # Skip pattern expansion logic

        # Sort matching files alphabetically for consistent ordering
        matching_files.sort()

        for path in matching_files:
            resolved.append(path)
            explicitly_ordered.add(path)
            logger.trace("[ORDER] %r → %s (pattern match)", entry, path)

        if not matching_files:
            logger.trace("[ORDER] Pattern %r matched no files", entry)

    return resolved


def find_package_root(file_paths: list[Path]) -> Path:
    """Compute common root (lowest common ancestor) of all file paths.

    Args:
        file_paths: List of file paths

    Returns:
        Common root path (lowest common ancestor)

    Raises:
        ValueError: If no common root can be found or list is empty
    """
    if not file_paths:
        xmsg = "Cannot find package root: no file paths provided"
        raise ValueError(xmsg)

    # Resolve all paths to absolute
    resolved_paths = [p.resolve() for p in file_paths]

    # Find common prefix by comparing path parts
    first_parts = list(resolved_paths[0].parts)
    common_parts: list[str] = []

    # For single file, exclude the filename itself (return parent directory)
    if len(resolved_paths) == 1:
        # Remove the last part (filename) for single file case
        common_parts = first_parts[:-1] if len(first_parts) > 1 else first_parts
    else:
        # For multiple files, find common prefix
        for i, part in enumerate(first_parts):
            # Check if all other paths have the same part at this position
            if all(
                i < len(list(p.parts)) and list(p.parts)[i] == part
                for p in resolved_paths[1:]
            ):
                common_parts.append(part)
            else:
                break

    if not common_parts:
        # No common prefix - use filesystem root
        return Path(resolved_paths[0].anchor)

    return Path(*common_parts)


# --------------------------------------------------------------------------- #
# internal helper
# --------------------------------------------------------------------------- #


def _extract_build_metadata(
    build_cfg: BuildConfigResolved,
    root_path: Path,
) -> tuple[str, str, str]:
    """Extract version, commit, and build date for embedding.

    Args:
        build_cfg: Resolved build config
        root_path: Project root path

    Returns:
        Tuple of (version, commit, build_date)
    """
    # Use version from resolved config if available (from pyproject.toml),
    # otherwise fall back to extracting it directly
    version_raw = build_cfg.get("_pyproject_version")
    if version_raw and isinstance(version_raw, str):
        version = version_raw
    else:
        version = extract_version(root_path / "pyproject.toml")
    commit = extract_commit(root_path)
    build_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # If no version found, use timestamp as version
    if version == "unknown":
        version = build_date

    return version, commit, build_date


def run_build(  # noqa: PLR0915, PLR0912
    build_cfg: BuildConfigResolved,
) -> None:
    """Execute a single build task using a fully resolved config.

    Serger handles module stitching builds (combining Python modules into
    a single executable script). File copying is the responsibility of
    pocket-build, not serger.
    """
    logger = get_app_logger()
    dry_run = build_cfg.get("dry_run", DEFAULT_DRY_RUN)

    # Extract stitching fields from config
    package = build_cfg.get("package")
    order = build_cfg.get("order")
    license_header = build_cfg.get("license_header", "")
    out_entry = build_cfg["out"]

    # Skip if package is not provided (required for stitch builds)
    if not package:
        logger.warning(
            "Skipping build: 'package' field is required for "
            "stitch builds. This build does not have it. "
            "(File copying is handled by pocket-build, not serger.)"
        )
        return

    # Type checking - ensure correct types after narrowing
    if not isinstance(package, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        xmsg = f"Invalid package name (expected str, got {type(package).__name__})"
        raise TypeError(xmsg)
    if order is not None and not isinstance(order, list):  # pyright: ignore[reportUnnecessaryIsInstance]
        xmsg = f"Invalid order (expected list, got {type(order).__name__})"
        raise TypeError(xmsg)

    # Determine output file path
    out_path = (out_entry["root"] / out_entry["path"]).resolve()
    # Check if it's a directory (exists and is dir) or should be treated as one
    # If path doesn't exist and has no .py extension, treat as directory
    # Use the resolved path string to check for .py extension
    # (handles absolute paths correctly)
    out_path_str = str(out_path)
    is_directory = out_path.is_dir() or (
        not out_path.exists() and not out_path_str.endswith(".py")
    )
    if is_directory:
        out_path = out_path / f"{package}.py"

    if dry_run:
        logger.info("🧪 (dry-run) Would stitch %s to: %s", package, out_path)
        return

    # Collect included files using new collection functions
    includes = build_cfg.get("include", [])
    excludes = build_cfg.get("exclude", [])
    included_files, file_to_include = collect_included_files(includes, excludes)

    if not included_files:
        xmsg = "No files found matching include patterns"
        raise ValueError(xmsg)

    # Get config root for resolving order paths
    config_root = build_cfg["__meta__"]["config_root"]

    # Compute package root for module name derivation (needed for auto-discovery)
    package_root = find_package_root(included_files)

    # Resolve order paths (order is list[str] of paths, or None for auto-discovery)
    topo_paths: list[Path] | None = None
    if order is not None:
        # Use explicit order from config
        order_paths = resolve_order_paths(order, included_files, config_root)
        logger.debug("Using explicit order from config (%d entries)", len(order_paths))
    else:
        # Auto-discover order via topological sort
        logger.info("Auto-discovering module order via topological sort...")
        order_paths = compute_module_order(
            included_files, package_root, package, file_to_include
        )
        logger.debug("Auto-discovered order (%d modules)", len(order_paths))
        # When auto-discovered, order_paths IS the topological order, so we can reuse it
        topo_paths = order_paths

    # Resolve exclude_names to paths (exclude_names is list[str] of paths)
    exclude_names_raw = build_cfg.get("exclude_names", [])
    exclude_paths: list[Path] = []
    if exclude_names_raw:
        included_set = set(included_files)
        for exclude_name in cast("list[str]", exclude_names_raw):
            # Resolve path (absolute or relative to config_root)
            if Path(exclude_name).is_absolute():
                exclude_path = Path(exclude_name).resolve()
            else:
                exclude_path = (config_root / exclude_name).resolve()
            if exclude_path in included_set:
                exclude_paths.append(exclude_path)

    # Prepare config dict for stitch_modules
    display_name_raw = build_cfg.get("display_name", "")
    description_raw = build_cfg.get("description", "")
    repo_raw = build_cfg.get("repo", "")
    post_processing = build_cfg.get("post_processing")

    stitch_config: dict[str, object] = {
        "package": package,
        "order": order_paths,  # Pass resolved paths
        "exclude_names": exclude_paths,  # Pass resolved paths
        "display_name": display_name_raw,
        "description": description_raw,
        "repo": repo_raw,
        "topo_paths": topo_paths,  # Pre-computed topological order (if auto-discovered)
    }

    # Extract metadata for embedding (use package_root as root_path)
    version, commit, build_date = _extract_build_metadata(build_cfg, package_root)

    # Create parent directory if needed
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("🧵 Stitching %s → %s", package, out_path)

    try:
        stitch_modules(
            config=stitch_config,
            file_paths=included_files,
            package_root=package_root,
            file_to_include=file_to_include,
            out_path=out_path,
            license_header=license_header,
            version=version,
            commit=commit,
            build_date=build_date,
            post_processing=post_processing,
        )
        logger.info("✅ Stitch completed → %s\n", out_path)
    except RuntimeError as e:
        xmsg = f"Stitch build failed: {e}"
        raise RuntimeError(xmsg) from e


def run_all_builds(
    resolved_builds: list[BuildConfigResolved],
    *,
    dry_run: bool,
) -> None:
    logger = get_app_logger()
    root_level = logger.level_name
    logger.trace(f"[run_all_builds] Processing {len(resolved_builds)} build(s)")

    for i, build_cfg in enumerate(resolved_builds, 1):
        build_log_level = build_cfg.get("log_level")

        build_cfg["dry_run"] = dry_run

        # apply build-specific log level temporarily
        needs_override = build_log_level and build_log_level != root_level
        context = (
            logger.use_level(cast_hint(str, build_log_level))
            if needs_override
            else contextlib.nullcontext()
        )

        with context:
            if needs_override:
                logger.debug("Overriding log level → %s", build_log_level)

            logger.info("▶️  Build %d/%d", i, len(resolved_builds))
            run_build(build_cfg)

    logger.info("🎉 All builds complete.")


# === serger.actions ===
# src/serger/actions.py


def _collect_included_files(resolved_builds: list[BuildConfigResolved]) -> list[Path]:
    """Flatten all include globs into a unique list of files.

    Uses collect_included_files() from build.py for consistency.
    Watch mode respects excludes from config.
    """
    all_files: list[Path] = []

    for b in resolved_builds:
        includes = b.get("include", [])
        excludes = b.get("exclude", [])
        # Collect files for this build (watch mode respects excludes from config)
        files, _file_to_include = collect_included_files(includes, excludes)
        all_files.extend(files)

    # Return unique sorted list
    return sorted(set(all_files))


def watch_for_changes(
    rebuild_func: Callable[[], None],
    resolved_builds: list[BuildConfigResolved],
    interval: float = DEFAULT_WATCH_INTERVAL,
) -> None:
    """Poll file modification times and rebuild when changes are detected.

    Features:
    - Skips files inside each build's output directory.
    - Re-expands include patterns every loop to detect newly created files.
    - Polling interval defaults to 1 second (tune 0.5–2.0 for balance).
    Stops on KeyboardInterrupt.
    """
    logger = get_app_logger()
    logger.info(
        "👀 Watching for changes (interval=%.2fs)... Press Ctrl+C to stop.", interval
    )

    # discover at start
    included_files = _collect_included_files(resolved_builds)

    mtimes: dict[Path, float] = {
        f: f.stat().st_mtime for f in included_files if f.exists()
    }

    # Collect all output paths to ignore (can be directories or files)
    out_paths: list[Path] = []
    for b in resolved_builds:
        out_path = (b["out"]["root"] / b["out"]["path"]).resolve()
        out_paths.append(out_path)

    rebuild_func()  # initial build

    try:
        while True:
            time.sleep(interval)

            # 🔁 re-expand every tick so new/removed files are tracked
            included_files = _collect_included_files(resolved_builds)

            logger.trace(f"[watch] Checking {len(included_files)} files for changes")

            changed: list[Path] = []
            for f in included_files:
                # skip files that are inside or equal to any output path
                if any(f == out_p or f.is_relative_to(out_p) for out_p in out_paths):
                    continue  # ignore output files/folders
                old_m = mtimes.get(f)
                if not f.exists():
                    if old_m is not None:
                        changed.append(f)
                        mtimes.pop(f, None)
                    continue
                new_m = f.stat().st_mtime
                if old_m is None or new_m > old_m:
                    changed.append(f)
                    mtimes[f] = new_m

            if changed:
                logger.info(
                    "\n🔁 Detected %d modified file(s). Rebuilding...", len(changed)
                )
                rebuild_func()
                # refresh timestamps after rebuild
                mtimes = {f: f.stat().st_mtime for f in included_files if f.exists()}
    except KeyboardInterrupt:
        logger.info("\n🛑 Watch stopped.")


def _get_metadata_from_header(script_path: Path) -> tuple[str, str]:
    """Extract version and commit from standalone script.

    Prefers in-file constants (__version__, __commit__) if present;
    falls back to commented header tags.
    """
    logger = get_app_logger()
    version = "unknown"
    commit = "unknown"

    logger.trace("reading commit from header:", script_path)

    with suppress(Exception):
        text = script_path.read_text(encoding="utf-8")

        # --- Prefer Python constants if defined ---
        const_version = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
        const_commit = re.search(r"__commit__\s*=\s*['\"]([^'\"]+)['\"]", text)
        if const_version:
            version = const_version.group(1)
        if const_commit:
            commit = const_commit.group(1)

        # --- Fallback: header lines ---
        if version == "unknown" or commit == "unknown":
            for line in text.splitlines():
                if line.startswith("# Version:") and version == "unknown":
                    version = line.split(":", 1)[1].strip()
                elif line.startswith("# Commit:") and commit == "unknown":
                    commit = line.split(":", 1)[1].strip()

    return version, commit


def get_metadata() -> Metadata:
    """Return (version, commit) tuple for this tool.

    - Standalone script → parse from header
    - Source installed → read pyproject.toml + git
    """
    script_path = Path(__file__)
    logger = get_app_logger()
    logger.trace("get_metadata ran from:", Path(__file__).resolve())

    # --- Heuristic: standalone script lives outside `src/` ---
    if globals().get("__STANDALONE__", False):
        version, commit = _get_metadata_from_header(script_path)
        logger.trace(f"got standalone version {version} with commit {commit}")
        return Metadata(version, commit)

    # --- Modular / source installed case ---

    # Source package case
    version = "unknown"
    commit = "unknown"

    # Try pyproject.toml for version
    root = Path(__file__).resolve().parents[2]
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        logger.trace(f"trying to read metadata from {pyproject}")
        text = pyproject.read_text()
        match = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']', text)
        if match:
            version = match.group(1)

    # Try git for commit
    with suppress(Exception):
        logger.trace("trying to get commit from git")
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        commit = result.stdout.strip()

    logger.trace(f"got package version {version} with commit {commit}")
    return Metadata(version, commit)


# === serger.selftest ===
# src/serger/selftest.py
"""Self-test functionality for verifying stitching works correctly."""


# Expected exit code from test script (42 * 2 = 84)
EXPECTED_EXIT_CODE = 84


def _create_test_package(pkg_dir: Path) -> None:
    """Create test package modules for selftest.

    Args:
        pkg_dir: Directory where test package modules should be created

    Raises:
        PermissionError: If unable to write files (environment issue)
        OSError: If directory operations fail (environment issue)
    """
    logger = get_app_logger()
    logger.trace("[SELFTEST] _create_test_package: pkg_dir=%s", pkg_dir)

    # base.py - simple module with a constant
    base_file = pkg_dir / "base.py"
    logger.trace("[SELFTEST] Creating base.py at %s", base_file)
    base_file.write_text(
        '"""Base module for selftest."""\nBASE_VALUE = 42\n',
        encoding="utf-8",
    )

    # utils.py - module that uses base
    utils_file = pkg_dir / "utils.py"
    logger.trace("[SELFTEST] Creating utils.py at %s", utils_file)
    utils_file.write_text(
        '"""Utils module for selftest."""\n'
        "from testpkg.base import BASE_VALUE\n\n"
        "def get_value() -> int:\n"
        "    return BASE_VALUE * 2\n",
        encoding="utf-8",
    )

    # main.py - entry point that uses utils
    main_file = pkg_dir / "main.py"
    logger.trace("[SELFTEST] Creating main.py at %s", main_file)
    main_file.write_text(
        '"""Main module for selftest."""\n'
        "from testpkg.utils import get_value\n\n"
        "def main(args: list[str] | None = None) -> int:\n"
        "    result = get_value()\n"
        "    print(f'Result: {result}')\n"
        "    return result\n",
        encoding="utf-8",
    )

    logger.debug(
        "[SELFTEST] Created test package modules: %s, %s, %s",
        base_file.name,
        utils_file.name,
        main_file.name,
    )


def _create_build_config(
    test_pkg_dir: Path, out_file: Path, tmp_dir: Path
) -> BuildConfigResolved:
    """Create build configuration for test package stitching.

    Args:
        test_pkg_dir: Directory containing test package modules
        out_file: Path where stitched output should be written
        tmp_dir: Temporary directory root for path resolution

    Returns:
        BuildConfigResolved configuration for stitching

    Raises:
        RuntimeError: If config construction fails (program bug)
    """
    logger = get_app_logger()
    logger.trace(
        "[SELFTEST] _create_build_config: test_pkg_dir=%s, out_file=%s, tmp_dir=%s",
        test_pkg_dir,
        out_file,
        tmp_dir,
    )

    try:
        include_pattern = str(test_pkg_dir / "*.py")
        logger.trace("[SELFTEST] Resolving include pattern: %s", include_pattern)
        include_resolved = make_includeresolved(include_pattern, tmp_dir, "code")
        logger.trace("[SELFTEST] Resolved include: %s", include_resolved)

        logger.trace("[SELFTEST] Resolving output path: %s", out_file)
        out_resolved = make_pathresolved(out_file, tmp_dir, "code")
        logger.trace("[SELFTEST] Resolved output: %s", out_resolved)

        # Order entries should be file paths relative to tmp_dir (config_root)
        # Since include pattern is testpkg_dir/*.py, files are under testpkg_dir
        order_entries = [
            str((test_pkg_dir / "base.py").relative_to(tmp_dir)),
            str((test_pkg_dir / "utils.py").relative_to(tmp_dir)),
            str((test_pkg_dir / "main.py").relative_to(tmp_dir)),
        ]
        config = {
            "package": "testpkg",
            "order": order_entries,
            "include": [include_resolved],
            "exclude": [],
            "out": out_resolved,
            # Don't care about user's gitignore in selftest
            "respect_gitignore": False,
            "log_level": DEFAULT_LOG_LEVEL,
            "strict_config": DEFAULT_STRICT_CONFIG,
            "dry_run": False,
            "__meta__": {"cli_root": tmp_dir, "config_root": tmp_dir},
        }
        logger.trace(
            "[SELFTEST] Build config created: package=%s, order=%s",
            "testpkg",
            config["order"],
        )
        return cast("BuildConfigResolved", config)
    except Exception as e:
        xmsg = f"Config construction failed: {e}"
        logger.trace("[SELFTEST] Config construction error: %s", e, exc_info=True)
        raise RuntimeError(xmsg) from e


def _execute_build(build_cfg: BuildConfigResolved) -> None:
    """Execute stitch build in both dry-run and real modes.

    Args:
        build_cfg: Build configuration to execute

    Raises:
        RuntimeError: If build execution fails (program bug)
    """
    logger = get_app_logger()
    logger.trace("[SELFTEST] _execute_build: package=%s", build_cfg.get("package"))

    for dry_run in (True, False):
        build_cfg["dry_run"] = dry_run
        phase = "dry-run" if dry_run else "real"
        logger.debug("[SELFTEST] Running stitch build (%s mode)", phase)
        logger.trace(
            "[SELFTEST] Build config: package=%s, out=%s, include_count=%d",
            build_cfg.get("package"),
            build_cfg.get("out"),
            len(build_cfg.get("include", [])),
        )

        phase_start = time.time()
        try:
            run_build(build_cfg)
            phase_elapsed = time.time() - phase_start
            logger.trace(
                "[SELFTEST] Build phase '%s' completed in %.3fs",
                phase,
                phase_elapsed,
            )
        except Exception as e:
            phase_elapsed = time.time() - phase_start
            logger.trace(
                "[SELFTEST] Build phase '%s' failed after %.3fs: %s",
                phase,
                phase_elapsed,
                e,
                exc_info=True,
            )
            xmsg = f"Stitch build failed ({phase} mode): {e}"
            raise RuntimeError(xmsg) from e


def _verify_compiles(stitched_file: Path) -> None:
    """Verify that the stitched file compiles without syntax errors.

    Args:
        stitched_file: Path to stitched Python file

    Raises:
        RuntimeError: If compilation fails (program bug - stitched output invalid)
    """
    logger = get_app_logger()
    file_size = stitched_file.stat().st_size
    logger.trace(
        "[SELFTEST] _verify_compiles: file=%s, size=%d bytes",
        stitched_file,
        file_size,
    )

    try:
        py_compile.compile(str(stitched_file), doraise=True)
        logger.debug(
            "[SELFTEST] Stitched file compiles successfully: %s", stitched_file
        )
    except py_compile.PyCompileError as e:
        lineno = getattr(e, "lineno", "unknown")
        logger.trace("[SELFTEST] Compilation error: %s at line %s", e.msg, lineno)
        xmsg = f"Stitched file has syntax errors at line {lineno}: {e.msg}"
        raise RuntimeError(xmsg) from e


def _verify_executes(stitched_file: Path) -> None:
    """Verify that the stitched file executes and produces expected output.

    Args:
        stitched_file: Path to stitched Python file

    Raises:
        FileNotFoundError: If python3 is not found (environment issue)
        RuntimeError: If execution fails or produces unexpected output (program bug)
        AssertionError: If output validation fails (program bug)
    """
    logger = get_app_logger()
    logger.trace("[SELFTEST] _verify_executes: file=%s", stitched_file)

    python_cmd = ["python3", str(stitched_file)]
    logger.trace("[SELFTEST] Executing: %s", " ".join(python_cmd))

    try:
        exec_start = time.time()
        result = subprocess.run(  # noqa: S603
            python_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        exec_elapsed = time.time() - exec_start
        logger.trace(
            "[SELFTEST] Execution completed in %.3fs: exit=%d, "
            "stdout_len=%d, stderr_len=%d",
            exec_elapsed,
            result.returncode,
            len(result.stdout),
            len(result.stderr),
        )

        # Check that expected output is present
        output = result.stdout
        expected_output = f"Result: {EXPECTED_EXIT_CODE}"
        if expected_output not in output:
            logger.trace(
                "[SELFTEST] Output mismatch: expected=%r, got_stdout=%r, got_stderr=%r",
                expected_output,
                output,
                result.stderr,
            )
            xmsg = (
                f"Unexpected output from stitched script. "
                f"Expected '{expected_output}' in stdout, but got: {output!r}. "
                f"stderr: {result.stderr!r}, exit code: {result.returncode}"
            )
            raise AssertionError(xmsg)

        # Exit code 84 is expected (the return value of main())
        # Any other non-zero exit code indicates an error
        if result.returncode not in {EXPECTED_EXIT_CODE, 0}:
            logger.trace(
                "[SELFTEST] Unexpected exit code: got=%d, expected=%s",
                result.returncode,
                {EXPECTED_EXIT_CODE, 0},
            )
            xmsg = (
                f"Stitched script execution failed with exit code "
                f"{result.returncode} (expected {EXPECTED_EXIT_CODE} or 0). "
                f"stderr: {result.stderr!r}"
            )
            raise RuntimeError(xmsg)

        logger.debug(
            "[SELFTEST] Stitched file executes correctly: exit=%d, output=%r",
            result.returncode,
            output.strip(),
        )

    except FileNotFoundError as e:
        # python3 not found - environment issue
        logger.trace("[SELFTEST] python3 not found: %s", e)
        xmsg = (
            f"python3 interpreter not found. Please ensure Python 3 is installed "
            f"and available in your PATH. Error: {e}"
        )
        raise FileNotFoundError(xmsg) from e

    except subprocess.TimeoutExpired as e:
        logger.trace("[SELFTEST] Execution timed out after 10s")
        xmsg = "Stitched script execution timed out after 10 seconds"
        raise RuntimeError(xmsg) from e


def _verify_content(stitched_file: Path) -> None:
    """Verify that key content markers are present in stitched file.

    Args:
        stitched_file: Path to stitched Python file

    Raises:
        AssertionError: If expected markers are not found (program bug)
    """
    logger = get_app_logger()
    logger.trace("[SELFTEST] _verify_content: file=%s", stitched_file)

    content = stitched_file.read_text(encoding="utf-8")
    content_size = len(content)
    line_count = content.count("\n") + 1
    logger.trace(
        "[SELFTEST] Content size: %d bytes, %d lines", content_size, line_count
    )

    expected_markers = [
        "# === base ===",
        "# === utils ===",
        "# === main ===",
        "BASE_VALUE = 42",
        "def get_value()",
        "def main(",
    ]
    logger.trace("[SELFTEST] Checking %d content markers", len(expected_markers))

    for marker in expected_markers:
        if marker not in content:
            logger.trace("[SELFTEST] Missing marker: %r", marker)
            xmsg = (
                f"Expected marker '{marker}' not found in stitched output. "
                f"This indicates the stitching process did not include "
                f"expected content."
            )
            raise AssertionError(xmsg)

    logger.debug(
        "[SELFTEST] All content markers verified (%d markers)",
        len(expected_markers),
    )


def run_selftest() -> bool:  # noqa: PLR0915
    """Run a lightweight functional test of the stitching functionality.

    Creates a simple test package with multiple Python modules, stitches them
    together, and verifies the output compiles and executes correctly.

    Returns:
        True if selftest passes, False otherwise
    """
    logger = get_app_logger()

    # Always run selftest with at least DEBUG level, then revert
    with logger.use_level("DEBUG", minimum=True):
        logger.info("🧪 Running self-test...")

        # Log environment info for GitHub issue reporting
        try:
            metadata = get_metadata()
            logger.debug(
                "[SELFTEST] Environment: %s %s, Python %s (%s) on %s",
                PROGRAM_DISPLAY,
                metadata,
                platform.python_version(),
                platform.python_implementation(),
                platform.system(),
            )
            logger.debug(
                "[SELFTEST] Python details: %s",
                sys.version.replace("\n", " "),
            )
        except Exception:  # noqa: BLE001
            # Metadata is optional for selftest, continue if it fails
            logger.trace("[SELFTEST] Failed to get metadata (non-fatal)")

        start_time = time.time()
        tmp_dir: Path | None = None
        stitched_file: Path | None = None

        try:
            logger.trace("[SELFTEST] Creating temporary directory")
            tmp_dir = Path(tempfile.mkdtemp(prefix=f"{PROGRAM_SCRIPT}-selftest-"))
            test_pkg_dir = tmp_dir / "testpkg"
            out_dir = tmp_dir / "out"
            test_pkg_dir.mkdir()
            out_dir.mkdir()

            logger.debug("[SELFTEST] Temp dir: %s", tmp_dir)
            logger.trace(
                "[SELFTEST] Test package dir: %s, Output dir: %s",
                test_pkg_dir,
                out_dir,
            )

            # --- Phase 1: Create test package modules ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 1: Creating test package modules")
            _create_test_package(test_pkg_dir)
            logger.debug(
                "[SELFTEST] Phase 1 completed in %.3fs",
                time.time() - phase_start,
            )

            # --- Phase 2: Prepare stitch config ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 2: Preparing stitch configuration")
            stitched_file = out_dir / "testpkg.py"
            build_cfg = _create_build_config(test_pkg_dir, stitched_file, tmp_dir)
            logger.debug(
                "[SELFTEST] Phase 2 completed in %.3fs, output will be: %s",
                time.time() - phase_start,
                stitched_file,
            )

            # --- Phase 3: Execute build (both dry and real) ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 3: Executing stitch build")
            _execute_build(build_cfg)
            logger.debug(
                "[SELFTEST] Phase 3 completed in %.3fs",
                time.time() - phase_start,
            )

            # --- Phase 4: Validate stitched output ---
            phase_start = time.time()
            logger.debug("[SELFTEST] Phase 4: Validating stitched output")
            if not stitched_file.exists():
                xmsg = (
                    f"Expected stitched output file missing: {stitched_file}. "
                    f"This indicates the build process did not create the output file."
                )
                raise RuntimeError(xmsg)  # noqa: TRY301

            file_size = stitched_file.stat().st_size
            logger.debug(
                "[SELFTEST] Stitched file exists: %s (%d bytes)",
                stitched_file,
                file_size,
            )
            logger.trace(
                "[SELFTEST] Stitched file path (absolute): %s",
                stitched_file.resolve(),
            )

            _verify_compiles(stitched_file)
            _verify_executes(stitched_file)
            _verify_content(stitched_file)
            logger.debug(
                "[SELFTEST] Phase 4 completed in %.3fs",
                time.time() - phase_start,
            )

            elapsed = time.time() - start_time
            logger.info(
                "✅ Self-test passed in %.2fs — %s is working correctly.",
                elapsed,
                PROGRAM_DISPLAY,
            )
            logger.trace("[SELFTEST] Total test duration: %.6fs", elapsed)

        except (PermissionError, OSError, FileNotFoundError) as e:
            # Environment issues: file system permissions, temp dir creation,
            # python3 not found, missing dependencies, etc.
            if isinstance(e, FileNotFoundError) and "python3" in str(e).lower():
                msg_template = (
                    "Self-test failed due to missing dependency or tool "
                    "(this is likely a problem with your environment, not with %s): %s"
                )
            else:
                msg_template = (
                    "Self-test failed due to environment issue (this is likely "
                    "a problem with your system setup, not with %s): %s"
                )
            logger.error_if_not_debug(msg_template, PROGRAM_DISPLAY, e)
            logger.debug(
                "[SELFTEST] Environment issue details: error=%s, tmp_dir=%s",
                e,
                tmp_dir,
            )
            return False

        except RuntimeError as e:
            # Program bugs: build failures, compilation errors, execution errors
            stitched_file_info = str(stitched_file) if stitched_file else "N/A"
            logger.error_if_not_debug(
                "Self-test failed (this appears to be a bug in %s): %s",
                PROGRAM_DISPLAY,
                e,
            )
            logger.debug(
                "[SELFTEST] Program bug details: error=%s, tmp_dir=%s, "
                "stitched_file=%s",
                e,
                tmp_dir,
                stitched_file_info,
            )
            return False

        except AssertionError as e:
            # Program bugs: validation failures, content mismatches
            stitched_file_info = str(stitched_file) if stitched_file else "N/A"
            logger.error_if_not_debug(
                "Self-test failed validation (this appears to be a bug in %s): %s",
                PROGRAM_DISPLAY,
                e,
            )
            logger.debug(
                "[SELFTEST] Validation failure: error=%s, tmp_dir=%s, stitched_file=%s",
                e,
                tmp_dir,
                stitched_file_info,
            )
            return False

        except Exception as e:
            # Unexpected program bugs: should never happen
            logger.exception(
                "Unexpected self-test failure (this is a bug in %s). "
                "Please report this traceback in a GitHub issue:",
                PROGRAM_DISPLAY,
            )
            logger.debug(
                "[SELFTEST] Unexpected error: type=%s, error=%s, tmp_dir=%s",
                type(e).__name__,
                e,
                tmp_dir,
            )
            return False

        else:
            return True

        finally:
            if tmp_dir and tmp_dir.exists():
                logger.trace("[SELFTEST] Cleaning up temp dir: %s", tmp_dir)
                shutil.rmtree(tmp_dir, ignore_errors=True)


# === serger.cli ===
# src/serger/cli.py


# --------------------------------------------------------------------------- #
# CLI setup and helpers
# --------------------------------------------------------------------------- #


class HintingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        # Build known option strings: ["-v", "--verbose", "--log-level", ...]
        known_opts: list[str] = []
        for action in self._actions:
            known_opts.extend([s for s in action.option_strings if s])

        hint_lines: list[str] = []
        # Argparse message for bad flags is typically
        # "unrecognized arguments: --inclde ..."
        if "unrecognized arguments:" in message:
            bad = message.split("unrecognized arguments:", 1)[1].strip()
            # Split conservatively on whitespace
            bad_args = [tok for tok in bad.split() if tok.startswith("-")]
            for arg in bad_args:
                close = get_close_matches(arg, known_opts, n=1, cutoff=0.6)
                if close:
                    hint_lines.append(f"Hint: did you mean {close[0]}?")

        # Print usage + the original error
        self.print_usage(sys.stderr)
        full = f"{self.prog}: error: {message}"
        if hint_lines:
            full += "\n" + "\n".join(hint_lines)
        self.exit(2, full + "\n")


def _setup_parser() -> argparse.ArgumentParser:
    """Define and return the CLI argument parser."""
    parser = HintingArgumentParser(prog=PROGRAM_SCRIPT)

    # --- Positional shorthand arguments ---
    parser.add_argument(
        "positional_include",
        nargs="*",
        metavar="INCLUDE",
        help="Positional include paths or patterns (shorthand for --include).",
    )
    parser.add_argument(
        "positional_out",
        nargs="?",
        metavar="OUT",
        help=(
            "Positional output file or directory (shorthand for --out). "
            "Use trailing slash for directories (e.g., 'dist/'), "
            "otherwise treated as file."
        ),
    )

    # --- Standard flags ---
    parser.add_argument(
        "--include",
        nargs="+",
        help="Override include patterns. Format: path or path:dest",
    )
    parser.add_argument("--exclude", nargs="+", help="Override exclude patterns.")
    parser.add_argument(
        "-o",
        "--out",
        help=(
            "Override output file or directory. "
            "Use trailing slash for directories (e.g., 'dist/'), "
            "otherwise treated as file. "
            "Examples: 'dist/serger.py' (file) or 'bin/' (directory)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate build actions without copying or deleting files.",
    )
    parser.add_argument("-c", "--config", help="Path to build config file.")

    parser.add_argument(
        "--add-include",
        nargs="+",
        help=(
            "Additional include paths (relative to cwd). "
            "Format: path or path:dest. Extends config includes."
        ),
    )
    parser.add_argument(
        "--add-exclude",
        nargs="+",
        help="Additional exclude patterns (relative to cwd). Extends config excludes.",
    )

    parser.add_argument(
        "--watch",
        nargs="?",
        type=float,
        metavar="SECONDS",
        default=None,
        help=(
            "Rebuild automatically on changes. "
            "Optionally specify interval in seconds"
            f" (default config or: {DEFAULT_WATCH_INTERVAL}). "
        ),
    )

    # --- Gitignore behavior ---
    gitignore = parser.add_mutually_exclusive_group()
    gitignore.add_argument(
        "--gitignore",
        dest="respect_gitignore",
        action="store_true",
        help="Respect .gitignore when selecting files (default).",
    )
    gitignore.add_argument(
        "--no-gitignore",
        dest="respect_gitignore",
        action="store_false",
        help="Ignore .gitignore and include all files.",
    )
    gitignore.set_defaults(respect_gitignore=None)

    # --- Color ---
    color = parser.add_mutually_exclusive_group()
    color.add_argument(
        "--no-color",
        dest="use_color",
        action="store_const",
        const=False,
        help="Disable ANSI color output.",
    )
    color.add_argument(
        "--color",
        dest="use_color",
        action="store_const",
        const=True,
        help="Force-enable ANSI color output (overrides auto-detect).",
    )
    color.set_defaults(use_color=None)

    # --- Version and verbosity ---
    parser.add_argument("--version", action="store_true", help="Show version info.")

    log_level = parser.add_mutually_exclusive_group()
    log_level.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const="warning",
        dest="log_level",
        help="Suppress non-critical output (same as --log-level warning).",
    )
    log_level.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const="debug",
        dest="log_level",
        help="Verbose output (same as --log-level debug).",
    )
    log_level.add_argument(
        "--log-level",
        choices=LEVEL_ORDER,
        default=None,
        dest="log_level",
        help="Set log verbosity level.",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run a built-in sanity test to verify tool correctness.",
    )
    return parser


def _normalize_positional_args(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> None:
    """Normalize positional arguments into explicit include/out flags."""
    logger = get_app_logger()
    includes: list[str] = getattr(args, "positional_include", [])
    out_pos: str | None = getattr(args, "positional_out", None)

    # If no --out, assume last positional is output if we have ≥2 positionals
    if not getattr(args, "out", None) and len(includes) >= 2 and not out_pos:  # noqa: PLR2004
        out_pos = includes.pop()

    # If --out provided, treat all positionals as includes
    elif getattr(args, "out", None) and out_pos:
        logger.trace(
            "Interpreting all positionals as includes since --out was provided.",
        )
        includes.append(out_pos)
        out_pos = None

    # Conflict: can't mix --include and positional includes
    if getattr(args, "include", None) and (includes or out_pos):
        parser.error(
            "Cannot mix positional include arguments with --include; "
            "use --out for destination or --add-include to extend."
        )

    # Internal sanity check
    assert not (getattr(args, "out", None) and out_pos), (  # only for dev # noqa: S101
        "out_pos not cleared after normalization"
    )

    # Assign normalized values
    if includes:
        args.include = includes
    if out_pos:
        args.out = out_pos


# --------------------------------------------------------------------------- #
# Main entry helpers
# --------------------------------------------------------------------------- #


@dataclass
class _LoadedConfig:
    """Container for loaded and resolved configuration data."""

    config_path: Path | None
    root_cfg: RootConfig
    resolved_root: RootConfigResolved
    resolved_builds: list[BuildConfigResolved]
    config_dir: Path
    cwd: Path


def _initialize_logger(args: argparse.Namespace) -> None:
    """Initialize logger with CLI args, env vars, and defaults."""
    logger = get_app_logger()
    logger.setLevel(logger.determine_log_level(args=args))
    logger.enable_color = getattr(
        args, "enable_color", logger.determine_color_enabled()
    )
    logger.trace("[BOOT] log-level initialized: %s", logger.level_name)

    logger.debug(
        "Runtime: Python %s (%s)\n    %s",
        platform.python_version(),
        platform.python_implementation(),
        sys.version.replace("\n", " "),
    )


def _validate_includes(
    root_cfg: RootConfig,
    resolved_builds: list[BuildConfigResolved],
    resolved_root: RootConfigResolved,
    args: argparse.Namespace,
) -> bool:
    """
    Validate that builds have include patterns.

    Returns True if validation passes, False if we should abort.
    Logs appropriate warnings/errors.
    """
    logger = get_app_logger()

    # Check for builds with missing includes. Respect per-build strict_config:
    # - If ANY build with no includes has strict_config=true → error (abort)
    # - If ALL builds with no includes have strict_config=false → warning (continue)
    # - If builds=[] and root strict_config=true → error
    # - If builds=[] and root strict_config=false → warning
    #
    # The presence of "include" key (even if empty) signals intentional choice:
    #   [] or includes=[]                  → include:[] in build → no check
    #   {"include": []}                    → include:[] in build → no check
    #   {"builds": [{"include": []}]}      → include:[] in build → no check
    #
    # Missing "include" key likely means forgotten:
    #   {} or ""                           → no include key → check
    #   {"builds": []}                     → no include key → check
    #   {"log_level": "debug"}             → no include key → check
    #   {"builds": [{"out": "dist"}]}      → no include key → check
    original_builds = root_cfg.get("builds", [])
    has_explicit_include_key = any(
        isinstance(b, dict) and "include" in b  # pyright: ignore[reportUnnecessaryIsInstance]
        for b in original_builds
    )

    # Check if any builds have missing includes (respecting CLI overrides)
    has_cli_includes = bool(
        getattr(args, "add_include", None) or getattr(args, "include", None)
    )

    # Builds with no includes
    builds_missing_includes = [b for b in resolved_builds if not b.get("include")]

    # Check if ALL builds have no includes (including zero builds)
    all_builds_missing = len(resolved_builds) == 0 or len(
        builds_missing_includes
    ) == len(resolved_builds)

    if not has_explicit_include_key and not has_cli_includes and all_builds_missing:
        # Determine if we should error or warn based on strict_config
        # If builds exist, check ANY build for strict_config=true
        # If no builds, use root-level strict_config
        if builds_missing_includes:
            any_strict = any(
                b.get("strict_config", True) for b in builds_missing_includes
            )
        else:
            # No builds at all - use root strict_config
            any_strict = resolved_root.get("strict_config", True)

        if any_strict:
            # Error: at least one build with missing includes is strict
            logger.error(
                "No include patterns found "
                "(strict_config=true prevents continuing).\n"
                "   Use 'include' in your config or pass "
                "--include / --add-include.",
            )
            return False

        # Warning: builds have no includes but all are non-strict
        logger.warning(
            "No include patterns found.\n"
            "   Use 'include' in your config or pass "
            "--include / --add-include.",
        )

    return True


def _handle_early_exits(args: argparse.Namespace) -> int | None:
    """
    Handle early exit conditions (version, selftest, Python version check).

    Returns exit code if we should exit early, None otherwise.
    """
    logger = get_app_logger()

    # --- Version flag ---
    if getattr(args, "version", None):
        meta = get_metadata()
        standalone = " [standalone]" if globals().get("__STANDALONE__", False) else ""
        logger.info(
            "%s %s (%s)%s", PROGRAM_DISPLAY, meta.version, meta.commit, standalone
        )
        return 0

    # --- Python version check ---
    if get_sys_version_info() < (3, 10):
        logger.error("%s requires Python 3.10 or newer.", {PROGRAM_DISPLAY})
        return 1

    # --- Self-test mode ---
    if getattr(args, "selftest", None):
        return 0 if run_selftest() else 1

    return None


def _load_and_resolve_config(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> _LoadedConfig:
    """Load config, normalize args, and resolve final configuration."""
    logger = get_app_logger()

    # --- Load configuration ---
    config_path: Path | None = None
    root_cfg: RootConfig | None = None
    config_result = load_and_validate_config(args)
    if config_result is not None:
        config_path, root_cfg, _validation_summary = config_result

    logger.trace("[CONFIG] log-level re-resolved from config: %s", logger.level_name)

    # --- Normalize shorthand arguments ---
    _normalize_positional_args(args, parser)
    cwd = Path.cwd().resolve()
    config_dir = config_path.parent if config_path else cwd

    # --- Configless early bailout ---
    if root_cfg is None and not can_run_configless(args):
        logger.error(
            "No build config found (.%s.json) and no includes provided.",
            PROGRAM_CONFIG,
        )
        xmsg = "No config file or CLI includes provided"
        raise RuntimeError(xmsg)

    # --- CLI-only mode fallback ---
    if root_cfg is None:
        logger.info("No config file found — using CLI-only mode.")
        root_cfg = cast_hint(RootConfig, {"builds": [{}]})

    # --- Resolve config with args and defaults ---
    resolved_root = resolve_config(root_cfg, args, config_dir, cwd)
    resolved_builds = resolved_root["builds"]

    return _LoadedConfig(
        config_path=config_path,
        root_cfg=root_cfg,
        resolved_root=resolved_root,
        resolved_builds=resolved_builds,
        config_dir=config_dir,
        cwd=cwd,
    )


def _execute_builds(
    resolved_builds: list[BuildConfigResolved],
    resolved_root: RootConfigResolved,
    args: argparse.Namespace,
    argv: list[str] | None,
) -> None:
    """Execute builds either in watch mode or one-time mode."""
    watch_enabled = getattr(args, "watch", None) is not None or (
        "--watch" in (argv or [])
    )

    if watch_enabled:
        watch_interval = resolved_root["watch_interval"]
        watch_for_changes(
            lambda: run_all_builds(
                resolved_builds,
                dry_run=getattr(args, "dry_run", DEFAULT_DRY_RUN),
            ),
            resolved_builds,
            interval=watch_interval,
        )
    else:
        run_all_builds(
            resolved_builds, dry_run=getattr(args, "dry_run", DEFAULT_DRY_RUN)
        )


# --------------------------------------------------------------------------- #
# Main entry
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    logger = get_app_logger()  # init (use env + defaults)

    try:
        parser = _setup_parser()
        args = parser.parse_args(argv)

        # --- Early runtime init (use CLI + env + defaults) ---
        _initialize_logger(args)

        # --- Handle early exits (version, selftest, etc.) ---
        early_exit_code = _handle_early_exits(args)
        if early_exit_code is not None:
            return early_exit_code

        # --- Load and resolve configuration ---
        config = _load_and_resolve_config(args, parser)

        # --- Validate includes ---
        if not _validate_includes(
            config.root_cfg, config.resolved_builds, config.resolved_root, args
        ):
            return 1

        # --- Dry-run notice ---
        if getattr(args, "dry_run", None):
            logger.info("🧪 Dry-run mode: no files will be written or deleted.\n")

        # --- Config summary ---
        if config.config_path:
            logger.info("🔧 Using config: %s", config.config_path.name)
        else:
            logger.info("🔧 Running in CLI-only mode (no config file).")
        logger.info("📁 Config root: %s", config.config_dir)
        logger.info("📂 Invoked from: %s", config.cwd)
        logger.info("🔧 Running %d build(s)\n", len(config.resolved_builds))

        # --- Execute builds ---
        _execute_builds(config.resolved_builds, config.resolved_root, args, argv)

    except (FileNotFoundError, ValueError, TypeError, RuntimeError) as e:
        # controlled termination
        silent = getattr(e, "silent", False)
        if not silent:
            try:
                logger.error_if_not_debug(str(e))
            except Exception:  # noqa: BLE001
                safe_log(f"[FATAL] Logging failed while reporting: {e}")
        return getattr(e, "code", 1)

    except Exception as e:  # noqa: BLE001
        # unexpected internal error
        try:
            logger.critical_if_not_debug("Unexpected internal error: %s", e)
        except Exception:  # noqa: BLE001
            safe_log(f"[FATAL] Logging failed while reporting: {e}")

        return getattr(e, "code", 1)

    else:
        return 0


# --- import shims for single-file runtime ---
def _create_pkg_module(pkg_name: str) -> types.ModuleType:
    """Create or get a package module and set up parent relationships."""
    _mod = sys.modules.get(pkg_name)
    if not _mod:
        _mod = types.ModuleType(pkg_name)
        _mod.__package__ = pkg_name
        sys.modules[pkg_name] = _mod
    # Set up parent-child relationships for nested packages
    if "." in pkg_name:
        _parent_pkg = ".".join(pkg_name.split(".")[:-1])
        _child_name = pkg_name.split(".")[-1]
        _parent = sys.modules.get(_parent_pkg)
        if _parent:
            setattr(_parent, _child_name, _mod)
    return _mod


def _setup_pkg_modules(pkg_name: str, module_names: list[str]) -> None:
    """Set up package module attributes and register submodules."""
    _mod = sys.modules.get(pkg_name)
    if not _mod:
        return
    # Copy attributes from all modules under this package
    _globals = globals()
    for _key, _value in _globals.items():
        setattr(_mod, _key, _value)
    # Register all modules under this package
    for _name in module_names:
        sys.modules[_name] = _mod
    # Set submodules as attributes on parent package
    for _name in module_names:
        if _name != pkg_name and _name.startswith(pkg_name + "."):
            _submodule_name = _name.split(".")[-1]
            if not hasattr(_mod, _submodule_name) or isinstance(
                getattr(_mod, _submodule_name, None), types.ModuleType
            ):
                setattr(_mod, _submodule_name, _mod)


_create_pkg_module("serger")
_create_pkg_module("apathetic_schema")
_create_pkg_module("apathetic_logs")
_create_pkg_module("apathetic_utils")
_create_pkg_module("serger.utils")
_create_pkg_module("serger.config")

_setup_pkg_modules(
    "serger",
    [
        "serger.constants",
        "serger.meta",
        "serger.logs",
        "serger.verify_script",
        "serger.stitch",
        "serger.build",
        "serger.actions",
        "serger.selftest",
        "serger.cli",
    ],
)
_setup_pkg_modules("apathetic_schema", ["apathetic_schema.schema"])
_setup_pkg_modules("apathetic_logs", ["apathetic_logs.logs"])
_setup_pkg_modules(
    "apathetic_utils",
    [
        "apathetic_utils.system",
        "apathetic_utils.text",
        "apathetic_utils.types",
        "apathetic_utils.files",
        "apathetic_utils.paths",
        "apathetic_utils.matching",
    ],
)
_setup_pkg_modules(
    "serger.utils",
    [
        "serger.utils.utils_types",
        "serger.utils.utils_matching",
        "serger.utils.utils_modules",
    ],
)
_setup_pkg_modules(
    "serger.config",
    [
        "serger.config.config_types",
        "serger.config.config_validate",
        "serger.config.config_loader",
        "serger.config.config_resolve",
    ],
)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
