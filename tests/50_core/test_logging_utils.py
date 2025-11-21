# tests/50_core/test_logging_utils.py
"""Tests for logging utility functions (getLevelName, getLevelNumber)."""

import logging

import pytest

import apathetic_logging as mod_alogs
from tests.utils.level_validation import validate_test_level


# Safe test level value (999 is well above any standard or custom level)
UNKNOWN_LEVEL = 999
validate_test_level(UNKNOWN_LEVEL)


# ---------------------------------------------------------------------------
# Tests for getLevelName()
# ---------------------------------------------------------------------------


def test_get_level_name_known_level() -> None:
    """getLevelName() should return known level names."""
    assert mod_alogs.getLevelName(logging.DEBUG) == "DEBUG"
    assert mod_alogs.getLevelName(logging.INFO) == "INFO"
    assert mod_alogs.getLevelName(logging.WARNING) == "WARNING"
    assert mod_alogs.getLevelName(logging.ERROR) == "ERROR"
    assert mod_alogs.getLevelName(logging.CRITICAL) == "CRITICAL"


def test_get_level_name_custom_levels() -> None:
    """getLevelName() should return custom apathetic level names."""
    assert mod_alogs.getLevelName(mod_alogs.TEST_LEVEL) == "TEST"
    assert mod_alogs.getLevelName(mod_alogs.TRACE_LEVEL) == "TRACE"
    assert mod_alogs.getLevelName(mod_alogs.DETAIL_LEVEL) == "DETAIL"
    assert mod_alogs.getLevelName(mod_alogs.MINIMAL_LEVEL) == "MINIMAL"
    assert mod_alogs.getLevelName(mod_alogs.SILENT_LEVEL) == "SILENT"


def test_get_level_name_string_input() -> None:
    """getLevelName() should return uppercased string for string input."""
    assert mod_alogs.getLevelName("DEBUG") == "DEBUG"
    assert mod_alogs.getLevelName("debug") == "DEBUG"
    assert mod_alogs.getLevelName("Info") == "INFO"
    assert mod_alogs.getLevelName("trace") == "TRACE"


def test_get_level_name_unknown_level_lenient() -> None:
    """getLevelName() should return 'Level {level}' format for unknown levels."""
    # Default behavior (strict=False) should return stdlib format
    result = mod_alogs.getLevelName(UNKNOWN_LEVEL)
    assert result == f"Level {UNKNOWN_LEVEL}"
    # Should match stdlib behavior
    assert result == logging.getLevelName(UNKNOWN_LEVEL)


def test_get_level_name_unknown_level_strict() -> None:
    """getLevelName() should raise ValueError for unknown levels when strict=True."""
    with pytest.raises(ValueError, match=r"Unknown log level: 999"):
        mod_alogs.getLevelName(UNKNOWN_LEVEL, strict=True)


def test_get_level_name_unknown_level_strict_string() -> None:
    """getLevelName() should not raise for string input even in strict mode."""
    # String input is always returned uppercased, even in strict mode
    assert mod_alogs.getLevelName("UNKNOWN", strict=True) == "UNKNOWN"
    assert mod_alogs.getLevelName("custom", strict=True) == "CUSTOM"


# ---------------------------------------------------------------------------
# Tests for getLevelNumber()
# ---------------------------------------------------------------------------


def test_get_level_number_known_levels() -> None:
    """getLevelNumber() should return correct integers for known level names."""
    assert mod_alogs.getLevelNumber("DEBUG") == logging.DEBUG
    assert mod_alogs.getLevelNumber("INFO") == logging.INFO
    assert mod_alogs.getLevelNumber("WARNING") == logging.WARNING
    assert mod_alogs.getLevelNumber("ERROR") == logging.ERROR
    assert mod_alogs.getLevelNumber("CRITICAL") == logging.CRITICAL


def test_get_level_number_case_insensitive() -> None:
    """getLevelNumber() should be case-insensitive."""
    assert mod_alogs.getLevelNumber("debug") == logging.DEBUG
    assert mod_alogs.getLevelNumber("Debug") == logging.DEBUG
    assert mod_alogs.getLevelNumber("DEBUG") == logging.DEBUG
    assert mod_alogs.getLevelNumber("info") == logging.INFO
    assert mod_alogs.getLevelNumber("Info") == logging.INFO


def test_get_level_number_custom_levels() -> None:
    """getLevelNumber() should return correct integers for custom apathetic levels."""
    assert mod_alogs.getLevelNumber("TEST") == mod_alogs.TEST_LEVEL
    assert mod_alogs.getLevelNumber("TRACE") == mod_alogs.TRACE_LEVEL
    assert mod_alogs.getLevelNumber("DETAIL") == mod_alogs.DETAIL_LEVEL
    assert mod_alogs.getLevelNumber("MINIMAL") == mod_alogs.MINIMAL_LEVEL
    assert mod_alogs.getLevelNumber("SILENT") == mod_alogs.SILENT_LEVEL


def test_get_level_number_integer_input() -> None:
    """getLevelNumber() should return integer as-is for integer input."""
    assert mod_alogs.getLevelNumber(logging.DEBUG) == logging.DEBUG
    assert mod_alogs.getLevelNumber(logging.INFO) == logging.INFO
    assert mod_alogs.getLevelNumber(UNKNOWN_LEVEL) == UNKNOWN_LEVEL


def test_get_level_number_unknown_level_raises() -> None:
    """getLevelNumber() should raise ValueError for unknown level names."""
    with pytest.raises(ValueError, match=r"Unknown log level: 'UNKNOWN'"):
        mod_alogs.getLevelNumber("UNKNOWN")

    with pytest.raises(ValueError, match=r"Unknown log level: 'INVALID'"):
        mod_alogs.getLevelNumber("INVALID")


# ---------------------------------------------------------------------------
# Tests for snake_case wrappers
# ---------------------------------------------------------------------------


def test_get_level_name_snake_case() -> None:
    """get_level_name() should work the same as getLevelName()."""
    assert mod_alogs.get_level_name(logging.DEBUG) == "DEBUG"
    assert mod_alogs.get_level_name(UNKNOWN_LEVEL) == f"Level {UNKNOWN_LEVEL}"
    with pytest.raises(ValueError, match=r"Unknown log level: 999"):
        mod_alogs.get_level_name(UNKNOWN_LEVEL, strict=True)


def test_get_level_number_snake_case() -> None:
    """get_level_number() should work the same as getLevelNumber()."""
    assert mod_alogs.get_level_number("DEBUG") == logging.DEBUG
    assert mod_alogs.get_level_number(logging.INFO) == logging.INFO
    with pytest.raises(ValueError, match=r"Unknown log level: 'UNKNOWN'"):
        mod_alogs.get_level_number("UNKNOWN")
