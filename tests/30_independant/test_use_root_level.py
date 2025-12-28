# tests/30_independant/test_use_root_level.py
"""Tests for useRootLevel context manager."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_use_root_level_temporarily_changes_level() -> None:
    """Test that useRootLevel temporarily changes root level."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    with mod_alogs.useRootLevel("DEBUG"):
        # --- verify inside context ---
        assert mod_alogs.getRootLevel() == logging.DEBUG

    # --- verify after context ---
    # Should be restored after context
    assert mod_alogs.getRootLevel() == logging.INFO

    # --- cleanup ---
    root.setLevel(original_level)


def test_use_root_level_restores_on_exception() -> None:
    """Test that useRootLevel restores level even on exception."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    test_exception = ValueError("Test exception")
    try:
        with mod_alogs.useRootLevel("DEBUG"):
            assert mod_alogs.getRootLevel() == logging.DEBUG
            raise test_exception
    except ValueError:
        pass

    # --- verify ---
    # Should be restored even after exception
    assert mod_alogs.getRootLevel() == logging.INFO

    # --- cleanup ---
    root.setLevel(original_level)


def test_use_root_level_with_string_and_int() -> None:
    """Test useRootLevel with both string and integer levels."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    with mod_alogs.useRootLevel("DEBUG"):
        assert mod_alogs.getRootLevel() == logging.DEBUG

    with mod_alogs.useRootLevel(logging.WARNING):
        assert mod_alogs.getRootLevel() == logging.WARNING

    # --- cleanup ---
    root.setLevel(original_level)


def test_use_root_level_minimum_parameter_true() -> None:
    """Test useRootLevel with minimum=True only upgrades."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    # Try to downgrade with minimum=True - should not apply
    with mod_alogs.useRootLevel("WARNING", minimum=True):
        # --- verify inside context ---
        # Still at INFO (more verbose), not WARNING
        assert mod_alogs.getRootLevel() == logging.INFO

    # --- cleanup ---
    root.setLevel(original_level)


def test_use_root_level_minimum_parameter_false() -> None:
    """Test useRootLevel with minimum=False applies regardless."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    # With minimum=False, should apply even if downgrading
    with mod_alogs.useRootLevel("WARNING", minimum=False):
        # --- verify inside context ---
        assert mod_alogs.getRootLevel() == logging.WARNING

    # --- cleanup ---
    root.setLevel(original_level)
