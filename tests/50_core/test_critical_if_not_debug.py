# tests/50_core/test_critical_if_not_debug.py
"""Tests for Logger.criticalIfNotDebug() method."""

import io
import sys
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


def test_critical_if_not_debug_logs_critical_when_not_debug(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """critical_if_not_debug() should log critical when debug is not enabled."""
    # --- setup ---
    direct_logger.setLevel("INFO")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    direct_logger.criticalIfNotDebug("test critical message")

    # --- verify ---
    output = err_buf.getvalue()
    assert "test critical message" in output
    # Should not contain traceback (debug not enabled)
    assert "Traceback" not in output


def test_critical_if_not_debug_logs_exception_when_debug_enabled(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """critical_if_not_debug() should log exception when debug is enabled."""
    # --- setup ---
    direct_logger.setLevel("DEBUG")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    def _raise_runtime_error() -> None:
        exc_msg = "test exception"
        raise RuntimeError(exc_msg)

    try:
        _raise_runtime_error()
    except RuntimeError:
        direct_logger.criticalIfNotDebug("test critical with exception")

    # --- verify ---
    output = err_buf.getvalue()
    assert "test critical with exception" in output
    # Should contain traceback (debug enabled)
    assert "Traceback" in output
    assert "RuntimeError" in output


def test_critical_if_not_debug_with_custom_exc_info(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """critical_if_not_debug() should respect exc_info parameter."""
    # --- setup ---
    direct_logger.setLevel("DEBUG")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    direct_logger.criticalIfNotDebug("test critical", exc_info=False)

    # --- verify ---
    output = err_buf.getvalue()
    assert "test critical" in output
    # Should not contain traceback when exc_info=False
    assert "Traceback" not in output


def test_critical_if_not_debug_with_args(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """critical_if_not_debug() should handle format args."""
    # --- setup ---
    direct_logger.setLevel("INFO")
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    direct_logger.criticalIfNotDebug("test %s %d", "critical", 99)

    # --- verify ---
    output = err_buf.getvalue()
    assert "test critical 99" in output
