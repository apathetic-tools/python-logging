"""Apathetic Logger implementation."""

from .logger import (
    CYAN,
    DEFAULT_APATHETIC_LOG_LEVEL,
    DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS,
    GRAY,
    GREEN,
    LEVEL_ORDER,
    RED,
    RESET,
    SILENT_LEVEL,
    TAG_STYLES,
    TEST_TRACE,
    TEST_TRACE_ENABLED,
    TRACE_LEVEL,
    YELLOW,
    ApatheticLogger,
    DualStreamHandler,
    TagFormatter,
    get_logger,
    make_test_trace,
    register_default_log_level,
    register_log_level_env_vars,
    register_logger_name,
    safe_log,
)


# Ensure logging module is extended with TRACE and SILENT levels
# This must be called before any loggers are created
ApatheticLogger.extend_logging_module()


__all__ = [
    "CYAN",
    "DEFAULT_APATHETIC_LOG_LEVEL",
    "DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS",
    "GRAY",
    "GREEN",
    "LEVEL_ORDER",
    "RED",
    "RESET",
    "SILENT_LEVEL",
    "TAG_STYLES",
    "TEST_TRACE",
    "TEST_TRACE_ENABLED",
    "TRACE_LEVEL",
    "YELLOW",
    "ApatheticLogger",
    "DualStreamHandler",
    "TagFormatter",
    "get_logger",
    "make_test_trace",
    "register_default_log_level",
    "register_log_level_env_vars",
    "register_logger_name",
    "safe_log",
]
