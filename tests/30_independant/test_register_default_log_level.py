# tests/30_independant/test_register_default_log_level.py
"""Tests for register_default_log_level function."""

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_default_log_level_stores_value() -> None:
    """register_default_log_level() should store the default log level."""
    # --- setup ---
    default_level = "warning"

    # --- execute ---
    mod_alogs.registerDefaultLogLevel(default_level)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_default_log_level == default_level


def test_register_default_log_level_overwrites_previous() -> None:
    """register_default_log_level() should overwrite previous value."""
    # --- setup ---
    mod_alogs.registerDefaultLogLevel("info")

    # --- execute ---
    mod_alogs.registerDefaultLogLevel("debug")

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_default_log_level == "debug"


@pytest.mark.parametrize("level", ["trace", "debug", "info", "warning", "error"])
def test_register_default_log_level_accepts_valid_levels(level: str) -> None:
    """register_default_log_level() should accept various log levels."""
    # --- execute ---
    mod_alogs.registerDefaultLogLevel(level)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_default_log_level == level


def test_register_default_log_level_accepts_none() -> None:
    """register_default_log_level() should accept None and return early."""
    # --- setup ---
    mod_alogs.registerDefaultLogLevel("info")
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_default_log_level

    # --- execute ---
    mod_alogs.registerDefaultLogLevel(None)

    # --- verify ---
    # Should not have changed the value
    assert _registry.registered_internal_default_log_level == original_value
