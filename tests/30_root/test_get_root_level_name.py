# tests/30_independant/test_get_root_level_name.py
"""Tests for getRootLevelName function."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_get_root_level_name_returns_string() -> None:
    """Test that getRootLevelName returns string."""
    root = logging.getLogger("")
    original_level = root.level

    mod_alogs.setRootLevel("DEBUG")

    name = mod_alogs.getRootLevelName()
    assert isinstance(name, str)
    assert name == "DEBUG"

    root.setLevel(original_level)


def test_get_root_level_name_with_different_levels() -> None:
    """Test getRootLevelName with various level values."""
    root = logging.getLogger("")
    original_level = root.level

    test_levels = [
        ("DEBUG", "DEBUG"),
        ("INFO", "INFO"),
        ("WARNING", "WARNING"),
        ("ERROR", "ERROR"),
        ("CRITICAL", "CRITICAL"),
    ]

    for level_name, expected_name in test_levels:
        mod_alogs.setRootLevel(level_name)
        assert mod_alogs.getRootLevelName() == expected_name

    root.setLevel(original_level)
