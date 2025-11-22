# tests/30_independant/test_get_target_python_version.py
"""Test getTargetPythonVersion and get_target_python_version functions."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_target_python_version_returns_default_when_not_registered() -> None:
    """Test that getTargetPythonVersion returns module default when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_target_python_version = None

    # Should return module default
    assert mod_alogs.getTargetPythonVersion() == (3, 10)
    assert mod_alogs.get_target_python_version() == (3, 10)


def test_get_target_python_version_returns_registered_value() -> None:
    """Test that getTargetPythonVersion returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_target_python_version = None

    # Register a value
    mod_alogs.registerTargetPythonVersion((3, 11))
    assert mod_alogs.getTargetPythonVersion() == (3, 11)
    assert mod_alogs.get_target_python_version() == (3, 11)

    # Change it
    mod_alogs.registerTargetPythonVersion((3, 12))
    assert mod_alogs.getTargetPythonVersion() == (3, 12)
    assert mod_alogs.get_target_python_version() == (3, 12)

    # Reset
    _registry.registered_internal_target_python_version = None


def test_get_target_python_version_both_naming_conventions() -> None:
    """Test that both camelCase and snake_case functions work identically."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_target_python_version = None

    # Both should return same default
    assert mod_alogs.getTargetPythonVersion() == mod_alogs.get_target_python_version()

    # Register and both should return same value
    mod_alogs.registerTargetPythonVersion((3, 13))
    assert (
        mod_alogs.getTargetPythonVersion()
        == mod_alogs.get_target_python_version()
        == (3, 13)
    )

    # Reset
    _registry.registered_internal_target_python_version = None
