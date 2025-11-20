# src/apathetic_logging/__init__.py
"""Apathetic Logging implementation."""

from typing import TYPE_CHECKING, TypeAlias, cast


if TYPE_CHECKING:
    from .logger import ApatheticLogging_Internal_Logger
    from .namespace import apathetic_logging as _apathetic_logging_class

# Get reference to the namespace class
# In stitched mode: class is already defined in namespace.py (executed before this)
# In installed mode: import from namespace module
_is_standalone = globals().get("__STANDALONE__", False)

if _is_standalone:
    # Stitched mode: class already defined in namespace.py
    # Get reference to the class (it's already in globals from namespace.py)
    _apathetic_logging_raw = globals().get("apathetic_logging")
    if _apathetic_logging_raw is None:
        # Fallback: should not happen, but handle gracefully
        msg = "apathetic_logging class not found in standalone mode"
        raise RuntimeError(msg)
    # Type cast to help mypy understand this is the apathetic_logging class
    # The import gives us type[apathetic_logging], so cast to
    # type[_apathetic_logging_class]
    apathetic_logging = cast("type[_apathetic_logging_class]", _apathetic_logging_raw)
else:
    # Installed mode: import from namespace module
    # This block is only executed in installed mode, not in standalone builds
    from .namespace import apathetic_logging

    # Ensure the else block is not empty (build script may remove import)
    _ = apathetic_logging

# Export all namespace items for convenience
# These are aliases to apathetic_logging.*
#
# Note: In embedded builds, __init__.py is excluded from the stitch,
# so this code never runs and no exports happen (only the class is available).
# In singlefile/installed builds, __init__.py is included, so exports happen.
DEFAULT_APATHETIC_LOG_LEVEL = apathetic_logging.DEFAULT_APATHETIC_LOG_LEVEL
DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS = (
    apathetic_logging.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
)
LEVEL_ORDER = apathetic_logging.LEVEL_ORDER
SILENT_LEVEL = apathetic_logging.SILENT_LEVEL
TAG_STYLES = apathetic_logging.TAG_STYLES
TEST_LEVEL = apathetic_logging.TEST_LEVEL
safe_trace = apathetic_logging.safe_trace
SAFE_TRACE_ENABLED = apathetic_logging.SAFE_TRACE_ENABLED
TRACE_LEVEL = apathetic_logging.TRACE_LEVEL
MINIMAL_LEVEL = apathetic_logging.MINIMAL_LEVEL
DETAIL_LEVEL = apathetic_logging.DETAIL_LEVEL

# ANSI Colors
ANSIColors = apathetic_logging.ANSIColors

# Classes
DualStreamHandler = apathetic_logging.DualStreamHandler
TagFormatter = apathetic_logging.TagFormatter
# Logger is a nested class in ApatheticLogging_Internal_Logger that
# inherits from logging.Logger.
# Use TypeAlias to help mypy understand this is a class type.
if TYPE_CHECKING:
    Logger: TypeAlias = ApatheticLogging_Internal_Logger.Logger
else:
    Logger = apathetic_logging.Logger

# Functions
get_logger = apathetic_logging.get_logger
make_safe_trace = apathetic_logging.make_safe_trace
register_default_log_level = apathetic_logging.register_default_log_level
register_log_level_env_vars = apathetic_logging.register_log_level_env_vars
register_logger = apathetic_logging.register_logger
safe_log = apathetic_logging.safe_log


__all__ = [
    "DEFAULT_APATHETIC_LOG_LEVEL",
    "DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS",
    "DETAIL_LEVEL",
    "LEVEL_ORDER",
    "MINIMAL_LEVEL",
    "SAFE_TRACE_ENABLED",
    "SILENT_LEVEL",
    "TAG_STYLES",
    "TEST_LEVEL",
    "TRACE_LEVEL",
    "ANSIColors",
    "DualStreamHandler",
    "Logger",
    "TagFormatter",
    "apathetic_logging",
    "get_logger",
    "make_safe_trace",
    "register_default_log_level",
    "register_log_level_env_vars",
    "register_logger",
    "safe_log",
    "safe_trace",
]
