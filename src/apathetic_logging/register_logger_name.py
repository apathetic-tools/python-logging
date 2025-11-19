# src/apathetic_logging/register_logger_name.py
"""RegisterLoggerName functionality for Apathetic Logging."""

from __future__ import annotations

import sys

from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)
from .safe_trace import (
    ApatheticLogging_Priv_SafeTrace,  # pyright: ignore[reportPrivateUsage]
)


class ApatheticLogging_Priv_RegisterLoggerName:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the register_logger_name static method.

    This class contains the register_logger_name implementation as a static
    method. When mixed into apathetic_logging, it provides
    apathetic_logging.register_logger_name.
    """

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
        auto_inferred = False
        if logger_name is None:
            # Extract top-level package from the namespace module's __package__
            namespace_module = sys.modules.get("apathetic_logging.namespace")
            if namespace_module is None:
                namespace_module = sys.modules["apathetic_logging.namespace"]
            package = getattr(namespace_module, "__package__", None)
            if package:
                logger_name = (
                    ApatheticLogging_Priv_RegisterLoggerName._extract_top_level_package(
                        package
                    )
                )
                auto_inferred = True
            if logger_name is None:
                _msg = (
                    "Cannot auto-infer logger name: __package__ is not set. "
                    "Please call register_logger_name() with an explicit logger name."
                )
                raise RuntimeError(_msg)

        ApatheticLogging_Priv_Registry.registered_priv_logger_name = logger_name
        ApatheticLogging_Priv_SafeTrace.safe_trace(
            "register_logger_name() called",
            f"name={logger_name}",
            f"auto_inferred={auto_inferred}",
        )
