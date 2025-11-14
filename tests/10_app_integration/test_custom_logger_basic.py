# tests/10_app_integration/test_custom_logger_basic.py
"""Tests for correct custom logger usage patterns from docs/custom-logger.md."""

import argparse
import logging
import os
from typing import cast

# Import from conftest in same directory
import conftest

import apathetic_logging as mod_alogs


AppLoggerForTest = conftest.AppLoggerForTest
AppLoggerWithCustomMethodForTest = conftest.AppLoggerWithCustomMethodForTest


def test_custom_logger_correct_usage_pattern() -> None:
    """Test the correct usage pattern from docs/custom-logger.md."""
    # --- setup ---
    app_name = "testapp"
    default_log_level = "info"
    log_level_env_var = "TESTAPP_LOG_LEVEL"

    # Step 1: Extend the logging module (must happen first)
    # Note: This sets the logger class globally, so logging.getLogger()
    # will create instances of AppLoggerForTest
    AppLoggerForTest.extend_logging_module()

    # Step 2: Register environment variables
    mod_alogs.register_log_level_env_vars([log_level_env_var, "LOG_LEVEL"])

    # Step 3: Register default log level
    mod_alogs.register_default_log_level(default_log_level)

    # Step 4: Register logger name
    mod_alogs.register_logger_name(app_name)

    # Step 5: Get logger instance
    # Since extend_logging_module() was called, this will be AppLoggerForTest
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))

    # --- verify ---
    assert logger is not None
    assert logger.name == app_name
    assert isinstance(logger, mod_alogs.apathetic_logging.Logger)
    # Should be able to use custom levels
    logger.setLevel("TRACE")
    assert logger.level_name == "TRACE"
    logger.setLevel("SILENT")
    assert logger.level_name == "SILENT"


def test_custom_logger_with_typed_getter() -> None:
    """Test custom logger with typed getter function."""
    # --- setup ---
    app_name = "testapp_typed"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)

    def get_app_logger() -> AppLoggerForTest:
        """Return the configured application logger."""
        logger = cast("AppLoggerForTest", mod_alogs.get_logger())
        return logger

    # --- execute ---
    logger = get_app_logger()

    # --- verify ---
    assert logger is not None
    assert logger.name == app_name
    assert isinstance(logger, mod_alogs.apathetic_logging.Logger)


def test_custom_logger_determine_log_level_override() -> None:
    """Test that custom determine_log_level() override works correctly."""
    # --- setup ---
    app_name = "testapp_determine"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    # Create logger directly to ensure we get the child class instance
    logger = AppLoggerForTest(app_name)

    # Test with command-line args
    args = argparse.Namespace(log_level="debug")
    level = logger.determine_log_level(args=args)
    assert level == "DEBUG"

    # Test with environment variable
    os.environ["TESTAPP_LOG_LEVEL"] = "warning"
    level = logger.determine_log_level()
    assert level == "WARNING"
    if "TESTAPP_LOG_LEVEL" in os.environ:
        del os.environ["TESTAPP_LOG_LEVEL"]

    # Test with root log level
    level = logger.determine_log_level(root_log_level="error")
    assert level == "ERROR"

    # Test default fallback
    level = logger.determine_log_level()
    assert level == "INFO"


def test_custom_logger_with_custom_methods() -> None:
    """Test custom logger with application-specific methods."""
    # --- setup ---
    app_name = "testapp_custom_methods"
    # Need to set logger class to our custom class
    AppLoggerWithCustomMethodForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    # Create logger directly to ensure we get the right type
    logger = AppLoggerWithCustomMethodForTest(app_name)

    # --- verify ---
    assert hasattr(logger, "log_operation")
    assert hasattr(logger, "log_performance")
    assert callable(logger.log_operation)
    assert callable(logger.log_performance)

    # Test custom methods work
    logger.setLevel("INFO")
    logger.log_operation("test_op", "success")
    logger.setLevel("DEBUG")
    logger.log_performance("latency", 42.5)
