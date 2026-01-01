# tests/30_independant/test_set_root_level_minimum.py
"""Tests for setRootLevelMinimum function."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_set_root_level_minimum_upgrades_to_more_verbose() -> None:
    """Test that setRootLevelMinimum upgrades to more verbose level."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")
    mod_alogs.setRootLevelMinimum("DEBUG")

    # --- verify ---
    # Should upgrade from INFO to DEBUG (more verbose)
    assert mod_alogs.getRootLevel() == logging.DEBUG

    # --- cleanup ---
    root.setLevel(original_level)


def test_set_root_level_minimum_does_not_downgrade() -> None:
    """Test that setRootLevelMinimum does not downgrade to less verbose."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG")
    mod_alogs.setRootLevelMinimum("INFO")

    # --- verify ---
    # Should not downgrade from DEBUG to INFO (less verbose)
    assert mod_alogs.getRootLevel() == logging.DEBUG

    # --- cleanup ---
    root.setLevel(original_level)


def test_set_root_level_minimum_with_custom_levels() -> None:
    """Test setRootLevelMinimum with custom levels."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    _constants = mod_alogs.apathetic_logging

    # --- execute ---
    mod_alogs.setRootLevel("TRACE")
    mod_alogs.setRootLevelMinimum("DEBUG")

    # --- verify ---
    # TRACE is more verbose than DEBUG, so should not change
    assert mod_alogs.getRootLevel() == _constants.TRACE_LEVEL

    # --- cleanup ---
    root.setLevel(original_level)
