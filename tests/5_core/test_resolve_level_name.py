# tests/5_core/test_resolve_level_name.py
"""Tests for Logger.resolve_level_name() method."""

import logging

import pytest

import apathetic_logging as mod_alogs


@pytest.mark.parametrize(
    ("level_name", "expected"),
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ],
)
def test_resolve_level_name_standard_levels(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
    level_name: str,
    expected: int,
) -> None:
    """resolve_level_name() should resolve standard logging level names."""
    # --- execute ---
    result = direct_logger.resolve_level_name(level_name)

    # --- verify ---
    assert result == expected


def test_resolve_level_name_case_insensitive(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """resolve_level_name() should handle case-insensitive level names."""
    # --- execute ---
    result_lower = direct_logger.resolve_level_name("debug")
    result_upper = direct_logger.resolve_level_name("DEBUG")
    result_mixed = direct_logger.resolve_level_name("Debug")

    # --- verify ---
    assert result_lower == logging.DEBUG
    assert result_upper == logging.DEBUG
    assert result_mixed == logging.DEBUG


def test_resolve_level_name_unknown_level(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """resolve_level_name() should return None for unknown level names."""
    # --- execute ---
    result = direct_logger.resolve_level_name("UNKNOWN_LEVEL")

    # --- verify ---
    assert result is None


def test_resolve_level_name_custom_levels_resolved(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """resolve_level_name() resolves TRACE/SILENT after extend_logging_module()."""
    # --- execute ---
    # extend_logging_module() is called at import time, so TRACE and SILENT
    # should be available in the logging module
    trace_result = direct_logger.resolve_level_name("TRACE")
    silent_result = direct_logger.resolve_level_name("SILENT")

    # --- verify ---
    # These custom levels are added to logging module by extend_logging_module()
    # So resolve_level_name should find them
    assert trace_result == mod_alogs.ApatheticLogging.TRACE_LEVEL
    assert silent_result == mod_alogs.ApatheticLogging.SILENT_LEVEL
