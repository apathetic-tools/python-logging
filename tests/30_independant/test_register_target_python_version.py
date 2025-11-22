# tests/30_independant/test_register_target_python_version.py
"""Tests for register_target_python_version function."""

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_target_python_version_stores_value() -> None:
    """register_target_python_version() should store the target Python version."""
    # --- setup ---
    version = (3, 11)

    # --- execute ---
    mod_alogs.registerTargetPythonVersion(version)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_target_python_version == version


def test_register_target_python_version_overwrites_previous() -> None:
    """register_target_python_version() should overwrite previous value."""
    # --- setup ---
    mod_alogs.registerTargetPythonVersion((3, 10))

    # --- execute ---
    mod_alogs.registerTargetPythonVersion((3, 12))

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_target_python_version == (3, 12)


def test_register_target_python_version_accepts_none() -> None:
    """register_target_python_version() should accept None and return early."""
    # --- setup ---
    mod_alogs.registerTargetPythonVersion((3, 11))
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_target_python_version

    # --- execute ---
    mod_alogs.registerTargetPythonVersion(None)

    # --- verify ---
    # Should not have changed the value
    assert _registry.registered_internal_target_python_version == original_value


@pytest.mark.parametrize("version", [(3, 10), (3, 11), (3, 12)])
def test_register_target_python_version_accepts_valid_versions(
    version: tuple[int, int],
) -> None:
    """register_target_python_version() should accept various Python versions."""
    # --- execute ---
    mod_alogs.registerTargetPythonVersion(version)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_target_python_version == version
