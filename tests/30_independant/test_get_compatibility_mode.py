# tests/30_independant/test_get_compatibility_mode.py
"""Test getCompatibilityMode and get_compatibility_mode functions."""

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
    assert mod_alogs.get_compatibility_mode() is False


def test_get_compatibility_mode_returns_registered_value() -> None:
    """Test that getCompatibilityMode returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = None

    # Register True
    mod_alogs.registerCompatibilityMode(compatibility_mode=True)
    assert mod_alogs.getCompatibilityMode() is True
    assert mod_alogs.get_compatibility_mode() is True

    # Change to False
    mod_alogs.registerCompatibilityMode(compatibility_mode=False)
    assert mod_alogs.getCompatibilityMode() is False
    assert mod_alogs.get_compatibility_mode() is False

    # Reset
    _registry.registered_internal_compatibility_mode = None


def test_get_compatibility_mode_both_naming_conventions() -> None:
    """Test that both camelCase and snake_case functions work identically."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = None

    # Both should return same default
    camel_result = mod_alogs.getCompatibilityMode()
    snake_result = mod_alogs.get_compatibility_mode()
    assert camel_result == snake_result is False

    # Register and both should return same value
    mod_alogs.registerCompatibilityMode(compatibility_mode=True)
    camel_result = mod_alogs.getCompatibilityMode()
    snake_result = mod_alogs.get_compatibility_mode()
    assert camel_result == snake_result is True

    # Reset
    _registry.registered_internal_compatibility_mode = None
