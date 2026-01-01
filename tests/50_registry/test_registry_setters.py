# tests/30_independant/test_registry_setters.py
"""Comprehensive tests for registry setter functions.

This consolidates registry setter tests which all follow the same pattern:
- Store a value
- Overwrite a previous value
- Accept None without changing value
- Accept valid values via parametrization
"""

from typing import Any

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


# ============================================================================
# Test Configuration: Maps registry function to its attributes
# ============================================================================

REGISTRY_SETTERS = [
    {
        "name": "registerPropagate",
        "func": mod_alogs.registerPropagate,
        "registry_attr": "registered_internal_propagate",
        "valid_values": [True, False],
        "kwarg_name": "propagate",
    },
    {
        "name": "registerPortLevel",
        "func": mod_alogs.registerPortLevel,
        "registry_attr": "registered_internal_port_level",
        "valid_values": [True, False],
        "kwarg_name": "port_level",
    },
    {
        "name": "registerPortHandlers",
        "func": mod_alogs.registerPortHandlers,
        "registry_attr": "registered_internal_port_handlers",
        "valid_values": [True, False],
        "kwarg_name": "port_handlers",
    },
    {
        "name": "registerCompatibilityMode",
        "func": mod_alogs.registerCompatibilityMode,
        "registry_attr": "registered_internal_compatibility_mode",
        "valid_values": [True, False],
        "kwarg_name": "compat_mode",
    },
    {
        "name": "registerDefaultLogLevel",
        "func": mod_alogs.registerDefaultLogLevel,
        "registry_attr": "registered_internal_default_log_level",
        "valid_values": ["trace", "debug", "info", "warning", "error"],
        "kwarg_name": "default_level",
    },
    {
        "name": "registerTargetPythonVersion",
        "func": mod_alogs.registerTargetPythonVersion,
        "registry_attr": "registered_internal_target_python_version",
        "valid_values": [(3, 10), (3, 11), (3, 12)],
        "kwarg_name": "version",
    },
]

ENV_VAR_SETTER = {
    "name": "registerLogLevelEnvVars",
    "func": mod_alogs.registerLogLevelEnvVars,
    "registry_attr": "registered_internal_log_level_env_vars",
    "valid_values": [
        [],
        ["SINGLE"],
        ["VAR1", "VAR2"],
        ["MYAPP_LOG_LEVEL", "LOG_LEVEL"],
    ],
    "kwarg_name": "env_vars",
}


# ============================================================================
# Parametrized Tests for Boolean/Simple Setters
# ============================================================================


@pytest.mark.parametrize("setter", REGISTRY_SETTERS[:-1])  # Exclude env_vars for now
def test_registry_setter_stores_value(setter: dict[str, Any]) -> None:
    """Registry setter should store the value provided."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = getattr(_registry, setter["registry_attr"])
    test_value = setter["valid_values"][0]

    try:
        # --- execute ---
        setter["func"](**{setter["kwarg_name"]: test_value})

        # --- verify ---
        assert getattr(_registry, setter["registry_attr"]) == test_value
    finally:
        # --- cleanup ---
        setattr(_registry, setter["registry_attr"], original_value)


@pytest.mark.parametrize("setter", REGISTRY_SETTERS[:-1])
def test_registry_setter_overwrites_previous(setter: dict[str, Any]) -> None:
    """Registry setter should overwrite previous value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = getattr(_registry, setter["registry_attr"])
    first_value = setter["valid_values"][0]
    second_value = setter["valid_values"][1 % len(setter["valid_values"])]

    try:
        setter["func"](**{setter["kwarg_name"]: first_value})

        # --- execute ---
        setter["func"](**{setter["kwarg_name"]: second_value})

        # --- verify ---
        assert getattr(_registry, setter["registry_attr"]) == second_value
    finally:
        # --- cleanup ---
        setattr(_registry, setter["registry_attr"], original_value)


@pytest.mark.parametrize("setter", REGISTRY_SETTERS[:-1])
def test_registry_setter_accepts_none(setter: dict[str, Any]) -> None:
    """Registry setter should accept None without changing value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = getattr(_registry, setter["registry_attr"])
    test_value = setter["valid_values"][0]

    try:
        # Set an initial value
        setter["func"](**{setter["kwarg_name"]: test_value})
        value_before_none = getattr(_registry, setter["registry_attr"])

        # --- execute ---
        setter["func"](**{setter["kwarg_name"]: None})

        # --- verify ---
        assert getattr(_registry, setter["registry_attr"]) == value_before_none
    finally:
        # --- cleanup ---
        setattr(_registry, setter["registry_attr"], original_value)


@pytest.mark.parametrize(
    ("setter", "value"),
    [
        (setter, value)
        for setter in REGISTRY_SETTERS[:-1]
        for value in setter["valid_values"]  # type: ignore[attr-defined]
    ],
)
def test_registry_setter_accepts_valid_values(
    setter: dict[str, Any], value: Any
) -> None:
    """Registry setter should accept all valid values."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = getattr(_registry, setter["registry_attr"])

    try:
        # --- execute ---
        setter["func"](**{setter["kwarg_name"]: value})

        # --- verify ---
        assert getattr(_registry, setter["registry_attr"]) == value
    finally:
        # --- cleanup ---
        setattr(_registry, setter["registry_attr"], original_value)


# ============================================================================
# Tests for registerLogLevelEnvVars (List Values)
# ============================================================================


def test_register_log_level_env_vars_stores_list() -> None:
    """registerLogLevelEnvVars() should store the list of env var names."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_log_level_env_vars
    env_vars = ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]

    try:
        # --- execute ---
        mod_alogs.registerLogLevelEnvVars(env_vars)

        # --- verify ---
        assert _registry.registered_internal_log_level_env_vars == env_vars
    finally:
        # --- cleanup ---
        _registry.registered_internal_log_level_env_vars = original_value


def test_register_log_level_env_vars_overwrites_previous() -> None:
    """registerLogLevelEnvVars() should overwrite previous value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_log_level_env_vars

    try:
        mod_alogs.registerLogLevelEnvVars(["OLD_VAR"])

        # --- execute ---
        new_vars = ["NEW_VAR1", "NEW_VAR2"]
        mod_alogs.registerLogLevelEnvVars(new_vars)

        # --- verify ---
        assert _registry.registered_internal_log_level_env_vars == new_vars
    finally:
        # --- cleanup ---
        _registry.registered_internal_log_level_env_vars = original_value


def test_register_log_level_env_vars_accepts_none() -> None:
    """registerLogLevelEnvVars() should accept None without changing value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_log_level_env_vars

    try:
        mod_alogs.registerLogLevelEnvVars(["OLD_VAR"])
        value_before_none = _registry.registered_internal_log_level_env_vars

        # --- execute ---
        mod_alogs.registerLogLevelEnvVars(None)

        # --- verify ---
        assert _registry.registered_internal_log_level_env_vars == value_before_none
    finally:
        # --- cleanup ---
        _registry.registered_internal_log_level_env_vars = original_value


@pytest.mark.parametrize(
    "env_vars",
    ENV_VAR_SETTER["valid_values"],  # type: ignore[arg-type]
)
def test_register_log_level_env_vars_accepts_valid_values(
    env_vars: list[str],
) -> None:
    """registerLogLevelEnvVars() should accept various list configurations."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_log_level_env_vars

    try:
        # --- execute ---
        mod_alogs.registerLogLevelEnvVars(env_vars)

        # --- verify ---
        assert _registry.registered_internal_log_level_env_vars == env_vars
    finally:
        # --- cleanup ---
        _registry.registered_internal_log_level_env_vars = original_value
