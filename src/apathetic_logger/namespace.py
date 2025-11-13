# src/serger/utils/utils_logs.py
"""Shared Apathetic CLI logger implementation."""

from __future__ import annotations

from .constants import _ApatheticLogger_Constants  # pyright: ignore[reportPrivateUsage]
from .dual_stream_handler import (
    _ApatheticLogger_DualStreamHandler,  # pyright: ignore[reportPrivateUsage]
)
from .get_logger import (
    _ApatheticLogger_GetLogger,  # pyright: ignore[reportPrivateUsage]
)
from .logger import _ApatheticLogger_Logger  # pyright: ignore[reportPrivateUsage]
from .register_default_log_level import (
    _ApatheticLogger_RegisterDefaultLogLevel,  # pyright: ignore[reportPrivateUsage]
)
from .register_log_level_env_vars import (
    _ApatheticLogger_RegisterLogLevelEnvVars,  # pyright: ignore[reportPrivateUsage]
)
from .register_logger_name import (
    _ApatheticLogger_RegisterLoggerName,  # pyright: ignore[reportPrivateUsage]
)
from .safe_log import _ApatheticLogger_SafeLog  # pyright: ignore[reportPrivateUsage]
from .tag_formatter import (
    _ApatheticLogger_TagFormatter,  # pyright: ignore[reportPrivateUsage]
)
from .test_trace import (
    _ApatheticLogger_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


# --- globals ---------------------------------------------------------------

# Registry for configurable log level settings
# These must be module-level for global state management
_registered_log_level_env_vars: list[str] | None = None
_registered_default_log_level: str | None = None
_registered_logger_name: str | None = None


# --- Apathetic Logger Namespace -------------------------------------------


class ApatheticLogger(  # pyright: ignore[reportPrivateUsage]
    _ApatheticLogger_Constants,
    _ApatheticLogger_DualStreamHandler,
    _ApatheticLogger_GetLogger,
    _ApatheticLogger_Logger,
    _ApatheticLogger_RegisterDefaultLogLevel,
    _ApatheticLogger_RegisterLogLevelEnvVars,
    _ApatheticLogger_RegisterLoggerName,
    _ApatheticLogger_SafeLog,
    _ApatheticLogger_TagFormatter,
    _ApatheticLogger_TestTrace,
):
    """Namespace for apathetic logger functionality.

    All logger functionality is accessed via this namespace class to minimize
    global namespace pollution when the library is embedded in a stitched script.

    **Classes:**
    - ``Logger`` → ``_ApatheticLogger_Logger``
    - ``TagFormatter`` → ``_ApatheticLogger_TagFormatter``
    - ``DualStreamHandler`` → ``_ApatheticLogger_DualStreamHandler``

    **Static Methods:**
    - ``get_logger()`` → ``_ApatheticLogger_GetLogger``
    - ``register_default_log_level()`` → ``_ApatheticLogger_RegisterDefaultLogLevel``
    - ``register_log_level_env_vars()`` → ``_ApatheticLogger_RegisterLogLevelEnvVars``
    - ``register_logger_name()`` → ``_ApatheticLogger_RegisterLoggerName``
    - ``safe_log()`` → ``_ApatheticLogger_SafeLog``
    - ``TEST_TRACE()`` → ``_ApatheticLogger_TestTrace``
    - ``make_test_trace()`` → ``_ApatheticLogger_TestTrace``

    **Constants:**
    - ``DEFAULT_APATHETIC_LOG_LEVEL`` → ``_ApatheticLogger_Constants``
    - ``DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS`` → ``_ApatheticLogger_Constants``
    - ``TEST_TRACE_ENABLED`` → ``_ApatheticLogger_Constants``
    - ``TRACE_LEVEL`` → ``_ApatheticLogger_Constants``
    - ``SILENT_LEVEL`` → ``_ApatheticLogger_Constants``
    - ``LEVEL_ORDER`` → ``_ApatheticLogger_Constants``
    - ``ANSIColors`` → ``_ApatheticLogger_Constants``
    - ``TAG_STYLES`` → ``_ApatheticLogger_Constants``
    """
