# src/apathetic_logging/registry.py
"""Registry functionality for Apathetic Logging."""

from __future__ import annotations

import sys

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
    - ``extract_top_level_package()``: Extract top-level package from full path
    """

    @staticmethod
    def extract_top_level_package(package_name: str | None) -> str | None:
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
        _registry = ApatheticLogging_Internal_Registry
        _registry_data = ApatheticLogging_Internal_RegistryData
        _safe_logging = ApatheticLogging_Internal_SafeLogging
        auto_inferred = False
        if logger_name is None:
            # Extract top-level package from the namespace module's __package__
            namespace_module = sys.modules.get("apathetic_logging.namespace")
            if namespace_module is None:
                namespace_module = sys.modules["apathetic_logging.namespace"]
            package = getattr(namespace_module, "__package__", None)
            if package:
                logger_name = _registry.extract_top_level_package(package)
                auto_inferred = True
            if logger_name is None:
                _msg = (
                    "Cannot auto-infer logger name: __package__ is not set. "
                    "Please call register_logger_name() with an explicit logger name."
                )
                raise RuntimeError(_msg)

        _registry_data.registered_internal_logger_name = logger_name
        _safe_logging.safe_trace(
            "register_logger_name() called",
            f"name={logger_name}",
            f"auto_inferred={auto_inferred}",
        )
