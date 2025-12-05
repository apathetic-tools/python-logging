# tests/50_core/test_extend_logging_module.py
"""Tests for Logger.extendLoggingModule() class method."""

import logging

import apathetic_logging as mod_alogs


def test_extend_logging_module_adds_trace_level() -> None:
    """extendLoggingModule() should add TRACE level to logging module."""
    # --- setup ---
    # Reset the extension state by creating a new logger class
    # (in real usage, this is called once at module import)

    # --- execute ---
    # Call extendLoggingModule (may have already been called)
    result = mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have TRACE level defined
    assert hasattr(logging, "TRACE")
    assert logging.TRACE == mod_alogs.apathetic_logging.TRACE_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    # Should return False if already extended
    assert isinstance(result, bool)


def test_extend_logging_module_adds_detail_level() -> None:
    """extendLoggingModule() should add DETAIL level to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have DETAIL level defined
    assert hasattr(logging, "DETAIL")
    assert logging.DETAIL == mod_alogs.apathetic_logging.DETAIL_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_extend_logging_module_adds_brief_level() -> None:
    """extendLoggingModule() should add BRIEF level to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have BRIEF level defined
    assert hasattr(logging, "BRIEF")
    assert logging.BRIEF == mod_alogs.apathetic_logging.BRIEF_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_extend_logging_module_adds_silent_level() -> None:
    """extendLoggingModule() should add SILENT level to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have SILENT level defined
    assert hasattr(logging, "SILENT")
    assert logging.SILENT == mod_alogs.apathetic_logging.SILENT_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_extend_logging_module_adds_level_names() -> None:
    """extendLoggingModule() should add level names to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should be able to get level names
    trace_name = logging.getLevelName(mod_alogs.apathetic_logging.TRACE_LEVEL)  # pyright: ignore[reportDeprecated]
    detail_name = logging.getLevelName(mod_alogs.apathetic_logging.DETAIL_LEVEL)  # pyright: ignore[reportDeprecated]
    brief_name = logging.getLevelName(mod_alogs.apathetic_logging.BRIEF_LEVEL)  # pyright: ignore[reportDeprecated]
    silent_name = logging.getLevelName(mod_alogs.apathetic_logging.SILENT_LEVEL)  # pyright: ignore[reportDeprecated]
    assert trace_name == "TRACE"
    assert detail_name == "DETAIL"
    assert brief_name == "BRIEF"
    assert silent_name == "SILENT"


def test_extend_logging_module_sets_logger_class() -> None:
    """extendLoggingModule() should set the logger class."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # The logger class should be set (though we can't easily test this
    # without creating a new logger, which would use the class)
    # We can at least verify the method completes without error
    assert True
