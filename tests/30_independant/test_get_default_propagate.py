# tests/30_independant/test_get_default_propagate.py
"""Test getDefaultPropagate function."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_default_propagate_returns_default_when_not_registered() -> None:
    """Test that getDefaultPropagate returns module default when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_propagate = None

    # Should return module default (True for root logger architecture)
    assert mod_alogs.getDefaultPropagate() is True


def test_get_default_propagate_returns_registered_value() -> None:
    """Test that getDefaultPropagate returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_propagate = None

    # Register True
    mod_alogs.registerPropagate(propagate=True)
    assert mod_alogs.getDefaultPropagate() is True

    # Change to False
    mod_alogs.registerPropagate(propagate=False)
    assert mod_alogs.getDefaultPropagate() is False

    # Reset
    _registry.registered_internal_propagate = None
