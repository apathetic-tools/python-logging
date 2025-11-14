# tests/3_independant/test_register_default_log_level.py
"""Tests for register_default_log_level function."""

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


def test_register_default_log_level_stores_value() -> None:
    """register_default_log_level() should store the default log level."""
    # --- setup ---
    default_level = "warning"

    # --- execute ---
    mod_alogs.register_default_log_level(default_level)

    # --- verify ---
    assert (
        ApatheticLogging_Priv_Registry.registered_priv_default_log_level
        == default_level
    )


def test_register_default_log_level_overwrites_previous() -> None:
    """register_default_log_level() should overwrite previous value."""
    # --- setup ---
    mod_alogs.register_default_log_level("info")

    # --- execute ---
    mod_alogs.register_default_log_level("debug")

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_default_log_level == "debug"


@pytest.mark.parametrize("level", ["trace", "debug", "info", "warning", "error"])
def test_register_default_log_level_accepts_valid_levels(level: str) -> None:
    """register_default_log_level() should accept various log levels."""
    # --- execute ---
    mod_alogs.register_default_log_level(level)

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_default_log_level == level
