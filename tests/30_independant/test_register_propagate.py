# tests/30_independant/test_register_propagate.py
"""Tests for register_propagate function."""

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_propagate_stores_value() -> None:
    """register_propagate() should store the propagate setting."""
    # --- setup ---
    propagate = True

    # --- execute ---
    mod_alogs.registerPropagate(propagate=propagate)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_propagate == propagate


def test_register_propagate_overwrites_previous() -> None:
    """register_propagate() should overwrite previous value."""
    # --- setup ---
    mod_alogs.registerPropagate(propagate=True)

    # --- execute ---
    mod_alogs.registerPropagate(propagate=False)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_propagate is False


def test_register_propagate_accepts_none() -> None:
    """register_propagate() should accept None and return early."""
    # --- setup ---
    mod_alogs.registerPropagate(propagate=True)
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_propagate

    # --- execute ---
    mod_alogs.registerPropagate(propagate=None)

    # --- verify ---
    # Should not have changed the value
    assert _registry.registered_internal_propagate == original_value


@pytest.mark.parametrize("propagate", [True, False])
def test_register_propagate_accepts_boolean_values(propagate: bool) -> None:  # noqa: FBT001
    """register_propagate() should accept True and False."""
    # --- execute ---
    mod_alogs.registerPropagate(propagate=propagate)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_propagate == propagate
