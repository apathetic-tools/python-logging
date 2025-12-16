# tests/30_independant/test_is_safe_trace_enabled.py
"""Tests for isSafeTraceEnabled method.

This test uses parametrization to consolidate many similar test cases
into a single parametrized test.
"""

from collections.abc import Generator

import pytest

import apathetic_logging.constants as mod_constants
import apathetic_logging.safe_logging as mod_safe_logging


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Reset environment variables before and after each test."""
    monkeypatch.delenv("SAFE_TRACE", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    yield
    monkeypatch.delenv("SAFE_TRACE", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)


@pytest.mark.parametrize(
    ("env_var", "env_value", "expected"),
    [
        # SAFE_TRACE env var cases
        ("SAFE_TRACE", "true", True),
        ("SAFE_TRACE", "1", True),
        ("SAFE_TRACE", "yes", True),
        # LOG_LEVEL=TRACE cases
        ("LOG_LEVEL", "TRACE", True),
        ("LOG_LEVEL", "trace", True),
        ("LOG_LEVEL", "TEST", True),
        # LOG_LEVEL numeric cases
        pytest.param(
            "LOG_LEVEL",
            "trace_level_at",
            True,
            id="log_level_numeric_at_trace_level",
        ),
        pytest.param(
            "LOG_LEVEL",
            "trace_level_below",
            True,
            id="log_level_numeric_below_trace_level",
        ),
        pytest.param(
            "LOG_LEVEL",
            "trace_level_above",
            False,
            id="log_level_numeric_above_trace_level",
        ),
        # LOG_LEVEL above TRACE cases
        ("LOG_LEVEL", "DEBUG", False),
        ("LOG_LEVEL", "INFO", False),
        # Edge case: empty LOG_LEVEL
        ("LOG_LEVEL", "", False),
    ],
)
def test_is_safe_trace_enabled_with_env_vars(
    monkeypatch: pytest.MonkeyPatch,
    env_var: str,
    env_value: str,
    expected: bool,  # noqa: FBT001
) -> None:
    """isSafeTraceEnabled() should correctly handle various env var values."""
    # --- setup ---
    trace_level = mod_constants.ApatheticLogging_Internal_Constants.TRACE_LEVEL

    # Handle special markers for numeric trace level tests
    if env_value == "trace_level_at":
        env_value = str(trace_level)
    elif env_value == "trace_level_below":
        env_value = str(trace_level - 1)
    elif env_value == "trace_level_above":
        env_value = str(trace_level + 1)

    monkeypatch.setenv(env_var, env_value)
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is expected


def test_is_safe_trace_enabled_with_no_env_vars() -> None:
    """isSafeTraceEnabled() should return False when no env vars are set."""
    # --- setup ---
    # Fixture already clears all env vars
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is False
