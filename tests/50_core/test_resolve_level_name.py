# tests/50_core/test_resolve_level_name.py
"""Tests for Logger.resolve_level_name() method."""

import logging
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


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
    direct_logger: Logger,
    level_name: str,
    expected: int,
) -> None:
    """resolve_level_name() should resolve standard logging level names."""
    # --- execute ---
    result = direct_logger.resolveLevelName(level_name)

    # --- verify ---
    assert result == expected


def test_resolve_level_name_case_insensitive(
    direct_logger: Logger,
) -> None:
    """resolve_level_name() should handle case-insensitive level names."""
    # --- execute ---
    result_lower = direct_logger.resolveLevelName("debug")
    result_upper = direct_logger.resolveLevelName("DEBUG")
    result_mixed = direct_logger.resolveLevelName("Debug")

    # --- verify ---
    assert result_lower == logging.DEBUG
    assert result_upper == logging.DEBUG
    assert result_mixed == logging.DEBUG


def test_resolve_level_name_unknown_level(
    direct_logger: Logger,
) -> None:
    """resolve_level_name() should return None for unknown level names."""
    # --- execute ---
    result = direct_logger.resolveLevelName("UNKNOWN_LEVEL")

    # --- verify ---
    assert result is None


def test_resolve_level_name_custom_levels_resolved(
    direct_logger: Logger,
) -> None:
    """resolve_level_name() resolves TRACE/DETAIL/MINIMAL/SILENT after extend.

    After extend_logging_module() is called, these custom levels should be
    resolvable.
    """
    # --- execute ---
    # extend_logging_module() is called at import time, so TRACE, DETAIL, MINIMAL,
    # and SILENT should be available in the logging module
    trace_result = direct_logger.resolveLevelName("TRACE")
    detail_result = direct_logger.resolveLevelName("DETAIL")
    minimal_result = direct_logger.resolveLevelName("MINIMAL")
    silent_result = direct_logger.resolveLevelName("SILENT")

    # --- verify ---
    # These custom levels are added to logging module by extend_logging_module()
    # So resolve_level_name should find them
    assert trace_result == mod_alogs.apathetic_logging.TRACE_LEVEL
    assert detail_result == mod_alogs.apathetic_logging.DETAIL_LEVEL
    assert minimal_result == mod_alogs.apathetic_logging.MINIMAL_LEVEL
    assert silent_result == mod_alogs.apathetic_logging.SILENT_LEVEL
