# tests/30_independant/test_get_default_propagate.py
"""Test getDefaultPropagate and get_default_propagate functions."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_default_propagate_returns_default_when_not_registered() -> None:
    """Test that getDefaultPropagate returns module default when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_propagate = None

    # Should return module default
    assert mod_alogs.getDefaultPropagate() is False
    assert mod_alogs.get_default_propagate() is False


def test_get_default_propagate_returns_registered_value() -> None:
    """Test that getDefaultPropagate returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_propagate = None

    # Register True
    mod_alogs.registerPropagate(propagate=True)
    assert mod_alogs.getDefaultPropagate() is True
    assert mod_alogs.get_default_propagate() is True

    # Change to False
    mod_alogs.registerPropagate(propagate=False)
    assert mod_alogs.getDefaultPropagate() is False
    assert mod_alogs.get_default_propagate() is False

    # Reset
    _registry.registered_internal_propagate = None


def test_get_default_propagate_both_naming_conventions() -> None:
    """Test that both camelCase and snake_case functions work identically."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_propagate = None

    # Both should return same default
    assert mod_alogs.getDefaultPropagate() == mod_alogs.get_default_propagate()

    # Register and both should return same value
    mod_alogs.registerPropagate(propagate=True)
    assert mod_alogs.getDefaultPropagate() == mod_alogs.get_default_propagate() is True

    # Reset
    _registry.registered_internal_propagate = None
