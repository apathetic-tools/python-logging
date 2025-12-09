# tests/50_core/test_set_level_allow_notset.py
"""Tests for setLevel() allow_inherit parameter."""

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


def test_set_level_notset_without_allow_inherit_raises(direct_logger: Logger) -> None:
    """setLevel(0) should raise ValueError in improved mode without allow_inherit."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute and verify ---
        with pytest.raises(ValueError, match=r"setLevel\(0\).*allow_inherit=True"):
            direct_logger.setLevel(0)

        with pytest.raises(ValueError, match=r"setLevel\(0\).*allow_inherit=True"):
            direct_logger.setLevel(_constants.INHERIT_LEVEL)
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_notset_with_allow_inherit_succeeds(direct_logger: Logger) -> None:
    """setLevel(0, allow_inherit=True) should succeed in improved mode."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    direct_logger.setLevel("INFO")
    assert direct_logger.level == logging.INFO

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute ---
        direct_logger.setLevel(0, allow_inherit=True)

        # --- verify ---
        assert direct_logger.level == _constants.INHERIT_LEVEL
        assert direct_logger.levelName == "NOTSET"
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_notset_in_compat_mode_succeeds(direct_logger: Logger) -> None:
    """setLevel(0) should succeed in compatibility mode without allow_inherit."""
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
        # allow_inherit parameter should be ignored in compat mode
        direct_logger.setLevel("WARNING")
        direct_logger.setLevel(0, allow_inherit=False)  # Should still work

        # --- verify ---
        assert direct_logger.level == _constants.INHERIT_LEVEL
        assert direct_logger.levelName == "NOTSET"
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


def test_set_level_negative_in_improved_mode_raises(direct_logger: Logger) -> None:
    """setLevel() should reject negative values in improved mode."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute and verify ---
        with pytest.raises(ValueError, match=r"<= 0.*PEP 282"):
            direct_logger.setLevel(-1)

        with pytest.raises(ValueError, match=r"<= 0.*PEP 282"):
            direct_logger.setLevel(-10)
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_notset_with_allow_inherit_inherits_from_parent() -> None:
    """setLevel(0, allow_inherit=True) should cause inheritance from parent."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("WARNING")

    logger = mod_alogs.getLogger("test_notset_inherit")
    logger.setLevel("DEBUG")  # Set explicit level first
    assert logger.level == logging.DEBUG
    assert logger.effectiveLevel == logging.DEBUG

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute ---
        logger.setLevel(0, allow_inherit=True)

        # --- verify ---
        assert logger.level == _constants.INHERIT_LEVEL
        assert logger.levelName == "NOTSET"
        # Should now inherit from root
        assert logger.effectiveLevel == logging.WARNING
        assert logger.effectiveLevelName == "WARNING"
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode
        root.setLevel(original_root_level)


def test_set_level_notset_with_allow_inherit_clears_cache(
    direct_logger: Logger,
) -> None:
    """setLevel(0, allow_inherit=True) should clear isEnabledFor cache."""
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
        direct_logger.setLevel(0, allow_inherit=True)

        # --- verify ---
        cache_after = getattr(direct_logger, "_cache", None)
        if cache_after is not None:
            # Cache should be cleared
            assert (
                trace_level not in cache_after or cache_after.get(trace_level) is None
            )
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode


def test_set_level_notset_with_minimum_parameter(direct_logger: Logger) -> None:
    """setLevel(0, allow_inherit=True) should work with minimum parameter."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry.registered_internal_compatibility_mode

    direct_logger.setLevel("WARNING")
    assert direct_logger.level == logging.WARNING

    try:
        mod_alogs.registerCompatibilityMode(compat_mode=False)
        # --- execute ---
        # minimum=True should allow setting to INHERIT_LEVEL (i.e. NOTSET)
        # when allow_inherit=True because INHERIT_LEVEL (i.e. NOTSET) (0) is
        # more verbose than WARNING (30), so it's an upgrade
        direct_logger.setLevel(0, allow_inherit=True, minimum=True)

        # --- verify ---
        # Should have set to INHERIT_LEVEL (i.e. NOTSET) since it's more
        # verbose
        assert direct_logger.level == _constants.INHERIT_LEVEL

        # Now test that minimum=True prevents downgrading to less verbose
        # levels. Set to a less verbose level (ERROR) - should be prevented by
        # minimum=True
        direct_logger.setLevel("ERROR", minimum=True)
        # Should not have changed because ERROR (40) is less verbose than
        # INHERIT_LEVEL (i.e. NOTSET) (0). (effective level might be from
        # parent, but explicit level should stay INHERIT_LEVEL (i.e. NOTSET))
        assert direct_logger.level == _constants.INHERIT_LEVEL
    finally:
        _registry.registered_internal_compatibility_mode = original_compat_mode
