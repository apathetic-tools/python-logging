# tests/30_independant/test_get_effective_root_level_name.py
"""Tests for getEffectiveRootLevelName function."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_get_effective_root_level_name_returns_same_as_explicit() -> None:
    """Test that getEffectiveRootLevelName returns same as explicit for root."""
    root = logging.getLogger("")
    original_level = root.level

    mod_alogs.setRootLevel("INFO")

    # For root logger, effective level name should be same as explicit
    assert mod_alogs.getEffectiveRootLevelName() == mod_alogs.getRootLevelName()
    assert mod_alogs.getEffectiveRootLevelName() == "INFO"

    root.setLevel(original_level)
