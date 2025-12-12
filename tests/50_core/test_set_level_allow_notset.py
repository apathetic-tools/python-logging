"""Tests for setLevel() NOTSET inheritance support."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


def test_set_level_notset_allows_inheritance() -> None:
    """setLevel(0) should be allowed and cause inheritance from parent."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("WARNING")

    logger = mod_alogs.getLogger("test_notset_inherit")
    logger.setLevel("DEBUG")  # Set explicit level first
    assert logger.level == logging.DEBUG
    assert logger.effectiveLevel == logging.DEBUG

    try:
        # --- execute ---
        logger.setLevel(0)

        # --- verify ---
        assert logger.level == _constants.INHERIT_LEVEL
        assert logger.levelName == "NOTSET"
        # Should now inherit from root
        assert logger.effectiveLevel == logging.WARNING
        assert logger.effectiveLevelName == "WARNING"
    finally:
        root.setLevel(original_root_level)


def test_set_level_notset_string_allows_inheritance() -> None:
    """setLevel("NOTSET") should be allowed and cause inheritance."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("WARNING")

    logger = mod_alogs.getLogger("test_notset_string")
    logger.setLevel("DEBUG")

    try:
        # --- execute ---
        logger.setLevel("NOTSET")

        # --- verify ---
        assert logger.levelName == "NOTSET"
        assert logger.effectiveLevel == logging.WARNING
    finally:
        root.setLevel(original_root_level)


def test_set_level_notset_clears_cache(direct_logger: Logger) -> None:
    """setLevel(0) should clear isEnabledFor cache."""
    # --- setup ---
    direct_logger.setLevel("TRACE")
    _constants = mod_alogs.apathetic_logging
    trace_level = _constants.TRACE_LEVEL

    # Trigger cache by calling trace()
    direct_logger.trace("trigger")
    cache_before = getattr(direct_logger, "_cache", None)
    if cache_before is not None:
        assert trace_level in cache_before

    # --- execute ---
    direct_logger.setLevel(0)

    # --- verify ---
    cache_after = getattr(direct_logger, "_cache", None)
    if cache_after is not None:
        # Cache should be cleared
        assert trace_level not in cache_after or cache_after.get(trace_level) is None


def test_set_level_notset_with_minimum_parameter(direct_logger: Logger) -> None:
    """setLevel(0) should work with minimum parameter."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    direct_logger.setLevel("WARNING")
    assert direct_logger.level == logging.WARNING

    # --- execute ---
    # minimum=True should allow setting to INHERIT_LEVEL (i.e. NOTSET)
    # because INHERIT_LEVEL (i.e. NOTSET) (0) is more verbose than WARNING (30),
    # so it's an upgrade
    direct_logger.setLevel(0, minimum=True)

    # --- verify ---
    # Should have set to INHERIT_LEVEL (i.e. NOTSET) since it's more verbose
    assert direct_logger.level == _constants.INHERIT_LEVEL

    # Now test that minimum=True prevents downgrading to less verbose levels
    # Set to a less verbose level (ERROR) - should be prevented by minimum=True
    direct_logger.setLevel("ERROR", minimum=True)
    # Should not have changed because ERROR (40) is less verbose than
    # INHERIT_LEVEL (i.e. NOTSET) (0). (effective level might be from parent,
    # but explicit level should stay INHERIT_LEVEL (i.e. NOTSET))
    assert direct_logger.level == _constants.INHERIT_LEVEL


def test_set_level_negative_in_improved_mode_raises(direct_logger: Logger) -> None:
    """setLevel() should reject negative values in improved mode."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute and verify ---
        with pytest.raises(ValueError, match=r"< 0.*PEP 282"):
            direct_logger.setLevel(-1)

        with pytest.raises(ValueError, match=r"< 0.*PEP 282"):
            direct_logger.setLevel(-10)
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_negative_in_compat_mode_succeeds(direct_logger: Logger) -> None:
    """setLevel() should accept negative values in compatibility mode."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    direct_logger.setLevel("INFO")
    assert direct_logger.level == logging.INFO

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=True)
        # --- execute ---
        direct_logger.setLevel(-1)

        # --- verify ---
        assert direct_logger.level == -1
        # Negative levels allow all messages through
        assert direct_logger.isEnabledFor(logging.DEBUG) is True
        assert direct_logger.isEnabledFor(logging.CRITICAL) is True
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_notset_in_compat_mode_succeeds(direct_logger: Logger) -> None:
    """setLevel(0) should succeed in compatibility mode."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    direct_logger.setLevel("INFO")
    assert direct_logger.level == logging.INFO

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=True)
        # --- execute ---
        direct_logger.setLevel(0)
        # All of these should work in compat mode
        direct_logger.setLevel("WARNING")
        direct_logger.setLevel(0)

        # --- verify ---
        assert direct_logger.level == _constants.INHERIT_LEVEL
        assert direct_logger.levelName == "NOTSET"
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_inherit_convenience_method(direct_logger: Logger) -> None:
    """setLevelInherit() should set level to NOTSET for inheritance."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("WARNING")

    direct_logger.setLevel("DEBUG")
    assert direct_logger.level == logging.DEBUG

    try:
        # --- execute ---
        direct_logger.setLevelInherit()

        # --- verify ---
        assert direct_logger.level == _constants.INHERIT_LEVEL
        assert direct_logger.levelName == "NOTSET"
        # After setting to NOTSET, the logger inherits from parent
        # Since direct_logger's parent chain goes through root,
        # effective level should come from the inheritance chain
        # (In Python stdlib, effective level traces through parents)
        parent = direct_logger.parent
        while parent is not None:
            if parent.level > 0:
                expected = parent.level
                break
            parent = parent.parent
        else:
            expected = logging.WARNING  # default if no parent with level
        assert direct_logger.effectiveLevel == expected
    finally:
        root.setLevel(original_root_level)
