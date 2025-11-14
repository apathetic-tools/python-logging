# src/apathetic_logging/__init__.py
"""Apathetic Logging implementation."""

# Detect if we're in stitched mode
if globals().get("__STANDALONE__"):
    # Stitched mode: class is already in globals
    _apathetic_logging_namespace = globals()["apathetic_logging"]
else:
    # Installed mode: import normally
    from .namespace import apathetic_logging as _apathetic_logging_ns

# Ensure logging module is extended with TRACE and SILENT levels
# This must be called before any loggers are created
_apathetic_logging_ns.Logger.extend_logging_module()


# Export all namespace items for convenience
# These are aliases to apathetic_logging.*
DEFAULT_APATHETIC_LOG_LEVEL = _apathetic_logging_ns.DEFAULT_APATHETIC_LOG_LEVEL
DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS = (
    _apathetic_logging_ns.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
)
LEVEL_ORDER = _apathetic_logging_ns.LEVEL_ORDER
SILENT_LEVEL = _apathetic_logging_ns.SILENT_LEVEL
TAG_STYLES = _apathetic_logging_ns.TAG_STYLES
TEST_TRACE = _apathetic_logging_ns.TEST_TRACE
TEST_TRACE_ENABLED = _apathetic_logging_ns.TEST_TRACE_ENABLED
TRACE_LEVEL = _apathetic_logging_ns.TRACE_LEVEL

# ANSI Colors
ANSIColors = _apathetic_logging_ns.ANSIColors

# Classes
DualStreamHandler = _apathetic_logging_ns.DualStreamHandler
TagFormatter = _apathetic_logging_ns.TagFormatter

# Functions
get_logger = _apathetic_logging_ns.get_logger
make_test_trace = _apathetic_logging_ns.make_test_trace
register_default_log_level = _apathetic_logging_ns.register_default_log_level
register_log_level_env_vars = _apathetic_logging_ns.register_log_level_env_vars
register_logger_name = _apathetic_logging_ns.register_logger_name
safe_log = _apathetic_logging_ns.safe_log


__all__ = [
    "DEFAULT_APATHETIC_LOG_LEVEL",
    "DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS",
    "LEVEL_ORDER",
    "SILENT_LEVEL",
    "TAG_STYLES",
    "TEST_TRACE",
    "TEST_TRACE_ENABLED",
    "TRACE_LEVEL",
    "ANSIColors",
    "ApatheticLogging",
    "DualStreamHandler",
    "TagFormatter",
    "get_logger",
    "make_test_trace",
    "register_default_log_level",
    "register_log_level_env_vars",
    "register_logger_name",
    "safe_log",
]
