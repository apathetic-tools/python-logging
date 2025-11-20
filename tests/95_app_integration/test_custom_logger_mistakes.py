# tests/95_app_integration/test_custom_logger_mistakes.py
"""Tests for common mistakes when using custom logger pattern."""

import logging
from typing import cast

# Import from conftest in same directory
import conftest
import pytest

import apathetic_logging as mod_alogs


AppLoggerForTest = conftest.AppLoggerForTest


def test_forgetting_extend_logging_module_before_get_logger() -> None:
    """Test what happens when extend_logging_module() is forgotten.

    This simulates a user creating a logger before calling extend_logging_module().
    """
    # --- setup ---
    app_name = "testapp_no_extend"

    # User forgets to call extend_logging_module() first
    # But it's already called at import time in __init__.py
    # So we need to test the case where they create a logger directly
    # without going through the normal pattern

    # --- execute ---
    # Create logger directly (extend_logging_module was called at import)
    logger = AppLoggerForTest(app_name)

    # --- verify ---
    # Should still work because extend_logging_module was called at import
    assert logger is not None
    assert logger.name == app_name
    # Should have TRACE and SILENT available
    assert hasattr(logging, "TRACE")
    assert hasattr(logging, "SILENT")


def test_registering_after_get_logger() -> None:
    """Test registering things AFTER getLogger() and instantiation.

    This tests the ordering issue where users might register configuration
    after they've already gotten the logger.
    """
    # --- setup ---
    app_name = "testapp_late_register"

    # User creates logger first
    AppLoggerForTest.extend_logging_module()
    logger = cast("AppLoggerForTest", logging.getLogger(app_name))

    # Then registers things after (wrong order)
    mod_alogs.register_logger(app_name)
    mod_alogs.register_default_log_level("debug")
    mod_alogs.register_log_level_env_vars(["TESTAPP_LOG_LEVEL"])

    # --- verify ---
    # Logger should still work
    assert logger is not None
    assert logger.name == app_name

    # get_logger() should now work since we registered the name
    logger2 = mod_alogs.get_logger()
    assert logger2.name == app_name

    # determine_log_level should use registered defaults
    # (though the logger instance was created before registration)
    level = logger.determine_log_level()
    # Should use registered default if available, otherwise fallback
    assert level in ("DEBUG", "INFO")  # May depend on registration timing


def test_registering_after_get_logger_affects_new_instances(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that registering after getLogger() affects new logger instances."""
    # --- setup ---
    app_name = "testapp_late_register_new"

    # Create logger before registration
    AppLoggerForTest.extend_logging_module()
    # Create logger1 to test that it exists before registration
    _logger1 = cast("AppLoggerForTest", logging.getLogger(f"{app_name}_1"))

    # Register configuration
    mod_alogs.register_logger(app_name)
    mod_alogs.register_default_log_level("warning")
    monkeypatch.setenv("TESTAPP_LOG_LEVEL", "error")
    mod_alogs.register_log_level_env_vars(["TESTAPP_LOG_LEVEL"])

    # Create new logger after registration
    logger2 = cast("AppLoggerForTest", logging.getLogger(f"{app_name}_2"))

    # --- verify ---
    # New logger should use registered configuration
    level2 = logger2.determine_log_level()
    # Should check env var first
    assert level2 == "ERROR"
