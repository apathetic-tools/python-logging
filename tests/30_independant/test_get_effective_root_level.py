# tests/30_independant/test_get_effective_root_level.py
"""Tests for getEffectiveRootLevel function."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_get_effective_root_level_returns_same_as_explicit() -> None:
    """Test that getEffectiveRootLevel returns same as explicit for root."""
    root = logging.getLogger("")
    original_level = root.level

    mod_alogs.setRootLevel("DEBUG")

    # For root logger, effective level should be same as explicit level
    assert mod_alogs.getEffectiveRootLevel() == mod_alogs.getRootLevel()
    assert mod_alogs.getEffectiveRootLevel() == logging.DEBUG

    root.setLevel(original_level)
