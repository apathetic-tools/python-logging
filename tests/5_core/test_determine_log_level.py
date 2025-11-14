# tests/5_core/test_determine_log_level.py
"""Tests for Logger.determine_log_level() method."""

import argparse

import pytest

import apathetic_logging as mod_alogs
from apathetic_logging.registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)


@pytest.fixture(autouse=True)
def reset_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset registry state and environment before and after each test."""
    # Save original values
    original_env_vars = (
        ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars
    )
    original_default = ApatheticLogging_Priv_Registry.registered_priv_default_log_level

    # Reset to None
    ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars = None
    ApatheticLogging_Priv_Registry.registered_priv_default_log_level = None

    # Clear environment variables
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("MYAPP_LOG_LEVEL", raising=False)

    yield

    # Restore original values
    ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars = (
        original_env_vars
    )
    ApatheticLogging_Priv_Registry.registered_priv_default_log_level = original_default


def test_determine_log_level_from_args(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should prioritize CLI args."""
    # --- setup ---
    args = argparse.Namespace(log_level="debug")

    # --- execute ---
    result = direct_logger.determine_log_level(args=args)

    # --- verify ---
    assert result == "DEBUG"


def test_determine_log_level_from_registered_env_var(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should use registered env vars."""
    # --- setup ---
    mod_alogs.register_log_level_env_vars(["MYAPP_LOG_LEVEL"])
    monkeypatch.setenv("MYAPP_LOG_LEVEL", "warning")

    # --- execute ---
    result = direct_logger.determine_log_level()

    # --- verify ---
    assert result == "WARNING"


def test_determine_log_level_from_default_env_var(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should fall back to default env var."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "error")

    # --- execute ---
    result = direct_logger.determine_log_level()

    # --- verify ---
    assert result == "ERROR"


def test_determine_log_level_from_registered_env_vars_order(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should check env vars in order."""
    # --- setup ---
    mod_alogs.register_log_level_env_vars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])
    monkeypatch.setenv("MYAPP_LOG_LEVEL", "debug")
    monkeypatch.setenv("LOG_LEVEL", "error")

    # --- execute ---
    result = direct_logger.determine_log_level()

    # --- verify ---
    # Should use first env var found (MYAPP_LOG_LEVEL)
    assert result == "DEBUG"


def test_determine_log_level_from_root_log_level(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should use root_log_level when provided."""
    # --- execute ---
    result = direct_logger.determine_log_level(root_log_level="info")

    # --- verify ---
    assert result == "INFO"


def test_determine_log_level_from_registered_default(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should use registered default."""
    # --- setup ---
    mod_alogs.register_default_log_level("warning")

    # --- execute ---
    result = direct_logger.determine_log_level()

    # --- verify ---
    assert result == "WARNING"


def test_determine_log_level_falls_back_to_module_default(
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should fall back to module default."""
    # --- execute ---
    result = direct_logger.determine_log_level()

    # --- verify ---
    # Should use DEFAULT_APATHETIC_LOG_LEVEL which is "info"
    assert result == "INFO"


def test_determine_log_level_priority_order(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: mod_alogs.ApatheticLogging.Logger,
) -> None:
    """determine_log_level() should respect priority: args > env > root > default."""
    # --- setup ---
    mod_alogs.register_default_log_level("error")
    monkeypatch.setenv("LOG_LEVEL", "warning")
    args = argparse.Namespace(log_level="debug")

    # --- execute ---
    result = direct_logger.determine_log_level(args=args, root_log_level="info")

    # --- verify ---
    # Args should win
    assert result == "DEBUG"

    # --- setup: test env over root ---
    # --- execute ---
    result = direct_logger.determine_log_level(root_log_level="info")

    # --- verify ---
    # Env should win over root
    assert result == "WARNING"

    # --- setup: test root over default ---
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    # --- execute ---
    result = direct_logger.determine_log_level(root_log_level="info")

    # --- verify ---
    # Root should win over default
    assert result == "INFO"
