# tests/5_core/test_dual_stream_handler.py
"""Tests for DualStreamHandler class."""

import io
import logging
import sys

import pytest

import apathetic_logging as mod_alogs


def test_dual_stream_handler_info_goes_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route INFO level to stdout."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    logger = logging.getLogger("test_stdout")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    logger.info("test info message")

    # --- verify ---
    assert "test info message" in out_buf.getvalue()
    assert "test info message" not in err_buf.getvalue()


def test_dual_stream_handler_debug_goes_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route DEBUG level to stdout."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    logger = logging.getLogger("test_debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    logger.debug("test debug message")

    # --- verify ---
    assert "test debug message" in out_buf.getvalue()
    assert "test debug message" not in err_buf.getvalue()


def test_dual_stream_handler_warning_goes_to_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route WARNING level to stderr."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    logger = logging.getLogger("test_warning")
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    logger.warning("test warning message")

    # --- verify ---
    assert "test warning message" not in out_buf.getvalue()
    assert "test warning message" in err_buf.getvalue()


def test_dual_stream_handler_error_goes_to_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route ERROR level to stderr."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    logger = logging.getLogger("test_error")
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    logger.error("test error message")

    # --- verify ---
    assert "test error message" not in out_buf.getvalue()
    assert "test error message" in err_buf.getvalue()


def test_dual_stream_handler_critical_goes_to_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route CRITICAL level to stderr."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    logger = logging.getLogger("test_critical")
    logger.setLevel(logging.CRITICAL)
    logger.addHandler(handler)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    logger.critical("test critical message")

    # --- verify ---
    assert "test critical message" not in out_buf.getvalue()
    assert "test critical message" in err_buf.getvalue()


def test_dual_stream_handler_has_enable_color_attribute() -> None:
    """DualStreamHandler should have enable_color attribute."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()

    # --- verify ---
    # Should have enable_color attribute (defaults to False)
    assert hasattr(handler, "enable_color")
    assert handler.enable_color is False

    # --- execute ---
    handler.enable_color = True

    # --- verify ---
    assert handler.enable_color is True
