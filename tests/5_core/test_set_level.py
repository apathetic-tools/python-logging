# tests/5_core/test_set_level.py
"""Tests for Logger.setLevel() method with various level types."""

import logging

import apathetic_logging as mod_alogs


def test_set_level_with_trace_string(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """setLevel() should accept 'TRACE' as a string."""
    # --- execute ---
    direct_logger.setLevel("TRACE")

    # --- verify ---
    assert direct_logger.level == mod_alogs.ApatheticLogging.TRACE_LEVEL
    assert direct_logger.level_name == "TRACE"


def test_set_level_with_trace_lowercase(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """setLevel() should accept 'trace' (lowercase) as a string."""
    # --- execute ---
    direct_logger.setLevel("trace")

    # --- verify ---
    assert direct_logger.level == mod_alogs.ApatheticLogging.TRACE_LEVEL
    assert direct_logger.level_name == "TRACE"


def test_set_level_with_silent_string(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """setLevel() should accept 'SILENT' as a string."""
    # --- execute ---
    direct_logger.setLevel("SILENT")

    # --- verify ---
    assert direct_logger.level == mod_alogs.ApatheticLogging.SILENT_LEVEL
    assert direct_logger.level_name == "SILENT"


def test_set_level_with_silent_lowercase(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """setLevel() should accept 'silent' (lowercase) as a string."""
    # --- execute ---
    direct_logger.setLevel("silent")

    # --- verify ---
    assert direct_logger.level == mod_alogs.ApatheticLogging.SILENT_LEVEL
    assert direct_logger.level_name == "SILENT"


def test_set_level_with_standard_levels_string(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """setLevel() should accept standard level names as strings."""
    # --- execute and verify ---
    direct_logger.setLevel("DEBUG")
    assert direct_logger.level == logging.DEBUG

    direct_logger.setLevel("INFO")
    assert direct_logger.level == logging.INFO

    direct_logger.setLevel("WARNING")
    assert direct_logger.level == logging.WARNING

    direct_logger.setLevel("ERROR")
    assert direct_logger.level == logging.ERROR

    direct_logger.setLevel("CRITICAL")
    assert direct_logger.level == logging.CRITICAL


def test_set_level_with_numeric_level(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """setLevel() should accept numeric level values."""
    # --- execute ---
    direct_logger.setLevel(logging.DEBUG)

    # --- verify ---
    assert direct_logger.level == logging.DEBUG


def test_set_level_case_insensitive(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """setLevel() should be case-insensitive for level names."""
    # --- execute and verify ---
    direct_logger.setLevel("debug")
    assert direct_logger.level == logging.DEBUG

    direct_logger.setLevel("Debug")
    assert direct_logger.level == logging.DEBUG

    direct_logger.setLevel("DEBUG")
    assert direct_logger.level == logging.DEBUG
