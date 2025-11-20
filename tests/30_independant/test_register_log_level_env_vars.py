# tests/30_independant/test_register_log_level_env_vars.py
"""Tests for register_log_level_env_vars function."""

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_log_level_env_vars_stores_list() -> None:
    """register_log_level_env_vars() should store the list of env var names."""
    # --- setup ---
    env_vars = ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]

    # --- execute ---
    mod_alogs.registerLogLevelEnvVars(env_vars)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_log_level_env_vars == env_vars


def test_register_log_level_env_vars_overwrites_previous() -> None:
    """register_log_level_env_vars() should overwrite previous value."""
    # --- setup ---
    mod_alogs.registerLogLevelEnvVars(["OLD_VAR"])

    # --- execute ---
    new_vars = ["NEW_VAR1", "NEW_VAR2"]
    mod_alogs.registerLogLevelEnvVars(new_vars)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_log_level_env_vars == new_vars


def test_register_log_level_env_vars_empty_list() -> None:
    """register_log_level_env_vars() should accept empty list."""
    # --- execute ---
    mod_alogs.registerLogLevelEnvVars([])

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_log_level_env_vars == []


def test_register_log_level_env_vars_single_var() -> None:
    """register_log_level_env_vars() should accept single env var."""
    # --- setup ---
    env_vars = ["SINGLE_VAR"]

    # --- execute ---
    mod_alogs.registerLogLevelEnvVars(env_vars)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_log_level_env_vars == env_vars
