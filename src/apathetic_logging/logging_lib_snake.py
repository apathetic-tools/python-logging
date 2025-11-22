# src/apathetic_logging/logging_lib_snake.py
"""Snake case convenience functions for apathetic logging library functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .get_logger import (
    ApatheticLogging_Internal_GetLogger,
)
from .logging_utils import (
    ApatheticLogging_Internal_LoggingUtils,
)
from .registry import (
    ApatheticLogging_Internal_Registry,
)
from .safe_logging import (
    ApatheticLogging_Internal_SafeLogging,
)


if TYPE_CHECKING:
    from collections.abc import Callable

    from .logger_namespace import (
        ApatheticLogging_Internal_Logger,
    )


class ApatheticLogging_Internal_LibSnakeCase:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides snake_case convenience functions for apathetic logging.

    **Purpose**: Extended wrappers for apathetic logging library functions with
    additional functionality beyond the standard library.

    This class contains snake_case wrapper functions for apathetic logging library
    functions that use camelCase naming. These wrappers provide a more Pythonic
    interface that follows PEP 8 naming conventions while maintaining full
    compatibility with the underlying apathetic logging functions. Unlike
    `ApatheticLogging_Internal_StdSnakeCase` (which maintains stdlib API compatibility),
    these functions explicitly document and type extended parameters that provide
    additional functionality beyond the standard library.

    When mixed into apathetic_logging, it provides snake_case alternatives
    to apathetic logging functions (e.g., `getLogger` -> `get_logger`,
    `registerDefaultLogLevel` -> `register_default_log_level`,
    `safeLog` -> `safe_log`).

    **Note**: For stdlib-compatible wrappers that match the standard library API
    exactly, see `ApatheticLogging_Internal_StdSnakeCase`.
    """

    # --- GetLogger Functions ---

    @staticmethod
    def get_logger(
        name: str | None = None,
        *args: Any,
        level: str | int | None = None,
        minimum: bool | None = None,
        **kwargs: Any,
    ) -> ApatheticLogging_Internal_Logger.Logger:
        """Get a logger with the specified name, creating it if necessary.

        **Apathetic logging library wrapper**: This function wraps apathetic logging's
        extended `getLogger()` implementation, which provides additional functionality
        beyond the standard library. Unlike the stdlib-compatible wrapper in
        `ApatheticLogging_Internal_StdSnakeCase`, this function explicitly documents
        and types extended parameters like `level` and `minimum`.

        **Note**: Due to Python's method resolution order (MRO), this function is
        the one that actually gets called at runtime (it comes before
        `ApatheticLogging_Internal_StdSnakeCase` in the inheritance chain). The
        extended parameters are therefore available and properly typed when using
        `apathetic_logging.get_logger()`.

        If no name is specified, the logger name will be auto-inferred from the
        calling module's __package__.

        Args:
            name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.
            *args: Additional positional arguments (for future-proofing)
            level: Exact log level to set on the logger. Accepts both string
                names (case-insensitive) and numeric values. If provided,
                sets the logger's level to this value. Defaults to None.
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current level. This prevents downgrading
                from a more verbose level (e.g., TRACE) to a less verbose one
                (e.g., DEBUG). If None, defaults to False. Only used when
                `level` is provided.
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            An ApatheticLogging_Internal_Logger.Logger instance.

        Wrapper for ApatheticLogging_Internal_GetLogger.getLogger with
        snake_case naming. This is the extended version with additional parameters;
        for stdlib-compatible API documentation, see
        ApatheticLogging_Internal_StdSnakeCase.get_logger.
        """
        return ApatheticLogging_Internal_GetLogger.getLogger(
            name, *args, level=level, minimum=minimum, **kwargs
        )

    @staticmethod
    def get_logger_of_type(
        name: str | None,
        class_type: type[Any],
        skip_frames: int = 1,
        *args: Any,
        level: str | int | None = None,
        minimum: bool | None = None,
        **kwargs: Any,
    ) -> Any:
        """Get a logger of the specified type, creating it if necessary.

        Args:
            name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.
            class_type: The logger class type to use.
            skip_frames: Number of frames to skip when inferring logger name.
                Prefer using as a keyword argument (e.g., skip_frames=2) for clarity.
            *args: Additional positional arguments (for future-proofing)
            level: Exact log level to set on the logger. Accepts both string
                names (case-insensitive) and numeric values. If provided,
                sets the logger's level to this value. Defaults to None.
            minimum: If True, only set the level if it's more verbose (lower
                numeric value) than the current level. This prevents downgrading
                from a more verbose level (e.g., TRACE) to a less verbose one
                (e.g., DEBUG). If None, defaults to False. Only used when
                `level` is provided.
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            A logger instance of the specified type.

        Wrapper for ApatheticLogging_Internal_GetLogger.getLoggerOfType
        with snake_case naming.
        """
        return ApatheticLogging_Internal_GetLogger.getLoggerOfType(
            name,
            class_type,
            skip_frames,
            *args,
            level=level,
            minimum=minimum,
            **kwargs,
        )

    # --- Registry Functions ---

    @staticmethod
    def register_default_log_level(default_level: str | None) -> None:
        """Register the default log level to use when no other source is found.

        Args:
            default_level: Default log level name (e.g., "info", "warning").
                If None, returns immediately without making any changes.

        Wrapper for ApatheticLogging_Internal_Registry.registerDefaultLogLevel
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerDefaultLogLevel(default_level)

    @staticmethod
    def register_log_level_env_vars(env_vars: list[str] | None) -> None:
        """Register environment variable names to check for log level.

        The environment variables will be checked in order, and the first
        non-empty value found will be used.

        Args:
            env_vars: List of environment variable names to check
                (e.g., ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]). If None, returns
                immediately without making any changes.

        Wrapper for ApatheticLogging_Internal_Registry.registerLogLevelEnvVars
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerLogLevelEnvVars(env_vars)

    @staticmethod
    def register_logger(
        logger_name: str | None = None,
        logger_class: type[Any] | None = None,
        *,
        target_python_version: tuple[int, int] | None = None,
        log_level_env_vars: list[str] | None = None,
        default_log_level: str | None = None,
        propagate: bool | None = None,
    ) -> None:
        """Register a logger for use by getLogger().

        This is the public API for registering a logger. It registers the logger
        name and extends the logging module with custom levels if needed.

        If logger_name is not provided, the top-level package is automatically
        extracted from the calling module's __package__ attribute.

        Args:
            logger_name: The name of the logger to retrieve (e.g., "myapp").
                If None, extracts the top-level package from __package__.
            logger_class: Optional logger class to use. If provided and the class
                has an ``extendLoggingModule()`` method, it will be called.
                If the class doesn't have that method, ``logging.setLoggerClass()``
                will be called directly. If None, nothing is done (default Logger
                is already set up at import time).
            target_python_version: Optional target Python version (major, minor)
                tuple. If provided, sets the target Python version in the registry
                permanently. Defaults to None (no change).
            log_level_env_vars: Optional list of environment variable names to
                check for log level. If provided, sets the log level environment
                variables in the registry permanently. Defaults to None (no change).
            default_log_level: Optional default log level name. If provided, sets
                the default log level in the registry permanently. Defaults to None
                (no change).
            propagate: Optional propagate setting. If provided, sets the propagate
                value in the registry permanently. If None, uses registered propagate
                setting or falls back to DEFAULT_PROPAGATE from constants.py.
                Defaults to None (no change).

        Wrapper for ApatheticLogging_Internal_Registry.registerLogger
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerLogger(
            logger_name,
            logger_class,
            target_python_version=target_python_version,
            log_level_env_vars=log_level_env_vars,
            default_log_level=default_log_level,
            propagate=propagate,
        )

    @staticmethod
    def register_target_python_version(version: tuple[int, int] | None) -> None:
        """Register the target Python version for compatibility checking.

        This sets the target Python version that will be used to validate
        function calls. If a function requires a Python version newer than
        the target version, it will raise a NotImplementedError even if
        the runtime version is sufficient.

        If not set, the library defaults to MIN_PYTHON_VERSION (3, 10) from
        constants.py. This allows developers to catch version incompatibilities
        during development even when running on a newer Python version than
        their target.

        Args:
            version: Target Python version as (major, minor) tuple
                (e.g., (3, 10) or (3, 11)). If None, returns immediately
                without making any changes.

        Wrapper for ApatheticLogging_Internal_Registry.registerTargetPythonVersion
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerTargetPythonVersion(version)

    @staticmethod
    def register_propagate(*, propagate: bool | None) -> None:
        """Register the propagate setting for loggers.

        This sets the default propagate value that will be used when creating
        loggers. If not set, the library defaults to DEFAULT_PROPAGATE (False)
        from constants.py.

        When propagate is False, loggers do not propagate messages to parent
        loggers, avoiding duplicate root logs.

        Args:
            propagate: Propagate setting (True or False). If None, returns
                immediately without making any changes.

        Wrapper for ApatheticLogging_Internal_Registry.registerPropagate
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerPropagate(propagate=propagate)

    @staticmethod
    def get_log_level_env_vars() -> list[str]:
        """Get the environment variable names to check for log level.

        Returns the registered environment variable names, or the default
        environment variables if none are registered.

        Returns:
            List of environment variable names to check for log level.
            Defaults to ["LOG_LEVEL"] if not registered.

        Wrapper for ApatheticLogging_Internal_Registry.getLogLevelEnvVars
        with snake_case naming.
        """
        return ApatheticLogging_Internal_Registry.getLogLevelEnvVars()

    @staticmethod
    def get_default_log_level() -> str:
        """Get the default log level.

        Returns the registered default log level, or the module default
        if none is registered.

        Returns:
            Default log level name (e.g., "detail", "info").
            Defaults to "detail" if not registered.

        Wrapper for ApatheticLogging_Internal_Registry.getDefaultLogLevel
        with snake_case naming.
        """
        return ApatheticLogging_Internal_Registry.getDefaultLogLevel()

    @staticmethod
    def get_registered_logger_name() -> str | None:
        """Get the registered logger name.

        Returns the registered logger name, or None if no logger name
        has been registered. Unlike get_default_logger_name(), this does not
        perform inference - it only returns the explicitly registered value.

        Returns:
            Registered logger name, or None if not registered.

        Wrapper for ApatheticLogging_Internal_Registry.getRegisteredLoggerName
        with snake_case naming.
        """
        return ApatheticLogging_Internal_Registry.getRegisteredLoggerName()

    @staticmethod
    def get_target_python_version() -> tuple[int, int]:
        """Get the target Python version.

        Returns the registered target Python version, or the minimum
        supported version if none is registered.

        Returns:
            Target Python version as (major, minor) tuple.
            Defaults to (3, 10) if not registered.

        Wrapper for ApatheticLogging_Internal_Registry.getTargetPythonVersion
        with snake_case naming.
        """
        return ApatheticLogging_Internal_Registry.getTargetPythonVersion()

    @staticmethod
    def get_default_propagate() -> bool:
        """Get the default propagate setting.

        Returns the registered propagate setting, or the module default
        if none is registered.

        Returns:
            Default propagate setting (True or False).
            Defaults to False if not registered.

        Wrapper for ApatheticLogging_Internal_Registry.getDefaultPropagate
        with snake_case naming.
        """
        return ApatheticLogging_Internal_Registry.getDefaultPropagate()

    # --- Safe Logging Functions ---

    @staticmethod
    def safe_log(msg: str) -> None:
        """Emergency logger that never fails.

        Wrapper for ApatheticLogging_Internal_SafeLogging.safeLog
        with snake_case naming.
        """
        ApatheticLogging_Internal_SafeLogging.safeLog(msg)

    @staticmethod
    def safe_trace(label: str, *args: Any, icon: str = "🧪") -> None:
        """Emit a synchronized, flush-safe diagnostic line.

        Args:
            label: Short identifier or context string.
            *args: Optional values to append.
            icon: Emoji prefix/suffix for easier visual scanning.

        Wrapper for ApatheticLogging_Internal_SafeLogging.safeTrace
        with snake_case naming.
        """
        ApatheticLogging_Internal_SafeLogging.safeTrace(label, *args, icon=icon)

    @staticmethod
    def make_safe_trace(icon: str = "🧪") -> Callable[..., Any]:
        """Create a local trace function with a custom icon.

        Args:
            icon: Emoji prefix/suffix for easier visual scanning.

        Returns:
            A callable trace function.

        Wrapper for ApatheticLogging_Internal_SafeLogging.makeSafeTrace
        with snake_case naming.
        """
        return ApatheticLogging_Internal_SafeLogging.makeSafeTrace(icon)

    # --- Logging Utils Functions ---

    @staticmethod
    def has_logger(logger_name: str) -> bool:
        """Check if a logger exists in the logging manager's registry.

        Args:
            logger_name: The name of the logger to check.

        Returns:
            True if the logger exists in the registry, False otherwise.

        Wrapper for ApatheticLogging_Internal_LoggingUtils.hasLogger
        with snake_case naming.
        """
        return ApatheticLogging_Internal_LoggingUtils.hasLogger(logger_name)

    @staticmethod
    def remove_logger(logger_name: str) -> None:
        """Remove a logger from the logging manager's registry.

        Args:
            logger_name: The name of the logger to remove.

        Wrapper for ApatheticLogging_Internal_LoggingUtils.removeLogger
        with snake_case naming.
        """
        ApatheticLogging_Internal_LoggingUtils.removeLogger(logger_name)

    @staticmethod
    def get_default_logger_name(
        logger_name: str | None = None,
        *,
        check_registry: bool = True,
        skip_frames: int = 1,
        raise_on_error: bool = False,
        infer: bool = True,
        register: bool = False,
    ) -> str | None:
        """Get default logger name with optional inference from caller's frame.

        This function handles the common pattern of:
        1. Using explicit name if provided
        2. Checking registry if requested
        3. Inferring from caller's frame if needed (when infer=True)
        4. Storing inferred name in registry (when register=True)
        5. Returning None or raising error if still unresolved

        Args:
            logger_name: Explicit logger name, or None to infer.
            check_registry: If True, check registry before inferring.
            skip_frames: Number of frames to skip from this function to get to
                the actual caller. Default is 1 (skips this function's frame).
            raise_on_error: If True, raise RuntimeError if logger name cannot be
                resolved. If False (default), return None instead.
            infer: If True (default), attempt to infer logger name from caller's
                frame when not found in registry. If False, skip inference.
            register: If True, store inferred name in registry. If False (default),
                do not modify registry.

        Returns:
            Resolved logger name, or None if cannot be resolved and
            raise_on_error=False.

        Raises:
            RuntimeError: If logger name cannot be resolved and raise_on_error=True.

        Wrapper for ApatheticLogging_Internal_LoggingUtils.getDefaultLoggerName
        with snake_case naming.
        """
        return ApatheticLogging_Internal_LoggingUtils.getDefaultLoggerName(
            logger_name,
            check_registry=check_registry,
            skip_frames=skip_frames,
            raise_on_error=raise_on_error,
            infer=infer,
            register=register,
        )

    @staticmethod
    def get_level_name(level: int | str, *, strict: bool = False) -> str:
        """Return the textual representation of a logging level.

        **Apathetic logging library wrapper**: This function wraps apathetic
        logging's extended `getLevelName()` implementation, which provides
        additional functionality beyond the standard library. Unlike the
        stdlib-compatible wrapper in `ApatheticLogging_Internal_StdSnakeCase`,
        this function always returns a string
        (breaking change from stdlib's bidirectional behavior).

        **Note**: Due to Python's method resolution order (MRO), this function is
        the one that actually gets called at runtime (it comes before
        `ApatheticLogging_Internal_StdSnakeCase` in the inheritance chain).

        Extended features:
        - Always returns a string (unlike stdlib which returns int for string input)
        - Accepts both int and str inputs (returns str uppercased if already str)
        - Optional strict mode to raise ValueError for unknown levels
        - Supports all levels registered via logging.addLevelName() (including
          custom apathetic levels and user-registered levels)

        Args:
            level: Log level as integer or string name
            strict: If True, raise ValueError for unknown levels. If False (default),
                returns "Level {level}" format for unknown integer levels (matching
                stdlib behavior).

        Returns:
            Level name (uppercase string). If level is already a string,
            returns it as-is (uppercased). For unknown integer levels (when
            strict=False), returns "Level {level}" format (e.g., "Level 999").

        Raises:
            ValueError: If strict=True and level cannot be resolved to a known
                level name.

        Wrapper for ApatheticLogging_Internal_LoggingUtils.getLevelName with
        snake_case naming. This is the extended version with additional functionality;
        for stdlib-compatible API documentation, see
        ApatheticLogging_Internal_StdSnakeCase.get_level_name.

        https://docs.python.org/3.10/library/logging.html#logging.getLevelName
        """
        return ApatheticLogging_Internal_LoggingUtils.getLevelName(level, strict=strict)

    @staticmethod
    def get_level_number(level: str | int) -> int:
        """Convert a log level name to its numeric value.

        Recommended way to convert string level names to integers. This function
        explicitly performs string->int conversion, unlike `get_level_name()` which
        has bidirectional behavior for backward compatibility.

        Handles all levels registered via logging.addLevelName() (including
        standard library levels, custom apathetic levels, and user-registered levels).

        Args:
            level: Log level as string name (case-insensitive) or integer

        Returns:
            Integer level value

        Raises:
            ValueError: If level cannot be resolved

        Example:
            >>> get_level_number("DEBUG")
            10
            >>> get_level_number("TRACE")
            5
            >>> get_level_number(20)
            20

        Wrapper for ApatheticLogging_Internal_LoggingUtils.getLevelNumber with
        snake_case naming.

        See Also:
            get_level_name() - Convert int to string (intended use)
        """
        return ApatheticLogging_Internal_LoggingUtils.getLevelNumber(level)
