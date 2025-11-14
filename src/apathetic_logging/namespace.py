# src/serger/utils/utils_logs.py
"""Shared Apathetic CLI logger implementation."""

from __future__ import annotations

from .constants import (
    ApatheticLogging_Priv_Constants,  # pyright: ignore[reportPrivateUsage]
)
from .dual_stream_handler import (
    ApatheticLogging_Priv_DualStreamHandler,  # pyright: ignore[reportPrivateUsage]
)
from .get_logger import (
    ApatheticLogging_Priv_GetLogger,  # pyright: ignore[reportPrivateUsage]
)
from .logger import ApatheticLogging_Priv_Logger  # pyright: ignore[reportPrivateUsage]
from .register_default_log_level import (
    ApatheticLogging_Priv_RegisterDefaultLogLevel,  # pyright: ignore[reportPrivateUsage]
)
from .register_log_level_env_vars import (
    ApatheticLogging_Priv_RegisterLogLevelEnvVars,  # pyright: ignore[reportPrivateUsage]
)
from .register_logger_name import (
    ApatheticLogging_Priv_RegisterLoggerName,  # pyright: ignore[reportPrivateUsage]
)
from .safe_log import (
    ApatheticLogging_Priv_SafeLog,  # pyright: ignore[reportPrivateUsage]
)
from .tag_formatter import (
    ApatheticLogging_Priv_TagFormatter,  # pyright: ignore[reportPrivateUsage]
)
from .test_trace import (
    ApatheticLogging_Priv_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


# --- globals ---------------------------------------------------------------

# Registry for configurable log level settings
# These must be module-level for global state management
_registered_log_level_env_vars: list[str] | None = None
_registered_default_log_level: str | None = None
_registered_logger_name: str | None = None


# --- Apathetic Logging Namespace -------------------------------------------


class ApatheticLogging(  # pyright: ignore[reportPrivateUsage]
    ApatheticLogging_Priv_Constants,
    ApatheticLogging_Priv_DualStreamHandler,
    ApatheticLogging_Priv_GetLogger,
    ApatheticLogging_Priv_Logger,
    ApatheticLogging_Priv_RegisterDefaultLogLevel,
    ApatheticLogging_Priv_RegisterLogLevelEnvVars,
    ApatheticLogging_Priv_RegisterLoggerName,
    ApatheticLogging_Priv_SafeLog,
    ApatheticLogging_Priv_TagFormatter,
    ApatheticLogging_Priv_TestTrace,
):
    """Namespace for apathetic logger functionality.

    All logger functionality is accessed via this namespace class to minimize
    global namespace pollution when the library is embedded in a stitched script.

    **Classes:**
    - ``Logger`` → ``ApatheticLogging_Priv_Logger``
    - ``TagFormatter`` → ``ApatheticLogging_Priv_TagFormatter``
    - ``DualStreamHandler`` → ``ApatheticLogging_Priv_DualStreamHandler``

    **Static Methods:**
    - ``get_logger()`` → ``ApatheticLogging_Priv_GetLogger``
    - ``register_default_log_level()`` →
      ``ApatheticLogging_Priv_RegisterDefaultLogLevel``
    - ``register_log_level_env_vars()`` →
      ``ApatheticLogging_Priv_RegisterLogLevelEnvVars``
    - ``register_logger_name()`` → ``ApatheticLogging_Priv_RegisterLoggerName``
    - ``safe_log()`` → ``ApatheticLogging_Priv_SafeLog``
    - ``TEST_TRACE()`` → ``ApatheticLogging_Priv_TestTrace``
    - ``make_test_trace()`` → ``ApatheticLogging_Priv_TestTrace``

    **Constants:**
    - ``DEFAULT_APATHETIC_LOG_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS`` → ``ApatheticLogging_Priv_Constants``
    - ``TEST_TRACE_ENABLED`` → ``ApatheticLogging_Priv_Constants``
    - ``TRACE_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``SILENT_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``LEVEL_ORDER`` → ``ApatheticLogging_Priv_Constants``
    - ``ANSIColors`` → ``ApatheticLogging_Priv_Constants``
    - ``TAG_STYLES`` → ``ApatheticLogging_Priv_Constants``
    """
