# tests/30_independant/test_register_port_level.py
"""Tests for registerPortLevel() function."""

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_port_level_stores_value() -> None:
    """registerPortLevel() should store the value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_level

    # --- execute ---
    mod_alogs.registerPortLevel(port_level=False)

    # --- verify ---
    assert _registry.registered_internal_port_level is False

    # --- cleanup ---
    _registry.registered_internal_port_level = original_value


def test_register_port_level_overwrites_previous() -> None:
    """registerPortLevel() should overwrite previous value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_level

    # Set initial value
    mod_alogs.registerPortLevel(port_level=False)

    # --- execute ---
    mod_alogs.registerPortLevel(port_level=True)

    # --- verify ---
    assert _registry.registered_internal_port_level is True

    # --- cleanup ---
    _registry.registered_internal_port_level = original_value


def test_register_port_level_accepts_none() -> None:
    """registerPortLevel() should accept None and skip registration."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_level

    # Set initial value
    mod_alogs.registerPortLevel(port_level=False)

    # --- execute ---
    mod_alogs.registerPortLevel(port_level=None)

    # --- verify ---
    # Value should be unchanged (None means skip)
    assert _registry.registered_internal_port_level is False

    # --- cleanup ---
    _registry.registered_internal_port_level = original_value


@pytest.mark.parametrize("port_level", [True, False])
def test_register_port_level_accepts_boolean_values(
    port_level: bool,  # noqa: FBT001
) -> None:
    """registerPortLevel() should accept True and False."""
    # --- setup ---

    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_level

    # --- execute ---
    mod_alogs.registerPortLevel(port_level=port_level)

    # --- verify ---
    assert _registry.registered_internal_port_level is port_level

    # --- cleanup ---
    _registry.registered_internal_port_level = original_value
