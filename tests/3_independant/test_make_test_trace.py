# tests/3_independant/test_make_test_trace.py
"""Tests for make_test_trace function."""

import sys
from io import StringIO

import pytest

import apathetic_logging as mod_alogs
from apathetic_logging.constants import (
    ApatheticLogging_Priv_Constants,  # pyright: ignore[reportPrivateUsage]
)


@pytest.fixture(autouse=True)
def reset_test_trace_enabled() -> None:
    """Reset TEST_TRACE_ENABLED before and after each test."""
    original = ApatheticLogging_Priv_Constants.TEST_TRACE_ENABLED
    yield
    ApatheticLogging_Priv_Constants.TEST_TRACE_ENABLED = original


def test_make_test_trace_returns_callable() -> None:
    """make_test_trace() should return a callable function."""
    # --- execute ---
    trace_func = mod_alogs.make_test_trace()

    # --- verify ---
    assert callable(trace_func)


def test_make_test_trace_custom_icon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_test_trace() should use custom icon when provided."""
    # --- setup ---
    custom_icon = "🔍"
    trace_func = mod_alogs.make_test_trace(icon=custom_icon)
    ApatheticLogging_Priv_Constants.TEST_TRACE_ENABLED = True
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test message")

    # --- verify ---
    output = buf.getvalue()
    assert custom_icon in output


def test_make_test_trace_default_icon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_test_trace() should use default icon when not provided."""
    # --- setup ---
    trace_func = mod_alogs.make_test_trace()
    ApatheticLogging_Priv_Constants.TEST_TRACE_ENABLED = True
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test message")

    # --- verify ---
    output = buf.getvalue()
    assert "🧪" in output


def test_make_test_trace_respects_test_trace_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_test_trace() should not output when TEST_TRACE is disabled."""
    # --- setup ---
    trace_func = mod_alogs.make_test_trace()
    ApatheticLogging_Priv_Constants.TEST_TRACE_ENABLED = False
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test message")

    # --- verify ---
    output = buf.getvalue()
    assert output == ""


def test_make_test_trace_outputs_to_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """make_test_trace() should write to sys.__stderr__."""
    # --- setup ---
    trace_func = mod_alogs.make_test_trace()
    ApatheticLogging_Priv_Constants.TEST_TRACE_ENABLED = True
    buf = StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "__stderr__", buf)
    trace_func("test label", "arg1", "arg2")

    # --- verify ---
    output = buf.getvalue()
    assert "test label" in output
    assert "arg1" in output
    assert "arg2" in output
