# tests/90_integration/test_extendLoggingModule_integration.py
"""Integration tests for extendLoggingModule() and get_logger()."""

import logging

import apathetic_logging as mod_alogs


def test_extendLoggingModule_called_twice_is_safe() -> None:
    """Calling extendLoggingModule() twice should be safe and idempotent."""
    # --- setup ---
    # First call (may have already been called at import)
    mod_alogs.Logger.extendLoggingModule()

    # --- execute ---
    # Second call
    result2 = mod_alogs.Logger.extendLoggingModule()

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


def test_extendLoggingModule_before_get_logger_works() -> None:
    """extendLoggingModule() should work when called before get_logger()."""
    # --- setup ---
    mod_alogs.registerLogger("test_integration")

    # --- execute ---
    # extendLoggingModule() is already called at import, but we can verify
    # that get_logger() works correctly
    logger = mod_alogs.getLogger()

    # --- verify ---
    assert logger is not None
    assert logger.name == "test_integration"
    # Logger should be able to use TRACE, DETAIL, MINIMAL, and SILENT levels
    logger.setLevel("TRACE")
    assert logger.levelName == "TRACE"
    logger.setLevel("DETAIL")
    assert logger.levelName == "DETAIL"
    logger.setLevel("MINIMAL")
    assert logger.levelName == "MINIMAL"
    logger.setLevel("SILENT")
    assert logger.levelName == "SILENT"


def test_get_logger_works_after_extendLoggingModule() -> None:
    """get_logger() should work correctly after extendLoggingModule() is called."""
    # --- setup ---
    mod_alogs.registerLogger("test_get_logger_after_extend")

    # --- execute ---
    logger = mod_alogs.getLogger()

    # --- verify ---
    assert logger is not None

    # this can be very brittle, use debug_logger_summary to figure out what class to use
    assert isinstance(logger, mod_alogs.apathetic_logging.Logger)

    # fallback assertions
    assert hasattr(logger, "trace")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determineLogLevel")
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
    """Logger should be able to use TRACE level after extendLoggingModule()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_trace_logger")
    logger.setLevel("TRACE")

    # --- verify ---
    # Should be able to call trace() method
    assert hasattr(logger, "trace")
    assert callable(logger.trace)


def test_logger_can_use_detail_level_after_extend() -> None:
    """Logger should be able to use DETAIL level after extendLoggingModule()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_detail_logger")
    logger.setLevel("DETAIL")

    # --- verify ---
    # Should be able to call detail() method
    assert hasattr(logger, "detail")
    assert callable(logger.detail)
    assert logger.levelName == "DETAIL"


def test_logger_can_use_minimal_level_after_extend() -> None:
    """Logger should be able to use MINIMAL level after extendLoggingModule()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_minimal_logger")
    logger.setLevel("MINIMAL")

    # --- verify ---
    # Should be able to call minimal() method
    assert hasattr(logger, "minimal")
    assert callable(logger.minimal)
    assert logger.levelName == "MINIMAL"


def test_logger_can_use_silent_level_after_extend() -> None:
    """Logger should be able to use SILENT level after extendLoggingModule()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_silent_logger")

    # --- execute ---
    logger.setLevel("SILENT")

    # --- verify ---
    assert logger.level == mod_alogs.apathetic_logging.SILENT_LEVEL
    assert logger.levelName == "SILENT"


def test_extendLoggingModule_sets_logger_class() -> None:
    """extendLoggingModule() should set the logger class for logging.getLogger()."""
    # --- setup ---
    mod_alogs.registerLogger("test_logger_class")

    # --- execute ---
    # get_logger() uses logging.getLogger() internally
    logger = mod_alogs.getLogger()

    # --- verify ---
    # The logger should be an instance of apathetic_logging.Logger
    # (or at least compatible with it)
    assert logger is not None
    # Should have apathetic logging methods
    assert hasattr(logger, "trace")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determineLogLevel")


def test_multiple_calls_to_extendLoggingModule() -> None:
    """Multiple calls to extendLoggingModule() should not cause issues."""
    # --- execute ---
    results: list[bool] = []
    for _ in range(5):
        result = mod_alogs.Logger.extendLoggingModule()
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


def test_extendLoggingModule_preserves_existing_loggers() -> None:
    """extendLoggingModule() should not break existing loggers."""
    # --- setup ---
    # Create a logger before calling extend (though it's already called at import)
    existing_logger = mod_alogs.Logger("existing_logger")
    existing_logger.setLevel("INFO")

    # --- execute ---
    # Call extend again (should be safe)
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Existing logger should still work
    assert existing_logger.levelName == "INFO"
    # Should be able to change to custom levels
    existing_logger.setLevel("TRACE")
    assert existing_logger.levelName == "TRACE"
    existing_logger.setLevel("SILENT")
    assert existing_logger.levelName == "SILENT"


def test_full_integration_flow() -> None:
    """Test the full integration flow: extend → register → get_logger → use."""
    # --- setup ---
    # This simulates the typical usage pattern

    # --- execute ---
    # 1. extendLoggingModule() is called at import (already done)
    # 2. Register logger name
    mod_alogs.registerLogger("integration_test")

    # 3. Get logger
    logger = mod_alogs.getLogger()

    # 4. Use logger with custom levels
    logger.setLevel("TRACE")
    logger.trace("trace message")
    logger.setLevel("SILENT")
    # At SILENT level, nothing should log
    logger.debug("should not appear")

    # --- verify ---
    assert logger.name == "integration_test"
    assert logger.levelName == "SILENT"
    # Logger should have all expected methods
    assert hasattr(logger, "trace")
    assert hasattr(logger, "errorIfNotDebug")
    assert hasattr(logger, "criticalIfNotDebug")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determineLogLevel")


def test_get_logger_requires_extendLoggingModule() -> None:
    """get_logger() should work even if extendLoggingModule() was called at import.

    Note: In practice, extendLoggingModule() is always called at import time
    in __init__.py. This test verifies that the integration works correctly.
    """
    # --- setup ---
    # extendLoggingModule() is already called at import time
    # Verify that get_logger() works correctly
    mod_alogs.registerLogger("test_requires_extend")

    # --- execute ---
    logger = mod_alogs.getLogger()

    # --- verify ---
    # Logger should work correctly with custom levels
    assert logger is not None
    # Should be able to use TRACE and SILENT
    logger.setLevel("TRACE")
    assert logger.levelName == "TRACE"
    logger.setLevel("SILENT")
    assert logger.levelName == "SILENT"
    # Should have custom methods
    assert hasattr(logger, "trace")


def test_extendLoggingModule_idempotent_behavior() -> None:
    """extendLoggingModule() should be idempotent - safe to call multiple times."""
    # --- setup ---
    # Get initial state
    initial_trace = getattr(logging, "TRACE", None)
    initial_silent = getattr(logging, "SILENT", None)

    # --- execute ---
    # Call multiple times
    mod_alogs.Logger.extendLoggingModule()
    result2 = mod_alogs.Logger.extendLoggingModule()
    result3 = mod_alogs.Logger.extendLoggingModule()

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
     after extendLoggingModule().

    This verifies that extendLoggingModule() sets the logger class correctly,
    so that logging.getLogger() returns the right type.
    """
    # --- setup ---
    # extendLoggingModule() is called at import time, which sets
    # logging.setLoggerClass(apathetic_logging.Logger)
    mod_alogs.registerLogger("test_logger_type")

    # --- execute ---
    logger = mod_alogs.getLogger()

    # --- verify ---
    # Logger should have apathetic_logging.Logger methods
    assert hasattr(logger, "trace")
    assert hasattr(logger, "colorize")
    assert hasattr(logger, "determineLogLevel")
    assert hasattr(logger, "errorIfNotDebug")
    assert hasattr(logger, "criticalIfNotDebug")
    # Should be able to use custom levels
    logger.setLevel("TRACE")
    assert logger.levelName == "TRACE"
    logger.setLevel("SILENT")
    assert logger.levelName == "SILENT"
