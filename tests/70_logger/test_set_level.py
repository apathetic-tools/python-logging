# tests/50_core/test_set_level.py
"""Tests for Logger.setLevel() method with various level types."""

import logging
from typing import TYPE_CHECKING

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


def test_set_level_with_trace_string(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'TRACE' as a string."""
    # --- execute ---
    direct_logger.setLevel("TRACE")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.TRACE_LEVEL
    assert direct_logger.levelName == "TRACE"


def test_set_level_with_trace_lowercase(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'trace' (lowercase) as a string."""
    # --- execute ---
    direct_logger.setLevel("trace")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.TRACE_LEVEL
    assert direct_logger.levelName == "TRACE"


def test_set_level_with_silent_string(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'SILENT' as a string."""
    # --- execute ---
    direct_logger.setLevel("SILENT")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.SILENT_LEVEL
    assert direct_logger.levelName == "SILENT"


def test_set_level_with_detail_string(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'DETAIL' as a string."""
    # --- execute ---
    direct_logger.setLevel("DETAIL")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.DETAIL_LEVEL
    assert direct_logger.levelName == "DETAIL"


def test_set_level_with_detail_lowercase(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'detail' (lowercase) as a string."""
    # --- execute ---
    direct_logger.setLevel("detail")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.DETAIL_LEVEL
    assert direct_logger.levelName == "DETAIL"


def test_set_level_with_brief_string(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'BRIEF' as a string."""
    # --- execute ---
    direct_logger.setLevel("BRIEF")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.BRIEF_LEVEL
    assert direct_logger.levelName == "BRIEF"


def test_set_level_with_brief_lowercase(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'brief' (lowercase) as a string."""
    # --- execute ---
    direct_logger.setLevel("brief")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.BRIEF_LEVEL
    assert direct_logger.levelName == "BRIEF"


def test_set_level_with_silent_lowercase(
    direct_logger: Logger,
) -> None:
    """setLevel() should accept 'silent' (lowercase) as a string."""
    # --- execute ---
    direct_logger.setLevel("silent")

    # --- verify ---
    assert direct_logger.level == mod_alogs.apathetic_logging.SILENT_LEVEL
    assert direct_logger.levelName == "SILENT"


def test_set_level_with_standard_levels_string(
    direct_logger: Logger,
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
    direct_logger: Logger,
) -> None:
    """setLevel() should accept numeric level values."""
    # --- execute ---
    direct_logger.setLevel(logging.DEBUG)

    # --- verify ---
    assert direct_logger.level == logging.DEBUG


def test_set_level_case_insensitive(
    direct_logger: Logger,
) -> None:
    """setLevel() should be case-insensitive for level names."""
    # --- execute and verify ---
    direct_logger.setLevel("debug")
    assert direct_logger.level == logging.DEBUG

    direct_logger.setLevel("Debug")
    assert direct_logger.level == logging.DEBUG

    direct_logger.setLevel("DEBUG")
    assert direct_logger.level == logging.DEBUG
