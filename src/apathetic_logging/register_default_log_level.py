# src/apathetic_logging/register_default_log_level.py
"""RegisterDefaultLogLevel functionality for Apathetic Logging."""

from __future__ import annotations

from .registry import (
    ApatheticLogging_Internal_Registry,
)
from .safe_trace import (
    ApatheticLogging_Internal_SafeTrace,
)


class ApatheticLogging_Internal_RegisterDefaultLogLevel:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the register_default_log_level static method.

    This class contains the register_default_log_level implementation as a static
    method. When mixed into apathetic_logging, it provides
    apathetic_logging.register_default_log_level.
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
        _registry = ApatheticLogging_Internal_Registry
        _safe_trace = ApatheticLogging_Internal_SafeTrace
        _registry.registered_priv_default_log_level = default_level
        _safe_trace.safe_trace(
            "register_default_log_level() called",
            f"default_level={default_level}",
        )
