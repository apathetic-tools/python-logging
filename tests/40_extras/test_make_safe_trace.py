# tests/30_independant/test_make_safe_trace.py
"""Tests for make_safe_trace function."""

import sys
from collections.abc import Generator
from io import StringIO

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.safe_logging as mod_safe_logging


@pytest.fixture(autouse=True)
def reset_safe_trace_enabled() -> Generator[None, None, None]:
    """Reset SAFE_TRACE_ENABLED before and after each test."""
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging
    original = _safe_logging.SAFE_TRACE_ENABLED
    yield
    _safe_logging.SAFE_TRACE_ENABLED = original


def test_make_safe_trace_returns_callable() -> None:
    """make_safe_trace() should return a callable function."""
    # --- execute ---
    trace_func = mod_alogs.makeSafeTrace()

    # --- verify ---
    assert callable(trace_func)


def test_make_safe_trace_custom_icon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_safe_trace() should use custom icon when provided."""
    # --- setup ---
    custom_icon = "🔍"
    trace_func = mod_alogs.makeSafeTrace(icon=custom_icon)
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging
    _safe_logging.SAFE_TRACE_ENABLED = True
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test message")

    # --- verify ---
    output = buf.getvalue()
    assert custom_icon in output


def test_make_safe_trace_default_icon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_safe_trace() should use default icon when not provided."""
    # --- setup ---
    trace_func = mod_alogs.makeSafeTrace()
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging
    _safe_logging.SAFE_TRACE_ENABLED = True
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test message")

    # --- verify ---
    output = buf.getvalue()
    assert "🧪" in output


def test_make_safe_trace_respects_safe_trace_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_safe_trace() should not output when safe_trace is disabled."""
    # --- setup ---
    trace_func = mod_alogs.makeSafeTrace()
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging
    _safe_logging.SAFE_TRACE_ENABLED = False
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test message")

    # --- verify ---
    output = buf.getvalue()
    assert output == ""


def test_make_safe_trace_outputs_to_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_safe_trace() should write to sys.__stderr__."""
    # --- setup ---
    trace_func = mod_alogs.makeSafeTrace()
    _safe_logging = mod_safe_logging.ApatheticLogging_Internal_SafeLogging
    _safe_logging.SAFE_TRACE_ENABLED = True
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test label", "arg1", "arg2")

    # --- verify ---
    output = buf.getvalue()
    assert "test label" in output
    assert "arg1" in output
    assert "arg2" in output
