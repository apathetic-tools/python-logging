# tests/30_independant/test_get_default_log_level.py
"""Test getDefaultLogLevel and get_default_log_level functions."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_default_log_level_returns_default_when_not_registered() -> None:
    """Test that getDefaultLogLevel returns module default when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_default_log_level = None

    # Should return module default
    assert mod_alogs.getDefaultLogLevel() == "detail"
    assert mod_alogs.get_default_log_level() == "detail"


def test_get_default_log_level_returns_registered_value() -> None:
    """Test that getDefaultLogLevel returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_default_log_level = None

    # Register a value
    mod_alogs.registerDefaultLogLevel("warning")
    assert mod_alogs.getDefaultLogLevel() == "warning"
    assert mod_alogs.get_default_log_level() == "warning"

    # Change it
    mod_alogs.registerDefaultLogLevel("info")
    assert mod_alogs.getDefaultLogLevel() == "info"
    assert mod_alogs.get_default_log_level() == "info"

    # Reset
    _registry.registered_internal_default_log_level = None


def test_get_default_log_level_both_naming_conventions() -> None:
    """Test that both camelCase and snake_case functions work identically."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_default_log_level = None

    # Both should return same default
    assert mod_alogs.getDefaultLogLevel() == mod_alogs.get_default_log_level()

    # Register and both should return same value
    mod_alogs.registerDefaultLogLevel("debug")
    assert (
        mod_alogs.getDefaultLogLevel() == mod_alogs.get_default_log_level() == "debug"
    )

    # Reset
    _registry.registered_internal_default_log_level = None
