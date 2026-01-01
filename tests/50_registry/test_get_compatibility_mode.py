# tests/30_independant/test_get_compatibility_mode.py
"""Test getCompatibilityMode function."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_compatibility_mode_returns_default_when_not_registered() -> None:
    """Test that getCompatibilityMode returns default when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = None

    # Should return default (False)
    assert mod_alogs.getCompatibilityMode() is False


def test_get_compatibility_mode_returns_registered_value() -> None:
    """Test that getCompatibilityMode returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = None

    # Register True
    mod_alogs.registerCompatibilityMode(compat_mode=True)
    assert mod_alogs.getCompatibilityMode() is True

    # Change to False
    mod_alogs.registerCompatibilityMode(compat_mode=False)
    assert mod_alogs.getCompatibilityMode() is False

    # Reset
    _registry.registered_internal_compatibility_mode = None
