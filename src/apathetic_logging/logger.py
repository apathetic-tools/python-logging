# src/apathetic_logging/logger.py
"""Core Logger implementation for Apathetic Logging.

See https://docs.python.org/3/library/logging.html#logging.Logger for the
complete list of standard library Logger methods that are extended by this class.

Docstrings are adapted from the standard library logging.Logger documentation
licensed under the Python Software Foundation License Version 2.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, TextIO, cast

from .constants import (
    ApatheticLogging_Internal_Constants,
)
from .dual_stream_handler import (
    ApatheticLogging_Internal_DualStreamHandler,
)
from .registry_data import (
    ApatheticLogging_Internal_RegistryData,
)
from .safe_logging import (
    ApatheticLogging_Internal_SafeLogging,
)
from .tag_formatter import (
    ApatheticLogging_Internal_TagFormatter,
)


class ApatheticLogging_Internal_LoggerCore(logging.Logger):  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Core Logger implementation for all Apathetic tools.

    This class contains the core Logger implementation.
    It provides all the custom methods and functionality for apathetic logging.
    """

    enable_color: bool = False
    """Enable ANSI color output for log messages."""

    _logging_module_extended: bool = False

    # if stdout or stderr are redirected, we need to repoint
    _last_stream_ids: tuple[TextIO, TextIO] | None = None

    DEFAULT_STACKLEVEL = 2
    """Default stacklevel for errorIfNotDebug/criticalIfNotDebug methods."""

    def __init__(
        self,
        name: str,
        level: int = logging.NOTSET,
        *,
        enable_color: bool | None = None,
        propagate: bool = False,
    ) -> None:
        """Initialize the logger.

        Resolves log level, color support, and log propagation.

        Args:
            name: Logger name
            level: Initial logging level (defaults to NOTSET, then auto-resolved)
            enable_color: Force color output on/off, or None for auto-detect
            propagate: False avoids duplicate root logs
        """
        # it is too late to call extendLoggingModule

        # now let's init our logger
        super().__init__(name, level)

        # default level resolution
        if self.level == logging.NOTSET:
            self.setLevel(self.determineLogLevel())

        # detect color support once per instance
        self.enable_color = (
            enable_color
            if enable_color is not None
            else type(self).determineColorEnabled()
        )

        self.propagate = propagate

        # handler attachment will happen in _log() with ensureHandlers()

    def ensureHandlers(self) -> None:
        """Ensure handlers are attached to this logger.

        DualStreamHandler is what will ensure logs go to the write channel.

        Rebuilds handlers if they're missing or if stdout/stderr have changed.
        """
        _dual_stream_handler = ApatheticLogging_Internal_DualStreamHandler
        _tag_formatter = ApatheticLogging_Internal_TagFormatter
        _safe_logging = ApatheticLogging_Internal_SafeLogging
        if self._last_stream_ids is None or not self.handlers:
            rebuild = True
        else:
            last_stdout, last_stderr = self._last_stream_ids
            rebuild = last_stdout is not sys.stdout or last_stderr is not sys.stderr

        if rebuild:
            self.handlers.clear()
            h = _dual_stream_handler.DualStreamHandler()
            h.setFormatter(_tag_formatter.TagFormatter("%(message)s"))
            h.enable_color = self.enable_color
            self.addHandler(h)
            self._last_stream_ids = (sys.stdout, sys.stderr)
            _safe_logging.safeTrace(
                "ensureHandlers()", f"rebuilt_handlers={self.handlers}"
            )

    def _log(  # type: ignore[override]
        self, level: int, msg: str, args: tuple[Any, ...], **kwargs: Any
    ) -> None:
        """Log a message with the specified level.

        Changed:
        - Automatically ensures handlers are attached via ensureHandlers()

        Args:
            level: The numeric logging level
            msg: The message format string
            args: Arguments for the message format string
            **kwargs: Additional keyword arguments passed to the base implementation

        Wrapper for logging.Logger._log.

        https://docs.python.org/3.10/library/logging.html#logging.Logger._log
        """
        self.ensureHandlers()
        super()._log(level, msg, args, **kwargs)

    def setLevel(self, level: int | str, *, minimum: bool | None = False) -> None:
        """Set the logging level of this logger.

        Changed:
        - Accepts both int and str level values (case-insensitive for strings)
        - Automatically resolves string level names to numeric values
        - Supports custom level names (TEST, TRACE, BRIEF, DETAIL, SILENT)
        - Validates that custom levels are not set to 0, which would cause
          NOTSET inheritance from root logger
        - Added `minimum` parameter: if True, only sets the level if it's more
          verbose (lower numeric value) than the current level

        Args:
            level: The logging level, either as an integer or a string name
                (case-insensitive). Standard levels (DEBUG, INFO, WARNING, ERROR,
                CRITICAL) and custom levels (TEST, TRACE, BRIEF, DETAIL, SILENT)
                are supported.
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current level. This prevents downgrading
                from a more verbose level (e.g., TRACE) to a less verbose one
                (e.g., DEBUG). Defaults to False. None is accepted and treated
                as False.

        Wrapper for logging.Logger.setLevel.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.setLevel
        """
        from .logging_utils import (  # noqa: PLC0415
            ApatheticLogging_Internal_LoggingUtils,
        )

        _logging_utils = ApatheticLogging_Internal_LoggingUtils

        # Resolve string to integer if needed using utility function
        if isinstance(level, str):
            level = _logging_utils.getLevelNumber(level)

        # Handle minimum level logic (None is treated as False)
        if minimum:
            current_level = self.getEffectiveLevel()
            # Lower number = more verbose, so only set if new level is more verbose
            if level >= current_level:
                # Don't downgrade - keep current level
                return

        # Validate any level <= 0 (prevents NOTSET inheritance)
        # Built-in levels (DEBUG=10, INFO=20, etc.) are all > 0, so they pass
        # validateLevelPositive() will raise if level <= 0
        # At this point, level is guaranteed to be int (resolved above)
        level_name = _logging_utils.getLevelNameStr(level)
        self.validateLevelPositive(level, level_name=level_name)

        super().setLevel(level)

    @classmethod
    def determineColorEnabled(cls) -> bool:
        """Return True if colored output should be enabled."""
        # Respect explicit overrides
        if "NO_COLOR" in os.environ:
            return False
        if os.getenv("FORCE_COLOR", "").lower() in {"1", "true", "yes"}:
            return True

        # Auto-detect: use color if output is a TTY
        return sys.stdout.isatty()

    @staticmethod
    def validateLevelPositive(level: int, *, level_name: str | None = None) -> None:
        """Validate that a level value is positive (> 0).

        Custom levels with values <= 0 will inherit from the root logger,
        causing NOTSET inheritance issues.

        Args:
            level: The numeric level value to validate
            level_name: Optional name for the level (for error messages).
                If None, will attempt to get from getLevelName()

        Raises:
            ValueError: If level <= 0

        Example:
            >>> Logger.validateLevelPositive(5, level_name="TRACE")
            >>> Logger.validateLevelPositive(0, level_name="TEST")
            ValueError: Level 'TEST' has value 0...
        """
        if level <= 0:
            if level_name is None:
                from .logging_utils import (  # noqa: PLC0415
                    ApatheticLogging_Internal_LoggingUtils,
                )

                level_name = ApatheticLogging_Internal_LoggingUtils.getLevelNameStr(
                    level
                )
            msg = (
                f"Level '{level_name}' has value {level}, "
                "which is <= 0. This causes NOTSET inheritance from root logger. "
                "Levels must be > 0."
            )
            raise ValueError(msg)

    @staticmethod
    def addLevelName(level: int, level_name: str) -> None:
        """Associate a level name with a numeric level.

        Changed:
        - Validates that level value is positive (> 0) to prevent NOTSET
          inheritance issues
        - Sets logging.<LEVEL_NAME> attribute for convenience, matching the
          pattern of built-in levels (logging.DEBUG, logging.INFO, etc.)
        - Validates existing attributes to ensure consistency

        Args:
            level: The numeric level value (must be > 0 for custom levels)
            level_name: The name to associate with this level

        Raises:
            ValueError: If level <= 0 (which would cause NOTSET inheritance)
            ValueError: If logging.<LEVEL_NAME> already exists with an invalid value
                (not a positive integer, or different from the provided level)

        Wrapper for logging.addLevelName.

        https://docs.python.org/3.10/library/logging.html#logging.addLevelName
        """
        # Validate level is positive
        ApatheticLogging_Internal_LoggerCore.validateLevelPositive(
            level, level_name=level_name
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
            ApatheticLogging_Internal_LoggerCore.validateLevelPositive(
                existing_value, level_name=level_name
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
    def extendLoggingModule(
        cls,
    ) -> bool:
        """The return value tells you if we ran or not.
        If it is False and you're calling it via super(),
        you can likely skip your code too.

        Note for tests:
            When testing isinstance checks on logger instances, use
            ``logging.getLoggerClass()`` instead of direct class references
            (e.g., ``mod_alogs.Logger``). This works reliably in both installed
            and singlefile runtime modes because it uses the actual class object
            that was set via ``logging.setLoggerClass()``, rather than a class
            reference from the import shim which may have different object identity
            in singlefile mode.

        Example:
                # ✅ Good: Works in both installed and singlefile modes
                assert isinstance(logger, logging.getLoggerClass())

                # ❌ May fail in singlefile mode due to class identity differences
                assert isinstance(logger, mod_alogs.Logger)
        """
        _constants = ApatheticLogging_Internal_Constants
        # Check if this specific class has already extended the module
        # (not inherited from base class)
        already_extended = getattr(cls, "_logging_module_extended", False)

        # Always set the logger class to cls, even if already extended.
        # This allows subclasses to override the logger class.
        # stdlib unwrapped
        logging.setLoggerClass(cls)

        # If already extended, skip the rest (level registration, etc.)
        if already_extended:
            return False
        cls._logging_module_extended = True

        # Sanity check: validate TAG_STYLES keys are in LEVEL_ORDER
        if __debug__:
            _tag_levels = set(_constants.TAG_STYLES.keys())
            _known_levels = {lvl.upper() for lvl in _constants.LEVEL_ORDER}
            if not _tag_levels <= _known_levels:
                _msg = "TAG_STYLES contains unknown levels"
                raise AssertionError(_msg)

        # Register custom levels with validation
        # addLevelName() also sets logging.TEST, logging.TRACE, etc. attributes
        cls.addLevelName(_constants.TEST_LEVEL, "TEST")
        cls.addLevelName(_constants.TRACE_LEVEL, "TRACE")
        cls.addLevelName(_constants.DETAIL_LEVEL, "DETAIL")
        cls.addLevelName(_constants.BRIEF_LEVEL, "BRIEF")
        cls.addLevelName(_constants.SILENT_LEVEL, "SILENT")

        return True

    def determineLogLevel(
        self,
        *,
        args: argparse.Namespace | None = None,
        root_log_level: str | None = None,
    ) -> str:
        """Resolve log level from CLI → env → root config → default."""
        _registry = ApatheticLogging_Internal_RegistryData
        _constants = ApatheticLogging_Internal_Constants
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
                    "registered_internal_log_level_env_vars",
                    None,
                )
                registered_default = getattr(
                    namespace_class,
                    "registered_internal_default_log_level",
                    None,
                )
            else:
                # Fallback to direct registry access
                registry_cls = _registry
                registered_env_vars = (
                    registry_cls.registered_internal_log_level_env_vars
                )
                registered_default = registry_cls.registered_internal_default_log_level
        else:
            # Fallback to direct registry access
            registered_env_vars = _registry.registered_internal_log_level_env_vars
            registered_default = _registry.registered_internal_default_log_level

        env_vars_to_check = (
            registered_env_vars or _constants.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
        )
        for env_var in env_vars_to_check:
            env_log_level = os.getenv(env_var)
            if env_log_level:
                return env_log_level.upper()

        if root_log_level:
            return root_log_level.upper()

        # Use registered default, or fall back to module default
        default_level: str = (
            registered_default or _constants.DEFAULT_APATHETIC_LOG_LEVEL
        )
        return default_level.upper()

    @property
    def levelName(self) -> str:
        """Return the explicit level name set on this logger.

        This property returns the name of the level explicitly set on this logger
        (via self.level). For the effective level name (what's actually used,
        considering inheritance), use effectiveLevelName instead.

        See also: logging.getLevelName, effectiveLevelName
        """
        return self.getLevelName()

    @property
    def effectiveLevel(self) -> int:
        """Return the effective level (what's actually used).

        This property returns the effective logging level for this logger,
        considering inheritance from parent loggers. This is the preferred
        way to get the effective level. Also available via getEffectiveLevel()
        for stdlib compatibility.

        See also: logging.Logger.getEffectiveLevel, effectiveLevelName
        """
        return self.getEffectiveLevel()

    @property
    def effectiveLevelName(self) -> str:
        """Return the effective level name (what's actually used).

        This property returns the name of the effective logging level for this
        logger, considering inheritance from parent loggers. This is the
        preferred way to get the effective level name. Also available via
        getEffectiveLevelName() for consistency.

        See also: logging.getLevelName, effectiveLevel
        """
        return self.getEffectiveLevelName()

    def getLevel(self) -> int:
        """Return the explicit level set on this logger.

        This method returns the level explicitly set on this logger (via
        self.level). For the effective level (what's actually used, considering
        inheritance), use getEffectiveLevel() or the effectiveLevel property.

        Returns:
            The explicit level value (int) set on this logger.

        See also: level property, getEffectiveLevel
        """
        return self.level

    def getLevelName(self) -> str:
        """Return the explicit level name set on this logger.

        This method returns the name of the level explicitly set on this logger
        (via self.level). For the effective level name (what's actually used,
        considering inheritance), use getEffectiveLevelName() or the
        effectiveLevelName property.

        Returns:
            The explicit level name (str) set on this logger.

        See also: levelName property, getEffectiveLevelName
        """
        from .logging_utils import (  # noqa: PLC0415
            ApatheticLogging_Internal_LoggingUtils,
        )

        return ApatheticLogging_Internal_LoggingUtils.getLevelNameStr(self.level)

    def getEffectiveLevelName(self) -> str:
        """Return the effective level name (what's actually used).

        This method returns the name of the effective logging level for this
        logger, considering inheritance from parent loggers. Prefer the
        effectiveLevelName property for convenience, or use this method for
        consistency with getEffectiveLevel().

        Returns:
            The effective level name (str) for this logger.

        See also: effectiveLevelName property, getEffectiveLevel
        """
        from .logging_utils import (  # noqa: PLC0415
            ApatheticLogging_Internal_LoggingUtils,
        )

        return ApatheticLogging_Internal_LoggingUtils.getLevelNameStr(
            self.getEffectiveLevel()
        )

    def errorIfNotDebug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs an exception with the real traceback starting from the caller.
        Only shows full traceback if debug/trace is enabled."""
        exc_info = kwargs.pop("exc_info", True)
        stacklevel = kwargs.pop("stacklevel", self.DEFAULT_STACKLEVEL)
        if self.isEnabledFor(logging.DEBUG):
            self.exception(
                msg, *args, exc_info=exc_info, stacklevel=stacklevel, **kwargs
            )
        else:
            self.error(msg, *args, **kwargs)

    def criticalIfNotDebug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs an exception with the real traceback starting from the caller.
        Only shows full traceback if debug/trace is enabled."""
        exc_info = kwargs.pop("exc_info", True)
        stacklevel = kwargs.pop("stacklevel", self.DEFAULT_STACKLEVEL)
        if self.isEnabledFor(logging.DEBUG):
            self.exception(
                msg, *args, exc_info=exc_info, stacklevel=stacklevel, **kwargs
            )
        else:
            self.critical(msg, *args, **kwargs)

    def colorize(
        self, text: str, color: str, *, enable_color: bool | None = None
    ) -> str:
        """Apply ANSI color codes to text.

        Defaults to using the instance's enable_color setting.

        Args:
            text: Text to colorize
            color: ANSI color code
            enable_color: Override color setting, or None to use instance default

        Returns:
            Colorized text if enabled, otherwise original text
        """
        _constants = ApatheticLogging_Internal_Constants
        if enable_color is None:
            enable_color = self.enable_color
        return f"{color}{text}{_constants.ANSIColors.RESET}" if enable_color else text

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a trace-level message (more verbose than DEBUG)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.TRACE_LEVEL):
            self._log(_constants.TRACE_LEVEL, msg, args, **kwargs)

    def detail(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a detail-level message (more detailed than INFO)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.DETAIL_LEVEL):
            self._log(
                _constants.DETAIL_LEVEL,
                msg,
                args,
                **kwargs,
            )

    def brief(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a brief-level message (less detailed than INFO)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.BRIEF_LEVEL):
            self._log(
                _constants.BRIEF_LEVEL,
                msg,
                args,
                **kwargs,
            )

    def test(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a test-level message (most verbose, bypasses capture)."""
        _constants = ApatheticLogging_Internal_Constants
        if self.isEnabledFor(_constants.TEST_LEVEL):
            self._log(_constants.TEST_LEVEL, msg, args, **kwargs)

    def logDynamic(self, level: str | int, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with a dynamically provided log level
           (unlike .info(), .error(), etc.).

        Useful when you have a log level (string or numeric) and don't want to resolve
        either the string to int, or the int to a log method.

        Args:
            level: Log level as string name or integer
            msg: Message format string
            *args: Arguments for message formatting
            **kwargs: Additional keyword arguments
        """
        # Resolve level
        if isinstance(level, str):
            from .logging_utils import (  # noqa: PLC0415
                ApatheticLogging_Internal_LoggingUtils,
            )

            try:
                level_no = ApatheticLogging_Internal_LoggingUtils.getLevelNumber(level)
            except ValueError:
                self.error("Unknown log level: %r", level)
                return
        elif isinstance(level, int):  # pyright: ignore[reportUnnecessaryIsInstance]
            level_no = level
        else:
            self.error("Invalid log level type: %r", type(level))
            return

        self._log(level_no, msg, args, **kwargs)

    @contextmanager
    def useLevel(
        self, level: str | int, *, minimum: bool = False
    ) -> Generator[None, None, None]:
        """Use a context to temporarily log with a different log-level.

        Args:
            level: Log level to use (string name or numeric value)
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current effective level. This prevents
                downgrading from a more verbose level (e.g., TRACE) to a less
                verbose one (e.g., DEBUG). Compares against effective level
                (considering parent inheritance), matching setLevel(minimum=True)
                behavior. Defaults to False.

        Yields:
            None: Context manager yields control to the with block
        """
        # Save explicit level for restoration (not effective level)
        prev_level = self.level

        # Resolve level
        if isinstance(level, str):
            from .logging_utils import (  # noqa: PLC0415
                ApatheticLogging_Internal_LoggingUtils,
            )

            try:
                level_no = ApatheticLogging_Internal_LoggingUtils.getLevelNumber(level)
            except ValueError:
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
            # Compare against effective level (not explicit level) to match
            # setLevel(minimum=True) behavior. This ensures consistent behavior
            # when logger inherits level from parent.
            current_effective_level = self.getEffectiveLevel()
            # Lower number = more verbose, so only set if new level is more verbose
            if level_no < current_effective_level:
                self.setLevel(level_no)
            # Otherwise keep current level (don't downgrade)
        else:
            self.setLevel(level_no)

        try:
            yield
        finally:
            self.setLevel(prev_level)
