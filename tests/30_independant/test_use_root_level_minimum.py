# tests/30_independant/test_use_root_level_minimum.py
"""Tests for useRootLevelMinimum context manager."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_use_root_level_minimum_convenience_method() -> None:
    """Test that useRootLevelMinimum is equivalent to useRootLevel with minimum=True."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    # Should not downgrade from INFO to WARNING
    with mod_alogs.useRootLevelMinimum("WARNING"):
        # --- verify ---
        assert mod_alogs.getRootLevel() == logging.INFO

    # Should upgrade from INFO to DEBUG
    with mod_alogs.useRootLevelMinimum("DEBUG"):
        # --- verify ---
        assert mod_alogs.getRootLevel() == logging.DEBUG

    # --- cleanup ---
    root.setLevel(original_level)


def test_use_root_level_minimum_restores_on_exception() -> None:
    """Test that useRootLevelMinimum restores level even on exception."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    test_exception = ValueError("Test exception")
    try:
        with mod_alogs.useRootLevelMinimum("DEBUG"):
            assert mod_alogs.getRootLevel() == logging.DEBUG
            raise test_exception
    except ValueError:
        pass

    # --- verify ---
    # Should be restored even after exception
    assert mod_alogs.getRootLevel() == logging.INFO

    # --- cleanup ---
    root.setLevel(original_level)
