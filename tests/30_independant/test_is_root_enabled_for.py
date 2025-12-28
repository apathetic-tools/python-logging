# tests/30_independant/test_is_root_enabled_for.py
"""Tests for isRootEnabledFor function."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_is_root_enabled_for_with_matching_level() -> None:
    """Test isRootEnabledFor returns True for enabled levels."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    # --- verify ---
    # Should be enabled for same and higher severity
    assert mod_alogs.isRootEnabledFor("INFO") is True
    assert mod_alogs.isRootEnabledFor("WARNING") is True
    assert mod_alogs.isRootEnabledFor("ERROR") is True

    # --- cleanup ---
    root.setLevel(original_level)


def test_is_root_enabled_for_with_disabled_level() -> None:
    """Test isRootEnabledFor returns False for disabled levels."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    # --- verify ---
    # Should not be enabled for lower severity (more verbose)
    assert mod_alogs.isRootEnabledFor("DEBUG") is False

    # --- cleanup ---
    root.setLevel(original_level)


def test_is_root_enabled_for_with_string_and_int() -> None:
    """Test isRootEnabledFor works with both string and integer levels."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    # --- verify ---
    # String level
    assert mod_alogs.isRootEnabledFor("INFO") is True
    assert mod_alogs.isRootEnabledFor("DEBUG") is False

    # Integer level
    assert mod_alogs.isRootEnabledFor(logging.INFO) is True
    assert mod_alogs.isRootEnabledFor(logging.DEBUG) is False

    # --- cleanup ---
    root.setLevel(original_level)
