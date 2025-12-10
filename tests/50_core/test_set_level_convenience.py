# tests/50_core/test_set_level_convenience.py
"""Tests for setLevel convenience functions (setLevelMinimum, setLevelInherit)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


def test_set_level_minimum_prevents_downgrade(
    direct_logger: Logger,
) -> None:
    """setLevelMinimum() should not downgrade from more verbose levels."""
    # --- setup ---
    direct_logger.setLevel("TRACE")
    assert direct_logger.levelName == "TRACE"

    # --- execute and verify: TRACE should not downgrade to DEBUG ---
    direct_logger.setLevelMinimum("DEBUG")
    # Should stay at TRACE (more verbose than DEBUG)
    assert direct_logger.levelName == "TRACE"

    # --- setup: now test that it does upgrade when current is less verbose ---
    direct_logger.setLevel("INFO")
    assert direct_logger.levelName == "INFO"

    # --- execute and verify: INFO should upgrade to DEBUG (more verbose) ---
    direct_logger.setLevelMinimum("DEBUG")
    # Should change to DEBUG (more verbose than INFO)
    assert direct_logger.levelName == "DEBUG"


def test_set_level_minimum_with_effective_level_inheritance() -> None:
    """setLevelMinimum() should compare against effectiveLevel."""
    # --- setup: create parent/child logger hierarchy ---
    parent = mod_alogs.getLogger("test_set_level_minimum_parent")
    parent.setLevel("WARNING")  # Parent has explicit WARNING

    child = mod_alogs.getLogger("test_set_level_minimum_parent.child")
    # Child will have a default level set (likely DETAIL or INFO), but we'll test
    # that setLevelMinimum() compares against effectiveLevel consistently

    # Get the current effective level (what's actually being used)
    current_effective = child.effectiveLevel
    current_explicit = child.level

    # Verify that setLevelMinimum() compares against effectiveLevel
    # by testing with a level more verbose than current effective
    more_verbose_level = logging.DEBUG  # More verbose than WARNING/INFO/DETAIL
    if more_verbose_level < current_effective:
        # Should upgrade to DEBUG (more verbose than current effective)
        child.setLevelMinimum("DEBUG")
        assert child.effectiveLevel == logging.DEBUG
        assert child.levelName == "DEBUG"
        # Restore
        child.setLevel(current_explicit, allow_inherit=True)

    # Test that it doesn't downgrade when requested level is less verbose
    less_verbose_level = logging.ERROR  # Less verbose than WARNING
    if less_verbose_level > current_effective:
        child.setLevelMinimum("ERROR")
        # Should stay at current effective level (not downgrade)
        assert child.effectiveLevel == current_effective
        assert child.level == current_explicit
        # Restore
        child.setLevel(current_explicit, allow_inherit=True)

    # Key test: Verify consistency with setLevel(minimum=True)
    # Both should compare against effectiveLevel
    child.setLevel("TRACE")  # Set explicit to TRACE
    assert child.effectiveLevel == logging.DEBUG - 5  # TRACE level
    assert child.level == logging.DEBUG - 5

    # Now test that setLevelMinimum() behaves the same as setLevel(minimum=True)
    # Both should compare against the current effective level (TRACE)
    child.setLevelMinimum("DEBUG")
    # Should NOT downgrade from TRACE to DEBUG
    assert child.effectiveLevel == logging.DEBUG - 5  # Still TRACE
    assert child.levelName == "TRACE"


def test_set_level_inherit_sets_to_notset(
    direct_logger: Logger,
) -> None:
    """setLevelInherit() should set logger to INHERIT_LEVEL (i.e. NOTSET)."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    direct_logger.setLevel("INFO")
    assert direct_logger.level == logging.INFO

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute ---
        direct_logger.setLevelInherit()

        # --- verify ---
        assert direct_logger.level == _constants.INHERIT_LEVEL
        assert direct_logger.levelName == "NOTSET"
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_inherit_inherits_from_parent() -> None:
    """setLevelInherit() should cause inheritance from parent."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("WARNING")

    logger = mod_alogs.getLogger("test_set_level_inherit")
    logger.setLevel("DEBUG")  # Set explicit level first
    assert logger.level == logging.DEBUG
    assert logger.effectiveLevel == logging.DEBUG

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute ---
        logger.setLevelInherit()

        # --- verify ---
        assert logger.level == _constants.INHERIT_LEVEL
        assert logger.levelName == "NOTSET"
        # Should now inherit from root
        assert logger.effectiveLevel == logging.WARNING
        assert logger.effectiveLevelName == "WARNING"
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode
        root.setLevel(original_root_level)


def test_set_level_inherit_clears_cache(
    direct_logger: Logger,
) -> None:
    """setLevelInherit() should clear isEnabledFor cache."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    direct_logger.setLevel("TRACE")
    _constants = mod_alogs.apathetic_logging
    trace_level = _constants.TRACE_LEVEL

    # Trigger cache by calling trace()
    direct_logger.trace("trigger")
    cache_before = getattr(direct_logger, "_cache", None)
    if cache_before is not None:
        assert trace_level in cache_before

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute ---
        direct_logger.setLevelInherit()

        # --- verify ---
        cache_after = getattr(direct_logger, "_cache", None)
        if cache_after is not None:
            # Cache should be cleared
            assert (
                trace_level not in cache_after or cache_after.get(trace_level) is None
            )
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_inherit_works_in_compat_mode(
    direct_logger: Logger,
) -> None:
    """setLevelInherit() should work in compatibility mode."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    direct_logger.setLevel("INFO")
    assert direct_logger.level == logging.INFO

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=True)
        # --- execute ---
        direct_logger.setLevelInherit()

        # --- verify ---
        assert direct_logger.level == _constants.INHERIT_LEVEL
        assert direct_logger.levelName == "NOTSET"
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_minimum_with_string_level(
    direct_logger: Logger,
) -> None:
    """setLevelMinimum() should accept string level names."""
    # --- setup ---
    direct_logger.setLevel("INFO")

    # --- execute ---
    direct_logger.setLevelMinimum("DEBUG")

    # --- verify ---
    assert direct_logger.level == logging.DEBUG
    assert direct_logger.levelName == "DEBUG"


def test_set_level_minimum_with_numeric_level(
    direct_logger: Logger,
) -> None:
    """setLevelMinimum() should accept numeric level values."""
    # --- setup ---
    direct_logger.setLevel(logging.INFO)

    # --- execute ---
    direct_logger.setLevelMinimum(logging.DEBUG)

    # --- verify ---
    assert direct_logger.level == logging.DEBUG
    assert direct_logger.levelName == "DEBUG"
