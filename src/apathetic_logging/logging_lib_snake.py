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

    This class contains snake_case wrapper functions for apathetic logging library
    functions that use camelCase naming. These wrappers provide a more Pythonic
    interface that follows PEP 8 naming conventions while maintaining full
    compatibility with the underlying apathetic logging functions.

    When mixed into apathetic_logging, it provides snake_case alternatives
    to apathetic logging functions (e.g., `getLogger` -> `get_logger`,
    `registerDefaultLogLevel` -> `register_default_log_level`,
    `safeLog` -> `safe_log`).
    """

    # --- GetLogger Functions ---

    @staticmethod
    def get_logger(
        logger_name: str | None = None,
    ) -> ApatheticLogging_Internal_Logger.Logger:
        """Get a logger with the specified name, creating it if necessary.

        If no name is specified, the logger name will be auto-inferred from the
        calling module's __package__.

        Returns an ApatheticLogging_Internal_Logger.Logger instance.

        Wrapper for ApatheticLogging_Internal_GetLogger.getLogger with
        snake_case naming.
        """
        return ApatheticLogging_Internal_GetLogger.getLogger(logger_name)

    @staticmethod
    def get_logger_of_type(
        name: str | None,
        class_type: type[Any],
        skip_frames: int = 1,
        *args: Any,
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
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            A logger instance of the specified type.

        Wrapper for ApatheticLogging_Internal_GetLogger.getLoggerOfType
        with snake_case naming.
        """
        return ApatheticLogging_Internal_GetLogger.getLoggerOfType(
            name, class_type, skip_frames, *args, **kwargs
        )

    # --- Registry Functions ---

    @staticmethod
    def register_default_log_level(default_level: str) -> None:
        """Register the default log level to use when no other source is found.

        Args:
            default_level: Default log level name (e.g., "info", "warning")

        Wrapper for ApatheticLogging_Internal_Registry.registerDefaultLogLevel
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerDefaultLogLevel(default_level)

    @staticmethod
    def register_log_level_env_vars(env_vars: list[str]) -> None:
        """Register environment variable names to check for log level.

        The environment variables will be checked in order, and the first
        non-empty value found will be used.

        Args:
            env_vars: List of environment variable names to check
                (e.g., ["MYAPP_LOG_LEVEL", "LOG_LEVEL"])

        Wrapper for ApatheticLogging_Internal_Registry.registerLogLevelEnvVars
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerLogLevelEnvVars(env_vars)

    @staticmethod
    def register_logger(
        logger_name: str | None = None,
        logger_class: type[Any] | None = None,
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
                has an ``extend_logging_module()`` method, it will be called.

        Wrapper for ApatheticLogging_Internal_Registry.registerLogger
        with snake_case naming.
        """
        ApatheticLogging_Internal_Registry.registerLogger(logger_name, logger_class)

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
    def resolve_logger_name(
        logger_name: str | None,
        *,
        check_registry: bool = True,
        skip_frames: int = 1,
    ) -> str:
        """Resolve logger name with optional inference from caller's frame.

        This is a unified helper that handles the common pattern of:
        1. Using explicit name if provided
        2. Checking registry if requested
        3. Inferring from caller's frame if needed
        4. Storing inferred name in registry
        5. Raising error if still unresolved

        Args:
            logger_name: Explicit logger name, or None to infer.
            check_registry: If True, check registry before inferring.
            skip_frames: Number of frames to skip from this function to get to
                the actual caller. Default is 1 (skips this function's frame).

        Returns:
            Resolved logger name (never None).

        Raises:
            RuntimeError: If logger name cannot be resolved.

        Wrapper for ApatheticLogging_Internal_LoggingUtils.resolveLoggerName
        with snake_case naming.
        """
        return ApatheticLogging_Internal_LoggingUtils.resolveLoggerName(
            logger_name, check_registry=check_registry, skip_frames=skip_frames
        )
