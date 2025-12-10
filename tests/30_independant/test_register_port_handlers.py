# tests/30_independant/test_register_port_handlers.py
"""Tests for registerPortHandlers() function."""

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_port_handlers_stores_value() -> None:
    """registerPortHandlers() should store the value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_handlers

    # --- execute ---
    mod_alogs.registerPortHandlers(port_handlers=False)

    # --- verify ---
    assert _registry.registered_internal_port_handlers is False

    # --- cleanup ---
    _registry.registered_internal_port_handlers = original_value


def test_register_port_handlers_overwrites_previous() -> None:
    """registerPortHandlers() should overwrite previous value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_handlers

    # Set initial value
    mod_alogs.registerPortHandlers(port_handlers=False)

    # --- execute ---
    mod_alogs.registerPortHandlers(port_handlers=True)

    # --- verify ---
    assert _registry.registered_internal_port_handlers is True

    # --- cleanup ---
    _registry.registered_internal_port_handlers = original_value


def test_register_port_handlers_accepts_none() -> None:
    """registerPortHandlers() should accept None and skip registration."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_handlers

    # Set initial value
    mod_alogs.registerPortHandlers(port_handlers=False)

    # --- execute ---
    mod_alogs.registerPortHandlers(port_handlers=None)

    # --- verify ---
    # Value should be unchanged (None means skip)
    assert _registry.registered_internal_port_handlers is False

    # --- cleanup ---
    _registry.registered_internal_port_handlers = original_value


@pytest.mark.parametrize("port_handlers", [True, False])
def test_register_port_handlers_accepts_boolean_values(
    port_handlers: bool,  # noqa: FBT001
) -> None:
    """registerPortHandlers() should accept True and False."""
    # --- setup ---

    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_port_handlers

    # --- execute ---
    mod_alogs.registerPortHandlers(port_handlers=port_handlers)

    # --- verify ---
    assert _registry.registered_internal_port_handlers is port_handlers

    # --- cleanup ---
    _registry.registered_internal_port_handlers = original_value
