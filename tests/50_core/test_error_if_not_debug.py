# tests/50_core/test_error_if_not_debug.py
"""Tests for Logger.errorIfNotDebug() method."""

import io
import sys
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


def test_error_if_not_debug_logs_error_when_not_debug(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """error_if_not_debug() should log error when debug is not enabled."""
    # --- setup ---
    direct_logger.setLevel("INFO")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    direct_logger.errorIfNotDebug("test error message")

    # --- verify ---
    output = err_buf.getvalue()
    assert "test error message" in output
    # Should not contain traceback (debug not enabled)
    assert "Traceback" not in output


def test_error_if_not_debug_logs_exception_when_debug_enabled(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """error_if_not_debug() should log exception when debug is enabled."""
    # --- setup ---
    direct_logger.setLevel("DEBUG")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    def _raise_value_error() -> None:
        exc_msg = "test exception"
        raise ValueError(exc_msg)

    try:
        _raise_value_error()
    except ValueError:
        direct_logger.errorIfNotDebug("test error with exception")

    # --- verify ---
    output = err_buf.getvalue()
    assert "test error with exception" in output
    # Should contain traceback (debug enabled)
    assert "Traceback" in output
    assert "ValueError" in output


def test_error_if_not_debug_with_custom_exc_info(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """error_if_not_debug() should respect exc_info parameter."""
    # --- setup ---
    direct_logger.setLevel("DEBUG")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    direct_logger.errorIfNotDebug("test error", exc_info=False)

    # --- verify ---
    output = err_buf.getvalue()
    assert "test error" in output
    # Should not contain traceback when exc_info=False
    assert "Traceback" not in output


def test_error_if_not_debug_with_args(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """error_if_not_debug() should handle format args."""
    # --- setup ---
    direct_logger.setLevel("INFO")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    direct_logger.errorIfNotDebug("test %s %d", "message", 42)

    # --- verify ---
    output = err_buf.getvalue()
    assert "test message 42" in output
