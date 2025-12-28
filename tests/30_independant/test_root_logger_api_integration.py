# tests/30_independant/test_root_logger_api_integration.py
"""Integration tests for root logger API."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_get_and_set_root_level_consistency() -> None:
    """Test that get and set operations are consistent."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    test_levels = [
        ("DEBUG", logging.DEBUG, "DEBUG"),
        ("INFO", logging.INFO, "INFO"),
        ("WARNING", logging.WARNING, "WARNING"),
    ]

    # --- execute and verify ---
    for level_str, expected_int, expected_str in test_levels:
        mod_alogs.setRootLevel(level_str)
        assert mod_alogs.getRootLevel() == expected_int
        assert mod_alogs.getRootLevelName() == expected_str

    # --- cleanup ---
    root.setLevel(original_level)


def test_root_api_does_not_affect_child_loggers_at_notset() -> None:
    """Test that root API doesn't affect child loggers that inherit."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    child = mod_alogs.getLogger("test_child_inherit")
    # Child should be at NOTSET to inherit
    assert child.level == logging.NOTSET

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG")
    # --- verify ---
    # Child effective level should follow root
    assert child.effectiveLevel == logging.DEBUG

    mod_alogs.setRootLevel("INFO")
    # --- verify ---
    # Child effective level should follow root
    assert child.effectiveLevel == logging.INFO

    # --- cleanup ---
    root.setLevel(original_root_level)


def test_use_root_level_with_nested_contexts() -> None:
    """Test nested useRootLevel contexts."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("WARNING")
    assert mod_alogs.getRootLevel() == logging.WARNING

    with mod_alogs.useRootLevel("INFO"):
        # --- verify inside outer context ---
        assert mod_alogs.getRootLevel() == logging.INFO

        with mod_alogs.useRootLevel("DEBUG"):
            # --- verify inside inner context ---
            assert mod_alogs.getRootLevel() == logging.DEBUG

        # --- verify after inner context ---
        # Should restore to INFO after inner context
        assert mod_alogs.getRootLevel() == logging.INFO

    # --- verify after outer context ---
    # Should restore to WARNING after outer context
    assert mod_alogs.getRootLevel() == logging.WARNING

    # --- cleanup ---
    root.setLevel(original_level)
