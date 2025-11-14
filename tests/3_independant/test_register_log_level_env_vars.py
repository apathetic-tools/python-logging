# tests/3_independant/test_register_log_level_env_vars.py
"""Tests for register_log_level_env_vars function."""

import pytest

import apathetic_logging as mod_alogs
from apathetic_logging.registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)


@pytest.fixture(autouse=True)
def reset_registry() -> None:
    """Reset registry state before and after each test."""
    # Save original values
    original_env_vars = (
        ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars
    )
    original_default = ApatheticLogging_Priv_Registry.registered_priv_default_log_level
    original_name = ApatheticLogging_Priv_Registry.registered_priv_logger_name

    # Reset to None
    ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars = None
    ApatheticLogging_Priv_Registry.registered_priv_default_log_level = None
    ApatheticLogging_Priv_Registry.registered_priv_logger_name = None

    yield

    # Restore original values
    ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars = (
        original_env_vars
    )
    ApatheticLogging_Priv_Registry.registered_priv_default_log_level = original_default
    ApatheticLogging_Priv_Registry.registered_priv_logger_name = original_name


def test_register_log_level_env_vars_stores_list() -> None:
    """register_log_level_env_vars() should store the list of env var names."""
    # --- setup ---
    env_vars = ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]

    # --- execute ---
    mod_alogs.register_log_level_env_vars(env_vars)

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars == env_vars


def test_register_log_level_env_vars_overwrites_previous() -> None:
    """register_log_level_env_vars() should overwrite previous value."""
    # --- setup ---
    mod_alogs.register_log_level_env_vars(["OLD_VAR"])

    # --- execute ---
    new_vars = ["NEW_VAR1", "NEW_VAR2"]
    mod_alogs.register_log_level_env_vars(new_vars)

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars == new_vars


def test_register_log_level_env_vars_empty_list() -> None:
    """register_log_level_env_vars() should accept empty list."""
    # --- execute ---
    mod_alogs.register_log_level_env_vars([])

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars == []


def test_register_log_level_env_vars_single_var() -> None:
    """register_log_level_env_vars() should accept single env var."""
    # --- setup ---
    env_vars = ["SINGLE_VAR"]

    # --- execute ---
    mod_alogs.register_log_level_env_vars(env_vars)

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars == env_vars
