# tests/30_independant/test_get_target_python_version.py
"""Test getTargetPythonVersion function."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_target_python_version_returns_default_when_not_registered() -> None:
    """Test that getTargetPythonVersion returns module default when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_target_python_version = None

    # Should return None when MIN_PYTHON_VERSION is None (checks disabled)
    assert mod_alogs.getTargetPythonVersion() is None


def test_get_target_python_version_returns_registered_value() -> None:
    """Test that getTargetPythonVersion returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_target_python_version = None

    # Register a value
    mod_alogs.registerTargetPythonVersion((3, 11))
    assert mod_alogs.getTargetPythonVersion() == (3, 11)

    # Change it
    mod_alogs.registerTargetPythonVersion((3, 12))
    assert mod_alogs.getTargetPythonVersion() == (3, 12)

    # Reset
    _registry.registered_internal_target_python_version = None
