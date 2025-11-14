# tests/10_app_integration/test_custom_logger_features.py
"""Tests for tricky features with custom logger child classes."""

import logging
import os
from typing import cast

# Import from conftest in same directory
import conftest

import apathetic_logging as mod_alogs


AppLoggerForTest = conftest.AppLoggerForTest
AppLoggerWithCustomMethodForTest = conftest.AppLoggerWithCustomMethodForTest


def test_use_level_context_manager_with_child_class() -> None:
    """Test use_level() context manager works with child logger class."""
    # --- setup ---
    app_name = "testapp_use_level"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))
    logger.setLevel("INFO")

    # --- execute ---
    # Use context manager to temporarily change level
    with logger.use_level("DEBUG"):
        assert logger.level_name == "DEBUG"
        logger.debug("This should appear")

    # --- verify ---
    # Level should be restored
    assert logger.level_name == "INFO"


def test_use_level_minimum_with_child_class() -> None:
    """Test use_level() with minimum=True works with child logger class."""
    # --- setup ---
    app_name = "testapp_use_level_min"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))
    logger.setLevel("TRACE")  # More verbose

    # --- execute ---
    # Try to downgrade with minimum=True (should not downgrade)
    with logger.use_level("INFO", minimum=True):
        # Should stay at TRACE (more verbose)
        assert logger.level_name == "TRACE"

    # Try to upgrade with minimum=True (should upgrade)
    logger.setLevel("WARNING")
    with logger.use_level("DEBUG", minimum=True):
        # Should upgrade to DEBUG (more verbose)
        assert logger.level_name == "DEBUG"

    # --- verify ---
    # Should restore to WARNING
    assert logger.level_name == "WARNING"


def test_log_dynamic_with_child_class() -> None:
    """Test log_dynamic() method works with child logger class."""
    # --- setup ---
    app_name = "testapp_log_dynamic"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))
    logger.setLevel("DEBUG")

    # --- execute ---
    # Should be able to log with dynamic level
    logger.log_dynamic("debug", "Dynamic debug message")
    logger.log_dynamic(logging.INFO, "Dynamic info message")
    logger.log_dynamic("TRACE", "Dynamic trace message")

    # --- verify ---
    # Should not raise errors
    assert True  # If we get here, it worked


def test_error_if_not_debug_with_child_class() -> None:
    """Test error_if_not_debug() works with child logger class."""
    # --- setup ---
    app_name = "testapp_error_if_not_debug"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))

    # Test at INFO level (not debug)
    logger.setLevel("INFO")
    # Should log as error (not exception)
    logger.error_if_not_debug("Error message at INFO level")

    # Test at DEBUG level
    logger.setLevel("DEBUG")
    # Should log as exception (full traceback)

    def _raise_test_exception() -> None:
        test_msg = "Test exception"
        raise ValueError(test_msg)

    try:
        _raise_test_exception()
    except ValueError:
        logger.error_if_not_debug("Error message at DEBUG level")

    # --- verify ---
    # Should not raise errors
    assert True  # If we get here, it worked


def test_critical_if_not_debug_with_child_class() -> None:
    """Test critical_if_not_debug() works with child logger class."""
    # --- setup ---
    app_name = "testapp_critical_if_not_debug"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))

    # Test at INFO level (not debug)
    logger.setLevel("INFO")
    logger.critical_if_not_debug("Critical message at INFO level")

    # Test at DEBUG level
    logger.setLevel("DEBUG")

    def _raise_test_exception() -> None:
        test_msg = "Test exception"
        raise ValueError(test_msg)

    try:
        _raise_test_exception()
    except ValueError:
        logger.critical_if_not_debug("Critical message at DEBUG level")

    # --- verify ---
    # Should not raise errors
    assert True  # If we get here, it worked


def test_trace_method_with_child_class() -> None:
    """Test trace() method works with child logger class."""
    # --- setup ---
    app_name = "testapp_trace"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))

    # Test at TRACE level
    logger.setLevel("TRACE")
    logger.trace("Trace message")

    # Test at DEBUG level (trace should not appear)
    logger.setLevel("DEBUG")
    logger.trace("This trace should not appear")

    # --- verify ---
    # Should not raise errors
    assert True  # If we get here, it worked


def test_colorize_with_child_class() -> None:
    """Test colorize() method works with child logger class."""
    # --- setup ---
    app_name = "testapp_colorize"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))

    # --- execute ---
    # ANSIColors is on the namespace, not the logger instance
    colored = logger.colorize("test", mod_alogs.ANSIColors.RED)
    uncolored = logger.colorize("test", mod_alogs.ANSIColors.RED, enable_color=False)

    # --- verify ---
    assert "test" in colored
    assert uncolored == "test"  # No color codes when disabled


def test_custom_methods_inherit_base_features() -> None:
    """Test that custom methods can use inherited base logger features."""
    # --- setup ---
    app_name = "testapp_inherit"
    AppLoggerWithCustomMethodForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    # Create logger directly to ensure we get the right type
    logger = AppLoggerWithCustomMethodForTest(app_name)

    # --- execute ---
    # Custom methods should be able to use base class methods
    logger.setLevel("DEBUG")
    logger.log_performance("test_metric", 123.45)

    # Should also have access to all base methods
    logger.trace("trace from custom logger")
    logger.use_level("TRACE")
    logger.log_dynamic("info", "dynamic log")

    # --- verify ---
    assert hasattr(logger, "trace")
    assert hasattr(logger, "use_level")
    assert hasattr(logger, "log_dynamic")
    assert hasattr(logger, "log_operation")
    assert hasattr(logger, "log_performance")


def test_child_class_determine_log_level_with_registered_settings() -> None:
    """Test that child class determine_log_level() works with registered settings."""
    # --- setup ---
    app_name = "testapp_registered"
    AppLoggerForTest.extend_logging_module()
    mod_alogs.register_logger_name(app_name)
    mod_alogs.register_default_log_level("warning")
    mod_alogs.register_log_level_env_vars(["TESTAPP_LOG_LEVEL", "LOG_LEVEL"])

    # Create logger directly to ensure we get the child class instance
    logger = AppLoggerForTest(app_name)

    # Test that registered env vars are checked
    # Note: Child class checks env vars directly, not through registry
    os.environ["TESTAPP_LOG_LEVEL"] = "error"
    level = logger.determine_log_level()
    assert level == "ERROR"

    # Test fallback to child class default (not registered default)
    if "TESTAPP_LOG_LEVEL" in os.environ:
        del os.environ["TESTAPP_LOG_LEVEL"]
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]
    level = logger.determine_log_level()
    # Child class override returns "INFO" as hardcoded default
    # This shows that child class override takes precedence over registered defaults
    assert level == "INFO"  # Child override takes precedence


def test_multiple_child_classes_independent() -> None:
    """Test that multiple child classes can coexist independently."""

    # --- setup ---
    class LoggerA(mod_alogs.apathetic_logging.Logger):
        def determine_log_level(self, **_kwargs: object) -> str:
            return "DEBUG"

    class LoggerB(mod_alogs.apathetic_logging.Logger):
        def determine_log_level(self, **_kwargs: object) -> str:
            return "WARNING"

    # Both should be able to extend (second call returns False)
    result1 = LoggerA.extend_logging_module()
    result2 = LoggerB.extend_logging_module()
    # First may return False if already extended, second definitely False
    assert isinstance(result1, bool)
    assert result2 is False

    # Create instances
    logger_a = LoggerA("app_a")
    logger_b = LoggerB("app_b")

    # --- verify ---
    assert logger_a.determine_log_level() == "DEBUG"
    assert logger_b.determine_log_level() == "WARNING"
