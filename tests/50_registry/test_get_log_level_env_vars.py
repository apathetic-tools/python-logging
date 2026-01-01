# tests/30_independant/test_get_log_level_env_vars.py
"""Test getLogLevelEnvVars function."""

from __future__ import annotations

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_log_level_env_vars_returns_default_when_not_registered() -> None:
    """Test that getLogLevelEnvVars returns module default when not registered."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_log_level_env_vars = None

    # Should return module default
    assert mod_alogs.getLogLevelEnvVars() == ["LOG_LEVEL"]


def test_get_log_level_env_vars_returns_registered_value() -> None:
    """Test that getLogLevelEnvVars returns registered value when set."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_log_level_env_vars = None

    # Register a value
    mod_alogs.registerLogLevelEnvVars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])
    assert mod_alogs.getLogLevelEnvVars() == ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]

    # Change it
    mod_alogs.registerLogLevelEnvVars(["CUSTOM_LOG_LEVEL"])
    assert mod_alogs.getLogLevelEnvVars() == ["CUSTOM_LOG_LEVEL"]

    # Reset
    _registry.registered_internal_log_level_env_vars = None
