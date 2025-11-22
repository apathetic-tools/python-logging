# tests/30_independant/test_register_compatibility_mode.py
"""Tests for register_compatibility_mode function."""

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_compatibility_mode_stores_value() -> None:
    """register_compatibility_mode() should store the compatibility mode setting."""
    # --- setup ---
    compatibility_mode = True

    # --- execute ---
    mod_alogs.registerCompatibilityMode(compatibility_mode=compatibility_mode)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_compatibility_mode == compatibility_mode


def test_register_compatibility_mode_overwrites_previous() -> None:
    """register_compatibility_mode() should overwrite previous value."""
    # --- setup ---
    mod_alogs.registerCompatibilityMode(compatibility_mode=True)

    # --- execute ---
    mod_alogs.registerCompatibilityMode(compatibility_mode=False)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_compatibility_mode is False


def test_register_compatibility_mode_accepts_none() -> None:
    """register_compatibility_mode() should accept None and return early."""
    # --- setup ---
    mod_alogs.registerCompatibilityMode(compatibility_mode=True)
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_compatibility_mode

    # --- execute ---
    mod_alogs.registerCompatibilityMode(compatibility_mode=None)

    # --- verify ---
    # Should not have changed the value
    assert _registry.registered_internal_compatibility_mode == original_value


@pytest.mark.parametrize("compatibility_mode", [True, False])
def test_register_compatibility_mode_accepts_boolean_values(
    compatibility_mode: bool,  # noqa: FBT001
) -> None:
    """register_compatibility_mode() should accept True and False."""
    # --- execute ---
    mod_alogs.registerCompatibilityMode(compatibility_mode=compatibility_mode)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_compatibility_mode == compatibility_mode


def test_register_compatibility_mode_snake_case() -> None:
    """register_compatibility_mode() snake_case should work identically."""
    # --- setup ---
    compatibility_mode = True

    # --- execute ---
    mod_alogs.register_compatibility_mode(compatibility_mode=compatibility_mode)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_compatibility_mode == compatibility_mode
