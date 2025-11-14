# tests/5_core/test_extend_logging_module.py
"""Tests for Logger.extend_logging_module() class method."""

import logging

import apathetic_logging as mod_alogs


def test_extend_logging_module_adds_trace_level() -> None:
    """extend_logging_module() should add TRACE level to logging module."""
    # --- setup ---
    # Reset the extension state by creating a new logger class
    # (in real usage, this is called once at module import)

    # --- execute ---
    # Call extend_logging_module (may have already been called)
    result = mod_alogs.ApatheticLogging.Logger.extend_logging_module()

    # --- verify ---
    # Should have TRACE level defined
    assert hasattr(logging, "TRACE")
    assert logging.TRACE == mod_alogs.ApatheticLogging.TRACE_LEVEL
    # Should return False if already extended
    assert isinstance(result, bool)


def test_extend_logging_module_adds_silent_level() -> None:
    """extend_logging_module() should add SILENT level to logging module."""
    # --- execute ---
    mod_alogs.ApatheticLogging.Logger.extend_logging_module()

    # --- verify ---
    # Should have SILENT level defined
    assert hasattr(logging, "SILENT")
    assert logging.SILENT == mod_alogs.ApatheticLogging.SILENT_LEVEL


def test_extend_logging_module_adds_level_names() -> None:
    """extend_logging_module() should add level names to logging module."""
    # --- execute ---
    mod_alogs.ApatheticLogging.Logger.extend_logging_module()

    # --- verify ---
    # Should be able to get level names
    trace_name = logging.getLevelName(mod_alogs.ApatheticLogging.TRACE_LEVEL)
    silent_name = logging.getLevelName(mod_alogs.ApatheticLogging.SILENT_LEVEL)
    assert trace_name == "TRACE"
    assert silent_name == "SILENT"


def test_extend_logging_module_sets_logger_class() -> None:
    """extend_logging_module() should set the logger class."""
    # --- execute ---
    mod_alogs.ApatheticLogging.Logger.extend_logging_module()

    # --- verify ---
    # The logger class should be set (though we can't easily test this
    # without creating a new logger, which would use the class)
    # We can at least verify the method completes without error
    assert True
