# src/apathetic_logging/namespace.py
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
from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)
from .safe_log import (
    ApatheticLogging_Priv_SafeLog,  # pyright: ignore[reportPrivateUsage]
)
from .safe_trace import (
    ApatheticLogging_Priv_SafeTrace,  # pyright: ignore[reportPrivateUsage]
)
from .tag_formatter import (
    ApatheticLogging_Priv_TagFormatter,  # pyright: ignore[reportPrivateUsage]
)


# --- Apathetic Logging Namespace -------------------------------------------


class apathetic_logging(  # pyright: ignore[reportPrivateUsage] # noqa: N801
    ApatheticLogging_Priv_Constants,
    ApatheticLogging_Priv_DualStreamHandler,
    ApatheticLogging_Priv_GetLogger,
    ApatheticLogging_Priv_Logger,
    ApatheticLogging_Priv_RegisterDefaultLogLevel,
    ApatheticLogging_Priv_RegisterLogLevelEnvVars,
    ApatheticLogging_Priv_RegisterLoggerName,
    ApatheticLogging_Priv_Registry,
    ApatheticLogging_Priv_SafeLog,
    ApatheticLogging_Priv_TagFormatter,
    ApatheticLogging_Priv_SafeTrace,
):
    """Namespace for apathetic logging functionality.

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
    - ``SAFE_TRACE()`` → ``ApatheticLogging_Priv_SafeTrace``
    - ``make_test_trace()`` → ``ApatheticLogging_Priv_SafeTrace``

    **Constants:**
    - ``DEFAULT_APATHETIC_LOG_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS`` → ``ApatheticLogging_Priv_Constants``
    - ``SAFE_TRACE_ENABLED`` → ``ApatheticLogging_Priv_Constants``
    - ``TEST_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``TRACE_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``MINIMAL_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``DETAIL_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``SILENT_LEVEL`` → ``ApatheticLogging_Priv_Constants``
    - ``LEVEL_ORDER`` → ``ApatheticLogging_Priv_Constants``
    - ``ANSIColors`` → ``ApatheticLogging_Priv_Constants``
    - ``TAG_STYLES`` → ``ApatheticLogging_Priv_Constants``
    """


# Ensure logging module is extended with TEST, TRACE, MINIMAL, DETAIL, and SILENT
# levels
# This must be called before any loggers are created
# This runs when namespace.py is executed (both installed and stitched modes)
# The method is idempotent, so safe to call multiple times if needed
apathetic_logging.Logger.extend_logging_module()

# Note: All exports are handled in __init__.py
# - For library builds (installed/singlefile): __init__.py is included, exports happen
# - For embedded builds: __init__.py is excluded, no exports (only class available)
