"""RegisterDefaultLogLevel functionality for Apathetic Logging."""

from __future__ import annotations

import sys
from typing import Any

from .test_trace import (
    ApatheticLogging_Priv_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


def _get_namespace_module() -> Any:
    """Get the namespace module at runtime.

    This avoids circular import issues by accessing the namespace
    through the module system after it's been created.
    """
    # Access through sys.modules to avoid circular import
    namespace_module = sys.modules.get("apathetic_logging.namespace")
    if namespace_module is None:
        # Fallback: import if not yet loaded
        namespace_module = sys.modules["apathetic_logging.namespace"]
    return namespace_module


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
        namespace_module = _get_namespace_module()
        namespace_module._registered_default_log_level = default_level  # noqa: SLF001
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "register_default_log_level() called",
            f"default_level={default_level}",
        )
