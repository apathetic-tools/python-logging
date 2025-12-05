# tests/30_independant/test_is_safe_trace_enabled.py
"""Tests for isSafeTraceEnabled method."""

from collections.abc import Generator

import pytest

import apathetic_logging.constants as mod_constants
import apathetic_logging.safe_logging as mod_safe_logging


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Reset environment variables before and after each test."""
    # Clear both env vars before test
    monkeypatch.delenv("SAFE_TRACE", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    yield
    # Clean up after test
    monkeypatch.delenv("SAFE_TRACE", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)


def test_is_safe_trace_enabled_with_safe_trace_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return True when SAFE_TRACE=true."""
    # --- setup ---
    monkeypatch.setenv("SAFE_TRACE", "true")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_safe_trace_1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return True when SAFE_TRACE=1."""
    # --- setup ---
    monkeypatch.setenv("SAFE_TRACE", "1")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_safe_trace_yes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return True when SAFE_TRACE=yes."""
    # --- setup ---
    monkeypatch.setenv("SAFE_TRACE", "yes")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_log_level_trace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return True when LOG_LEVEL=TRACE."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_log_level_trace_lowercase(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() returns True when LOG_LEVEL=trace (case insensitive)."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "trace")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_log_level_test(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return True when LOG_LEVEL=TEST."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "TEST")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_log_level_numeric_at_trace_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() returns True when LOG_LEVEL equals TRACE_LEVEL."""
    # --- setup ---
    trace_level = mod_constants.ApatheticLogging_Internal_Constants.TRACE_LEVEL
    monkeypatch.setenv("LOG_LEVEL", str(trace_level))
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_log_level_numeric_below_trace_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() returns True when LOG_LEVEL < TRACE_LEVEL."""
    # --- setup ---
    trace_level = mod_constants.ApatheticLogging_Internal_Constants.TRACE_LEVEL
    monkeypatch.setenv("LOG_LEVEL", str(trace_level - 1))
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is True


def test_is_safe_trace_enabled_with_log_level_numeric_above_trace_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() returns False when LOG_LEVEL > TRACE_LEVEL."""
    # --- setup ---
    trace_level = mod_constants.ApatheticLogging_Internal_Constants.TRACE_LEVEL
    monkeypatch.setenv("LOG_LEVEL", str(trace_level + 1))
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is False


def test_is_safe_trace_enabled_with_log_level_debug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return False when LOG_LEVEL=DEBUG (above TRACE)."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is False


def test_is_safe_trace_enabled_with_log_level_info(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return False when LOG_LEVEL=INFO (above TRACE)."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is False


def test_is_safe_trace_enabled_with_no_env_vars() -> None:
    """isSafeTraceEnabled() should return False when no env vars are set."""
    # --- setup ---
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is False


def test_is_safe_trace_enabled_with_empty_log_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """isSafeTraceEnabled() should return False when LOG_LEVEL is empty."""
    # --- setup ---
    monkeypatch.setenv("LOG_LEVEL", "")
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging

    # --- execute ---
    result = _safe_logging.isSafeTraceEnabled()

    # --- verify ---
    assert result is False
