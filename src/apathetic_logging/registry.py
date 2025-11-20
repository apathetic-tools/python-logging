# src/apathetic_logging/registry.py
"""Registry functionality for Apathetic Logging."""

from __future__ import annotations

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
    - ``register_logger_name()``: Register a logger name
    """

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
            >>> from apathetic_logging import ApatheticLogging
            >>> apathetic_logging.register_logger_name("myapp")

            >>> # Auto-infer from __package__
            >>> apathetic_logging.register_logger_name()
            ...     # Uses top-level package from __package__
        """
        _registry_data = ApatheticLogging_Internal_RegistryData
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        _safe_logging = ApatheticLogging_Internal_SafeLogging

        # Track if name was auto-inferred
        was_explicit = logger_name is not None

        # Resolve logger name (with inference if needed)
        # skip_frames=1 because: register_logger_name -> resolve_logger_name -> caller
        # check_registry=False because register_logger_name() should actively determine
        # the name from the current context, not return an old registered name. This
        # allows re-inferring from __package__ if the package context has changed.
        resolved_name = _logging_utils.resolve_logger_name(
            logger_name,
            check_registry=False,
            skip_frames=1,
        )

        # register_logger_name always stores the result (explicit or inferred)
        _registry_data.registered_internal_logger_name = resolved_name

        _safe_logging.safe_trace(
            "register_logger_name() called",
            f"name={resolved_name}",
            f"auto_inferred={not was_explicit}",
        )
