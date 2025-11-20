# src/apathetic_logging/registry.py
"""Registry functionality for Apathetic Logging."""

from __future__ import annotations

import logging
from typing import TypeVar

from .logging_utils import (
    ApatheticLogging_Internal_LoggingUtils,
)
from .registry_data import (
    ApatheticLogging_Internal_RegistryData,
)
from .safe_logging import (
    ApatheticLogging_Internal_SafeLogging,
)


class ApatheticLogging_Internal_Registry:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides registration methods.

    This class contains static methods for registering configuration values.
    When mixed into apathetic_logging, it provides registration methods for
    log level environment variables, default log level, and logger name.

    Registry storage is provided by ``ApatheticLogging_Internal_RegistryData``.

    **Static Methods:**
    - ``register_default_log_level()``: Register the default log level
    - ``register_log_level_env_vars()``: Register environment variable names
    - ``register_logger()``: Register a logger (public API)
    """

    _LoggerType = TypeVar("_LoggerType", bound=logging.Logger)

    @staticmethod
    def register_default_log_level(default_level: str) -> None:
        """Register the default log level to use when no other source is found.

        Args:
            default_level: Default log level name (e.g., "info", "warning")

        Example:
            >>> from apathetic_logging import ApatheticLogging
            >>> apathetic_logging.register_default_log_level("warning")
        """
        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging
        _registry_data.registered_internal_default_log_level = default_level
        _safe_logging.safe_trace(
            "register_default_log_level() called",
            f"default_level={default_level}",
        )

    @staticmethod
    def register_log_level_env_vars(env_vars: list[str]) -> None:
        """Register environment variable names to check for log level.

        The environment variables will be checked in order, and the first
        non-empty value found will be used.

        Args:
            env_vars: List of environment variable names to check
                (e.g., ["SERGER_LOG_LEVEL", "LOG_LEVEL"])

        Example:
            >>> from apathetic_logging import ApatheticLogging
            >>> apathetic_logging.register_log_level_env_vars(
            ...     ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]
            ... )
        """
        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging
        _registry_data.registered_internal_log_level_env_vars = env_vars
        _safe_logging.safe_trace(
            "register_log_level_env_vars() called",
            f"env_vars={env_vars}",
        )

    @staticmethod
    def register_logger(
        logger_name: str | None = None,
        logger_class: type[ApatheticLogging_Internal_Registry._LoggerType]
        | None = None,
    ) -> None:
        """Register a logger for use by get_logger().

        This is the public API for registering a logger. It registers the logger
        name and extends the logging module with custom levels if needed.

        If logger_name is not provided, the top-level package is automatically
        extracted from the calling module's __package__ attribute.

        If logger_class is provided and has an ``extend_logging_module()``
        method, it will be called to extend the logging module with custom
        levels and set the logger class. If logger_class is provided but does
        not have ``extend_logging_module()``, ``logging.setLoggerClass()``
        will be called directly to set the logger class. If logger_class is not
        provided, nothing is done with the logger class (the default ``Logger``
        is already extended at import time).

        **Important**: If you're using a custom logger class that has
        ``extend_logging_module()``, do not call ``logging.setLoggerClass()``
        directly. Instead, pass the class to ``register_logger()`` and let
        ``extend_logging_module()`` handle setting the logger class. This
        ensures consistent behavior and avoids class identity issues in
        singlefile mode.

        Args:
            logger_name: The name of the logger to retrieve (e.g., "myapp").
                If None, extracts the top-level package from __package__.
            logger_class: Optional logger class to use. If provided and the class
                has an ``extend_logging_module()`` method, it will be called.
                If the class doesn't have that method, ``logging.setLoggerClass()``
                will be called directly. If None, nothing is done (default Logger
                is already set up at import time).

        Example:
            >>> # Explicit registration with default Logger (already extended)
            >>> from apathetic_logging import register_logger
            >>> register_logger("myapp")

            >>> # Auto-infer from __package__
            >>> register_logger()
            ...     # Uses top-level package from __package__

            >>> # Register with custom logger class (has extend_logging_module)
            >>> from apathetic_logging import Logger
            >>> class AppLogger(Logger):
            ...     pass
            >>> # Don't call AppLogger.extend_logging_module() or
            >>> # logging.setLoggerClass() directly - register_logger() handles it
            >>> register_logger("myapp", AppLogger)

            >>> # Register with any logger class (no extend_logging_module)
            >>> import logging
            >>> class SimpleLogger(logging.Logger):
            ...     pass
            >>> register_logger("myapp", SimpleLogger)  # Sets logger class directly
        """
        _registry_data = ApatheticLogging_Internal_RegistryData
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        # Import Logger locally to avoid circular import

        # Track if name was auto-inferred
        was_explicit = logger_name is not None

        # Resolve logger name (with inference if needed)
        # skip_frames=1 because: register_logger -> resolve_logger_name -> caller
        # check_registry=False because register_logger() should actively determine
        # the name from the current context, not return an old registered name. This
        # allows re-inferring from __package__ if the package context has changed.
        resolved_name = _logging_utils.resolve_logger_name(
            logger_name,
            check_registry=False,
            skip_frames=1,
        )

        if logger_class is not None:
            # extend_logging_module will call setLoggerClass for those that support it
            if hasattr(logger_class, "extend_logging_module"):
                logger_class.extend_logging_module()  # type: ignore[attr-defined]
            else:
                logging.setLoggerClass(logger_class)

        # register_logger always stores the result (explicit or inferred)
        _registry_data.registered_internal_logger_name = resolved_name

        _safe_logging.safe_trace(
            "register_logger() called",
            f"name={resolved_name}",
            f"auto_inferred={not was_explicit}",
            f"logger_class={logger_class.__name__ if logger_class else None}",
        )
