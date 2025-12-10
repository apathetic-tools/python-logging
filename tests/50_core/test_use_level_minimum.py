# tests/50_core/test_use_level_minimum.py
"""Tests for Logger.useLevelMinimum() context manager."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


def test_use_level_minimum_prevents_downgrade(
    direct_logger: Logger,
) -> None:
    """useLevelMinimum() should not downgrade from more verbose levels."""
    # --- setup ---
    direct_logger.setLevel("TRACE")
    orig_level = direct_logger.level
    assert direct_logger.levelName == "TRACE"

    # --- execute and verify: TRACE should not downgrade to DEBUG ---
    with direct_logger.useLevelMinimum("DEBUG"):
        # Should stay at TRACE (more verbose than DEBUG)
        assert direct_logger.levelName == "TRACE"
        assert direct_logger.level == orig_level
    # Should restore to original TRACE
    assert direct_logger.level == orig_level

    # --- setup: now test that it does upgrade when current is less verbose ---
    direct_logger.setLevel("INFO")
    orig_level = direct_logger.level
    assert direct_logger.levelName == "INFO"

    # --- execute and verify: INFO should upgrade to DEBUG (more verbose) ---
    with direct_logger.useLevelMinimum("DEBUG"):
        # Should change to DEBUG (more verbose than INFO)
        assert direct_logger.levelName == "DEBUG"
        assert direct_logger.level != orig_level
    # Should restore to original INFO
    assert direct_logger.level == orig_level
    assert direct_logger.levelName == "INFO"


def test_use_level_minimum_with_effective_level_inheritance() -> None:
    """useLevelMinimum() should compare against effectiveLevel.

    This test verifies that useLevelMinimum() compares against effectiveLevel
    (what's actually used for logging), ensuring consistency with
    setLevel(minimum=True). Even when explicit and effective levels are the same,
    the comparison should use effectiveLevel to match setLevel's behavior.
    """
    # --- setup: create parent/child logger hierarchy ---
    parent = mod_alogs.getLogger("test_use_level_minimum_parent")
    parent.setLevel("WARNING")  # Parent has explicit WARNING

    child = mod_alogs.getLogger("test_use_level_minimum_parent.child")
    # Child will have a default level set (likely DETAIL or INFO), but we'll test
    # that useLevelMinimum() compares against effectiveLevel consistently

    # Get the current effective level (what's actually being used)
    current_effective = child.effectiveLevel
    current_explicit = child.level

    # Verify that useLevelMinimum() compares against effectiveLevel
    # by testing with a level more verbose than current effective
    more_verbose_level = logging.DEBUG  # More verbose than WARNING/INFO/DETAIL
    if more_verbose_level < current_effective:
        # Should upgrade to DEBUG (more verbose than current effective)
        with child.useLevelMinimum("DEBUG"):
            assert child.effectiveLevel == logging.DEBUG
            assert child.levelName == "DEBUG"
        # Should restore to original explicit level
        assert child.level == current_explicit
        assert child.effectiveLevel == current_effective

    # Test that it doesn't downgrade when requested level is less verbose
    less_verbose_level = logging.ERROR  # Less verbose than WARNING
    if less_verbose_level > current_effective:
        with child.useLevelMinimum("ERROR"):
            # Should stay at current effective level (not downgrade)
            assert child.effectiveLevel == current_effective
            assert child.level == current_explicit
        # Should still be at original level
        assert child.level == current_explicit
        assert child.effectiveLevel == current_effective

    # Key test: Verify consistency with setLevel(minimum=True)
    # Both should compare against effectiveLevel
    child.setLevel("TRACE")  # Set explicit to TRACE
    assert child.effectiveLevel == logging.DEBUG - 5  # TRACE level
    assert child.level == logging.DEBUG - 5

    # Now test that useLevelMinimum() behaves the same as setLevel(minimum=True)
    # Both should compare against the current effective level (TRACE)
    with child.useLevelMinimum("DEBUG"):
        # Should NOT downgrade from TRACE to DEBUG
        assert child.effectiveLevel == logging.DEBUG - 5  # Still TRACE
        assert child.levelName == "TRACE"
    # Should restore to TRACE
    assert child.level == logging.DEBUG - 5
    assert child.levelName == "TRACE"


def test_use_level_minimum_with_string_level(
    direct_logger: Logger,
) -> None:
    """useLevelMinimum() should accept string level names."""
    # --- setup ---
    direct_logger.setLevel("INFO")
    orig_level = direct_logger.level

    # --- execute ---
    with direct_logger.useLevelMinimum("DEBUG"):
        # --- verify ---
        assert direct_logger.level == logging.DEBUG
        assert direct_logger.levelName == "DEBUG"

    # --- verify restoration ---
    assert direct_logger.level == orig_level


def test_use_level_minimum_with_numeric_level(
    direct_logger: Logger,
) -> None:
    """useLevelMinimum() should accept numeric level values."""
    # --- setup ---
    direct_logger.setLevel(logging.INFO)
    orig_level = direct_logger.level

    # --- execute ---
    with direct_logger.useLevelMinimum(logging.DEBUG):
        # --- verify ---
        assert direct_logger.level == logging.DEBUG
        assert direct_logger.levelName == "DEBUG"

    # --- verify restoration ---
    assert direct_logger.level == orig_level
