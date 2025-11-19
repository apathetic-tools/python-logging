# src/apathetic_logging/namespace.py
"""Shared Apathetic CLI logger implementation."""

from __future__ import annotations

from .constants import (
    ApatheticLogging_Internal_Constants,
)
from .dual_stream_handler import (
    ApatheticLogging_Internal_DualStreamHandler,
)
from .get_logger import (
    ApatheticLogging_Internal_GetLogger,
)
from .logger import (
    ApatheticLogging_Internal_Logger,
)
from .registry import (
    ApatheticLogging_Internal_Registry,
)
from .registry_data import (
    ApatheticLogging_Internal_RegistryData,
)
from .safe_logging import (
    ApatheticLogging_Internal_SafeLogging,
)
from .tag_formatter import (
    ApatheticLogging_Internal_TagFormatter,
)


# --- Apathetic Logging Namespace -------------------------------------------


class apathetic_logging(  # noqa: N801
    ApatheticLogging_Internal_Constants,
    ApatheticLogging_Internal_DualStreamHandler,
    ApatheticLogging_Internal_GetLogger,
    ApatheticLogging_Internal_Logger,
    ApatheticLogging_Internal_Registry,
    ApatheticLogging_Internal_RegistryData,
    ApatheticLogging_Internal_SafeLogging,
    ApatheticLogging_Internal_TagFormatter,
):
    """Namespace for apathetic logging functionality.

    All logger functionality is accessed via this namespace class to minimize
    global namespace pollution when the library is embedded in a stitched script.

    **Classes:**
    - ``Logger`` → ``ApatheticLogging_Internal_Logger``
    - ``TagFormatter`` → ``ApatheticLogging_Internal_TagFormatter``
    - ``DualStreamHandler`` → ``ApatheticLogging_Internal_DualStreamHandler``

    **Static Methods:**
    - ``get_logger()`` → ``ApatheticLogging_Internal_GetLogger``
    - ``register_default_log_level()`` → ``ApatheticLogging_Internal_Registry``
    - ``register_log_level_env_vars()`` → ``ApatheticLogging_Internal_Registry``
    - ``register_logger_name()`` → ``ApatheticLogging_Internal_Registry``
    - ``safe_log()`` → ``ApatheticLogging_Internal_SafeLogging``
    - ``safe_trace()`` → ``ApatheticLogging_Internal_SafeLogging``
    - ``make_safe_trace()`` → ``ApatheticLogging_Internal_SafeLogging``

    **Constants:**
    - ``DEFAULT_APATHETIC_LOG_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS`` → ``ApatheticLogging_Internal_Constants``
    - ``SAFE_TRACE_ENABLED`` → ``ApatheticLogging_Internal_Constants``
    - ``TEST_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``TRACE_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``MINIMAL_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``DETAIL_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``SILENT_LEVEL`` → ``ApatheticLogging_Internal_Constants``
    - ``LEVEL_ORDER`` → ``ApatheticLogging_Internal_Constants``
    - ``ANSIColors`` → ``ApatheticLogging_Internal_Constants``
    - ``TAG_STYLES`` → ``ApatheticLogging_Internal_Constants``
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
