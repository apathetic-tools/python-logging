# tests/30_independant/test_get_root_level.py
"""Tests for getRootLevel function."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_get_root_level_returns_int() -> None:
    """Test that getRootLevel returns integer."""
    root = logging.getLogger("")
    original_level = root.level

    mod_alogs.setRootLevel("DEBUG")

    level = mod_alogs.getRootLevel()
    assert isinstance(level, int)
    assert level == logging.DEBUG

    root.setLevel(original_level)


def test_get_root_level_with_different_levels() -> None:
    """Test getRootLevel with various level values."""
    root = logging.getLogger("")
    original_level = root.level

    test_levels = [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ]

    for level_name, level_int in test_levels:
        mod_alogs.setRootLevel(level_name)
        assert mod_alogs.getRootLevel() == level_int

    root.setLevel(original_level)
