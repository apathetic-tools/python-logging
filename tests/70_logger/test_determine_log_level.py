# tests/50_core/test_determine_log_level.py
"""Tests for Logger.determine_log_level() method."""

import argparse
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


@pytest.fixture(autouse=True)
def reset_namespace_and_env(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None, None, None]:
    """Reset namespace shadow attributes and environment.

    Registry state is handled by the global fixture, but this handles:
    - Shadow attributes on namespace class (set directly on namespace)
    - Environment variables
    """
    _ns = mod_alogs.apathetic_logging

    # Also reset any shadow attributes on namespace class (in case a previous
    # test set them directly on the namespace class)
    # Check __dict__ directly to avoid MRO lookup
    if "registered_internal_log_level_env_vars" in _ns.__dict__:
        delattr(_ns, "registered_internal_log_level_env_vars")
    if "registered_internal_default_log_level" in _ns.__dict__:
        delattr(_ns, "registered_internal_default_log_level")

    # Clear environment variables
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("MYAPP_LOG_LEVEL", raising=False)

    return  # type: ignore[return-value]


def test_determine_log_level_from_args(
    direct_logger: Logger,
) -> None:
    """determine_log_level() should prioritize CLI args."""
    # --- setup ---
    args = argparse.Namespace(log_level="debug")

    # --- execute ---
    result = direct_logger.determineLogLevel(args=args)

    # --- verify ---
    assert result == "DEBUG"


def test_determine_log_level_from_registered_env_var(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """determine_log_level() should use registered env vars."""
    # --- setup ---
    mod_alogs.registerLogLevelEnvVars(["MYAPP_LOG_LEVEL"])
    monkeypatch.setenv("MYAPP_LOG_LEVEL", "warning")

    # --- execute ---
    result = direct_logger.determineLogLevel()

    # --- verify ---
    assert result == "WARNING"


def test_determine_log_level_from_default_env_var(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """determine_log_level() should fall back to default env var."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "error")

    # --- execute ---
    result = direct_logger.determineLogLevel()

    # --- verify ---
    assert result == "ERROR"


def test_determine_log_level_from_registered_env_vars_order(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """determine_log_level() should check env vars in order."""
    # --- setup ---
    mod_alogs.registerLogLevelEnvVars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])
    monkeypatch.setenv("MYAPP_LOG_LEVEL", "debug")
    monkeypatch.setenv("LOG_LEVEL", "error")

    # --- execute ---
    result = direct_logger.determineLogLevel()

    # --- verify ---
    # Should use first env var found (MYAPP_LOG_LEVEL)
    assert result == "DEBUG"


def test_determine_log_level_from_root_log_level(
    direct_logger: Logger,
) -> None:
    """determine_log_level() should use root_log_level when provided."""
    # --- execute ---
    result = direct_logger.determineLogLevel(root_log_level="info")

    # --- verify ---
    assert result == "INFO"


def test_determine_log_level_from_registered_default(
    direct_logger: Logger,
) -> None:
    """determine_log_level() should use registered default."""
    # --- setup ---
    mod_alogs.registerDefaultLogLevel("warning")

    # --- execute ---
    result = direct_logger.determineLogLevel()

    # --- verify ---
    assert result == "WARNING"


def test_determine_log_level_falls_back_to_module_default(
    direct_logger: Logger,
) -> None:
    """determine_log_level() should fall back to module default."""
    # --- execute ---
    result = direct_logger.determineLogLevel()

    # --- verify ---
    # Should use DEFAULT_APATHETIC_LOG_LEVEL which is "detail"
    assert result == "DETAIL"


def test_determine_log_level_args_override_all(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """determine_log_level() should prioritize CLI args over all other sources."""
    # --- setup ---
    mod_alogs.registerDefaultLogLevel("error")
    monkeypatch.setenv("LOG_LEVEL", "warning")
    args = argparse.Namespace(log_level="debug")

    # --- execute ---
    result = direct_logger.determineLogLevel(args=args, root_log_level="info")

    # --- verify ---
    assert result == "DEBUG"


def test_determine_log_level_env_overrides_root_and_default(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """determine_log_level() should prioritize env vars over root_log_level."""
    # --- setup ---
    mod_alogs.registerDefaultLogLevel("error")
    monkeypatch.setenv("LOG_LEVEL", "warning")

    # --- execute ---
    result = direct_logger.determineLogLevel(root_log_level="info")

    # --- verify ---
    assert result == "WARNING"


def test_determine_log_level_root_overrides_default(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """determine_log_level() should prioritize root_log_level over default."""
    # --- setup ---
    mod_alogs.registerDefaultLogLevel("error")
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    # --- execute ---
    result = direct_logger.determineLogLevel(root_log_level="info")

    # --- verify ---
    assert result == "INFO"
