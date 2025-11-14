"""RegisterDefaultLogLevel functionality for Apathetic Logging."""

from __future__ import annotations

from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)
from .test_trace import (
    ApatheticLogging_Priv_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


class ApatheticLogging_Priv_RegisterDefaultLogLevel:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the register_default_log_level static method.

    This class contains the register_default_log_level implementation as a static
    method. When mixed into ApatheticLogging, it provides
    ApatheticLogging.register_default_log_level.
    """

    @staticmethod
    def register_default_log_level(default_level: str) -> None:
        """Register the default log level to use when no other source is found.

        Args:
            default_level: Default log level name (e.g., "info", "warning")

        Example:
            >>> from apathetic_logging import ApatheticLogging
            >>> ApatheticLogging.register_default_log_level("warning")
        """
        ApatheticLogging_Priv_Registry.registered_priv_default_log_level = default_level
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "register_default_log_level() called",
            f"default_level={default_level}",
        )
