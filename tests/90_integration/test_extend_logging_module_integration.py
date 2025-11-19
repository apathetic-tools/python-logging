# tests/90_integration/test_extend_logging_module_integration.py
"""Integration tests for extend_logging_module() and get_logger()."""

import logging
from collections.abc import Generator

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


@pytest.fixture(autouse=True)
def reset_registry() -> Generator[None, None, None]:
    """Reset registry state and logger class before and after each test."""
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _logging_utils = mod_alogs.apathetic_logging
    original_name = _registry.registered_internal_logger_name
    original_logger_class = logging.getLoggerClass()
    _registry.registered_internal_logger_name = None
    # Clear any existing loggers from the registry
    logger_names = list(logging.Logger.manager.loggerDict.keys())
    for logger_name in logger_names:
        _logging_utils.remove_logger(logger_name)
    # Reset logger class to default before test (may have been changed by other tests)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extend_logging_module()
    yield
    _registry.registered_internal_logger_name = original_name
    # Reset logger class to original after test
    logging.setLoggerClass(original_logger_class)
    # Re-extend with the default Logger class to ensure it's set correctly
    mod_alogs.Logger.extend_logging_module()


def test_extend_logging_module_called_twice_is_safe() -> None:
    """Calling extend_logging_module() twice should be safe and idempotent."""
    # --- setup ---
    # First call (may have already been called at import)
    mod_alogs.Logger.extend_logging_module()

    # --- execute ---
    # Second call
    result2 = mod_alogs.Logger.extend_logging_module()

    # --- verify ---
    # Second call should return False (already extended)
    assert result2 is False
    # TRACE, DETAIL, MINIMAL, and SILENT should still be available
    assert hasattr(logging, "TRACE")
    assert hasattr(logging, "DETAIL")
    assert hasattr(logging, "MINIMAL")
    assert hasattr(logging, "SILENT")
    assert logging.TRACE == mod_alogs.apathetic_logging.TRACE_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    assert logging.DETAIL == mod_alogs.apathetic_logging.DETAIL_LEVEL  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    assert logging.MINIMAL == mod_alogs.apathetic_logging.MINIMAL_LEVEL  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    assert logging.SILENT == mod_alogs.apathetic_logging.SILENT_LEVEL  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_extend_logging_module_before_get_logger_works() -> None:
    """extend_logging_module() should work when called before get_logger()."""
    # --- setup ---
    mod_alogs.register_logger_name("test_integration")

    # --- execute ---
    # extend_logging_module() is already called at import, but we can verify
    # that get_logger() works correctly
    logger = mod_alogs.get_logger()

    # --- verify ---
    assert logger is not None
    assert logger.name == "test_integration"
    # Logger should be able to use TRACE, DETAIL, MINIMAL, and SILENT levels
    logger.setLevel("TRACE")
    assert logger.level_name == "TRACE"
    logger.setLevel("DETAIL")
    assert logger.level_name == "DETAIL"
    logger.setLevel("MINIMAL")
    assert logger.level_name == "MINIMAL"
    logger.setLevel("SILENT")
    assert logger.level_name == "SILENT"


def test_get_logger_works_after_extend_logging_module() -> None:
    """get_logger() should work correctly after extend_logging_module() is called."""
    # --- setup ---
    mod_alogs.register_logger_name("test_get_logger_after_extend")

    # --- execute ---
    logger = mod_alogs.get_logger()

    # --- verify ---
    assert logger is not None
    # Check that logger has expected apathetic_logging.Logger methods/behavior
    # (instead of isinstance check which may fail in singlefile mode due to class
    # reference differences)
    assert hasattr(logger, "trace")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determine_log_level")
    # Should be able to use custom levels
    logger.setLevel(logging.TRACE)  # type: ignore[attr-defined]
    assert logger.level == mod_alogs.apathetic_logging.TRACE_LEVEL
    logger.setLevel(logging.DETAIL)  # type: ignore[attr-defined]
    assert logger.level == mod_alogs.apathetic_logging.DETAIL_LEVEL
    logger.setLevel(logging.MINIMAL)  # type: ignore[attr-defined]
    assert logger.level == mod_alogs.apathetic_logging.MINIMAL_LEVEL
    logger.setLevel(logging.SILENT)  # type: ignore[attr-defined]
    assert logger.level == mod_alogs.apathetic_logging.SILENT_LEVEL


def test_logger_can_use_trace_level_after_extend() -> None:
    """Logger should be able to use TRACE level after extend_logging_module()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_trace_logger")
    logger.setLevel("TRACE")

    # --- verify ---
    # Should be able to call trace() method
    assert hasattr(logger, "trace")
    assert callable(logger.trace)


def test_logger_can_use_detail_level_after_extend() -> None:
    """Logger should be able to use DETAIL level after extend_logging_module()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_detail_logger")
    logger.setLevel("DETAIL")

    # --- verify ---
    # Should be able to call detail() method
    assert hasattr(logger, "detail")
    assert callable(logger.detail)
    assert logger.level_name == "DETAIL"


def test_logger_can_use_minimal_level_after_extend() -> None:
    """Logger should be able to use MINIMAL level after extend_logging_module()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_minimal_logger")
    logger.setLevel("MINIMAL")

    # --- verify ---
    # Should be able to call minimal() method
    assert hasattr(logger, "minimal")
    assert callable(logger.minimal)
    assert logger.level_name == "MINIMAL"


def test_logger_can_use_silent_level_after_extend() -> None:
    """Logger should be able to use SILENT level after extend_logging_module()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_silent_logger")

    # --- execute ---
    logger.setLevel("SILENT")

    # --- verify ---
    assert logger.level == mod_alogs.apathetic_logging.SILENT_LEVEL
    assert logger.level_name == "SILENT"


def test_extend_logging_module_sets_logger_class() -> None:
    """extend_logging_module() should set the logger class for logging.getLogger()."""
    # --- setup ---
    mod_alogs.register_logger_name("test_logger_class")

    # --- execute ---
    # get_logger() uses logging.getLogger() internally
    logger = mod_alogs.get_logger()

    # --- verify ---
    # The logger should be an instance of apathetic_logging.Logger
    # (or at least compatible with it)
    assert logger is not None
    # Should have apathetic logging methods
    assert hasattr(logger, "trace")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determine_log_level")


def test_multiple_calls_to_extend_logging_module() -> None:
    """Multiple calls to extend_logging_module() should not cause issues."""
    # --- execute ---
    results: list[bool] = []
    for _ in range(5):
        result = mod_alogs.Logger.extend_logging_module()
        results.append(result)

    # --- verify ---
    # First call should return True (or False if already called at import)
    # Subsequent calls should all return False
    assert all(r is False for r in results[1:])  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
    # TRACE, DETAIL, MINIMAL, and SILENT should still be available
    assert hasattr(logging, "TRACE")
    assert hasattr(logging, "DETAIL")
    assert hasattr(logging, "MINIMAL")
    assert hasattr(logging, "SILENT")


def test_extend_logging_module_preserves_existing_loggers() -> None:
    """extend_logging_module() should not break existing loggers."""
    # --- setup ---
    # Create a logger before calling extend (though it's already called at import)
    existing_logger = mod_alogs.Logger("existing_logger")
    existing_logger.setLevel("INFO")

    # --- execute ---
    # Call extend again (should be safe)
    mod_alogs.Logger.extend_logging_module()

    # --- verify ---
    # Existing logger should still work
    assert existing_logger.level_name == "INFO"
    # Should be able to change to custom levels
    existing_logger.setLevel("TRACE")
    assert existing_logger.level_name == "TRACE"
    existing_logger.setLevel("SILENT")
    assert existing_logger.level_name == "SILENT"


def test_full_integration_flow() -> None:
    """Test the full integration flow: extend → register → get_logger → use."""
    # --- setup ---
    # This simulates the typical usage pattern

    # --- execute ---
    # 1. extend_logging_module() is called at import (already done)
    # 2. Register logger name
    mod_alogs.register_logger_name("integration_test")

    # 3. Get logger
    logger = mod_alogs.get_logger()

    # 4. Use logger with custom levels
    logger.setLevel("TRACE")
    logger.trace("trace message")
    logger.setLevel("SILENT")
    # At SILENT level, nothing should log
    logger.debug("should not appear")

    # --- verify ---
    assert logger.name == "integration_test"
    assert logger.level_name == "SILENT"
    # Logger should have all expected methods
    assert hasattr(logger, "trace")
    assert hasattr(logger, "error_if_not_debug")
    assert hasattr(logger, "critical_if_not_debug")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determine_log_level")


def test_get_logger_requires_extend_logging_module() -> None:
    """get_logger() should work even if extend_logging_module() was called at import.

    Note: In practice, extend_logging_module() is always called at import time
    in __init__.py. This test verifies that the integration works correctly.
    """
    # --- setup ---
    # extend_logging_module() is already called at import time
    # Verify that get_logger() works correctly
    mod_alogs.register_logger_name("test_requires_extend")

    # --- execute ---
    logger = mod_alogs.get_logger()

    # --- verify ---
    # Logger should work correctly with custom levels
    assert logger is not None
    # Should be able to use TRACE and SILENT
    logger.setLevel("TRACE")
    assert logger.level_name == "TRACE"
    logger.setLevel("SILENT")
    assert logger.level_name == "SILENT"
    # Should have custom methods
    assert hasattr(logger, "trace")


def test_extend_logging_module_idempotent_behavior() -> None:
    """extend_logging_module() should be idempotent - safe to call multiple times."""
    # --- setup ---
    # Get initial state
    initial_trace = getattr(logging, "TRACE", None)
    initial_silent = getattr(logging, "SILENT", None)

    # --- execute ---
    # Call multiple times
    mod_alogs.Logger.extend_logging_module()
    result2 = mod_alogs.Logger.extend_logging_module()
    result3 = mod_alogs.Logger.extend_logging_module()

    # --- verify ---
    # All calls after the first should return False
    # (First may return False if already called at import)
    assert result2 is False
    assert result3 is False
    # TRACE and SILENT should still be set correctly
    assert hasattr(logging, "TRACE")
    assert hasattr(logging, "SILENT")
    assert logging.TRACE == mod_alogs.apathetic_logging.TRACE_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    assert logging.SILENT == mod_alogs.apathetic_logging.SILENT_LEVEL  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    # Values should not change
    if initial_trace is not None:
        assert initial_trace == logging.TRACE  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    if initial_silent is not None:
        assert initial_silent == logging.SILENT  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_get_logger_returns_apathetic_logger_after_extend() -> None:
    """get_logger() should return apathetic_logging.Logger
     after extend_logging_module().

    This verifies that extend_logging_module() sets the logger class correctly,
    so that logging.getLogger() returns the right type.
    """
    # --- setup ---
    # extend_logging_module() is called at import time, which sets
    # logging.setLoggerClass(apathetic_logging.Logger)
    mod_alogs.register_logger_name("test_logger_type")

    # --- execute ---
    logger = mod_alogs.get_logger()

    # --- verify ---
    # Logger should have apathetic_logging.Logger methods
    assert hasattr(logger, "trace")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determine_log_level")
    assert hasattr(logger, "error_if_not_debug")
    assert hasattr(logger, "critical_if_not_debug")
    # Should be able to use custom levels
    logger.setLevel("TRACE")
    assert logger.level_name == "TRACE"
    logger.setLevel("SILENT")
    assert logger.level_name == "SILENT"
