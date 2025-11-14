"""Apathetic Logging implementation."""

from .namespace import ApatheticLogging as _ApatheticLoggingNamespace


# Ensure logging module is extended with TRACE and SILENT levels
# This must be called before any loggers are created
_ApatheticLoggingNamespace.Logger.extend_logging_module()


# Export the namespace class
# In stitched version, only this will be in global namespace
ApatheticLogging = _ApatheticLoggingNamespace

# Export all namespace items for convenience
# These are aliases to ApatheticLogging.*
DEFAULT_APATHETIC_LOG_LEVEL = _ApatheticLoggingNamespace.DEFAULT_APATHETIC_LOG_LEVEL
DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS = (
    _ApatheticLoggingNamespace.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
)
LEVEL_ORDER = _ApatheticLoggingNamespace.LEVEL_ORDER
SILENT_LEVEL = _ApatheticLoggingNamespace.SILENT_LEVEL
TAG_STYLES = _ApatheticLoggingNamespace.TAG_STYLES
TEST_TRACE = _ApatheticLoggingNamespace.TEST_TRACE
TEST_TRACE_ENABLED = _ApatheticLoggingNamespace.TEST_TRACE_ENABLED
TRACE_LEVEL = _ApatheticLoggingNamespace.TRACE_LEVEL

# ANSI Colors
ANSIColors = _ApatheticLoggingNamespace.ANSIColors

# Classes
DualStreamHandler = _ApatheticLoggingNamespace.DualStreamHandler
TagFormatter = _ApatheticLoggingNamespace.TagFormatter

# Functions
get_logger = _ApatheticLoggingNamespace.get_logger
make_test_trace = _ApatheticLoggingNamespace.make_test_trace
register_default_log_level = _ApatheticLoggingNamespace.register_default_log_level
register_log_level_env_vars = _ApatheticLoggingNamespace.register_log_level_env_vars
register_logger_name = _ApatheticLoggingNamespace.register_logger_name
safe_log = _ApatheticLoggingNamespace.safe_log


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
