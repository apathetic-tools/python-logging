# tests/30_independant/test_get_registered_logger_name.py
"""Test getRegisteredLoggerName function."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_registered_logger_name_returns_none_when_not_registered() -> None:
    """Test that getRegisteredLoggerName returns None when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_logger_name = None

    # Should return None (no default)
    assert mod_alogs.getRegisteredLoggerName() is None


def test_get_registered_logger_name_returns_registered_value() -> None:
    """Test that getRegisteredLoggerName returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_logger_name = None

    # Register a value
    mod_alogs.registerLogger("myapp")
    assert mod_alogs.getRegisteredLoggerName() == "myapp"

    # Change it
    mod_alogs.registerLogger("myotherapp")
    assert mod_alogs.getRegisteredLoggerName() == "myotherapp"

    # Reset
    _registry.registered_internal_logger_name = None
