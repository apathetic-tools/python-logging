# src/apathetic_logging/register_log_level_env_vars.py
"""RegisterLogLevelEnvVars functionality for Apathetic Logging."""

from __future__ import annotations

from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)
from .test_trace import (
    ApatheticLogging_Priv_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


class ApatheticLogging_Priv_RegisterLogLevelEnvVars:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the register_log_level_env_vars static method.

    This class contains the register_log_level_env_vars implementation as a static
    method. When mixed into apathetic_logging, it provides
    apathetic_logging.register_log_level_env_vars.
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
            >>> apathetic_logging.register_log_level_env_vars(
            ...     ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]
            ... )
        """
        ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars = env_vars
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "register_log_level_env_vars() called",
            f"env_vars={env_vars}",
        )
