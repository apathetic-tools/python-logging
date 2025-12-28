# tests/30_independant/test_log_root_dynamic.py
"""Tests for logRootDynamic function."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    import pytest


def test_log_root_dynamic_with_string_level(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test logRootDynamic with string level."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG")

    with caplog.at_level(logging.DEBUG):
        mod_alogs.logRootDynamic("INFO", "Test message with %s", "arg")

    # --- verify ---
    assert "Test message with arg" in caplog.text

    # --- cleanup ---
    root.setLevel(original_level)


def test_log_root_dynamic_with_int_level(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test logRootDynamic with integer level."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG")

    with caplog.at_level(logging.DEBUG):
        mod_alogs.logRootDynamic(logging.WARNING, "Test warning message")

    # --- verify ---
    assert "Test warning message" in caplog.text

    # --- cleanup ---
    root.setLevel(original_level)


def test_log_root_dynamic_respects_log_level() -> None:
    """Test logRootDynamic respects current log level."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    # Test that function works without errors
    mod_alogs.setRootLevel("WARNING")

    # These calls should not raise exceptions
    mod_alogs.logRootDynamic("DEBUG", "Debug message")
    mod_alogs.logRootDynamic("WARNING", "Warning message")
    mod_alogs.logRootDynamic(logging.ERROR, "Error message")

    # --- cleanup ---
    root.setLevel(original_level)
