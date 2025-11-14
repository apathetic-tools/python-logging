"""RegisterLogLevelEnvVars functionality for Apathetic Logging."""

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


class ApatheticLogging_Priv_RegisterLogLevelEnvVars:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the register_log_level_env_vars static method.

    This class contains the register_log_level_env_vars implementation as a static
    method. When mixed into ApatheticLogging, it provides
    ApatheticLogging.register_log_level_env_vars.
    """

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
            >>> ApatheticLogging.register_log_level_env_vars(
            ...     ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]
            ... )
        """
        namespace_module = _get_namespace_module()
        namespace_module._registered_log_level_env_vars = env_vars  # noqa: SLF001
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "register_log_level_env_vars() called",
            f"env_vars={env_vars}",
        )
