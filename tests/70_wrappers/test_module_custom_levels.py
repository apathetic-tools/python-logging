# tests/70_wrappers/test_module_custom_levels.py
"""Test module-level custom level convenience functions (trace, detail, brief)."""

from __future__ import annotations

import io
import sys
from typing import TYPE_CHECKING

import pytest  # noqa: TC002

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import (  # noqa: ICN003
        Logger,  # pyright: ignore[reportUnusedImport]
    )
else:
    Logger = mod_alogs.Logger


def test_module_custom_level_functions_exist() -> None:
    """Verify custom level module functions exist on apathetic_logging."""
    assert hasattr(mod_alogs, "trace"), (
        "Function trace should exist on apathetic_logging"
    )
    assert hasattr(mod_alogs, "detail"), (
        "Function detail should exist on apathetic_logging"
    )
    assert hasattr(mod_alogs, "brief"), (
        "Function brief should exist on apathetic_logging"
    )


def test_trace_logs_to_root_logger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that trace() logs to root logger at TRACE level."""
    # --- setup ---
    # Capture output
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # Get root logger and configure it
    root_logger = mod_alogs.getLogger("")
    root_logger.setLevel("TRACE")
    # Clear any existing handlers
    root_logger.handlers.clear()
    # Add a handler to capture output
    handler = mod_alogs.DualStreamHandler()
    root_logger.addHandler(handler)

    # --- execute ---
    mod_alogs.trace("test trace message")

    # --- verify ---
    output = err_buf.getvalue()
    assert "test trace message" in output
    # Tag might not be present if formatter isn't fully configured,
    # but message should be there. The important thing is that the
    # function works and logs at TRACE level


def test_detail_logs_to_root_logger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that detail() logs to root logger at DETAIL level."""
    # --- setup ---
    # Capture output
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # Get root logger and configure it
    root_logger = mod_alogs.getLogger("")
    root_logger.setLevel("DETAIL")
    # Clear any existing handlers
    root_logger.handlers.clear()
    # Add a handler to capture output
    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter())
    root_logger.addHandler(handler)

    # --- execute ---
    mod_alogs.detail("test detail message")

    # --- verify ---
    output = out_buf.getvalue()  # DETAIL goes to stdout like INFO
    assert "test detail message" in output


def test_brief_logs_to_root_logger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that brief() logs to root logger at BRIEF level."""
    # --- setup ---
    # Capture output
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # Get root logger and configure it
    root_logger = mod_alogs.getLogger("")
    root_logger.setLevel("BRIEF")
    # Clear any existing handlers
    root_logger.handlers.clear()
    # Add a handler to capture output
    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter())
    root_logger.addHandler(handler)

    # --- execute ---
    mod_alogs.brief("test brief message")

    # --- verify ---
    output = out_buf.getvalue()  # BRIEF goes to stdout like INFO
    assert "test brief message" in output


def test_trace_respects_log_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that trace() respects log level setting."""
    # --- setup ---
    # Capture output
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # Get root logger and configure it
    root_logger = mod_alogs.getLogger("")
    root_logger.setLevel("INFO")  # Set to INFO, so TRACE should not log
    # Clear any existing handlers
    root_logger.handlers.clear()
    # Add a handler to capture output
    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter())
    root_logger.addHandler(handler)

    # --- execute ---
    mod_alogs.trace("test trace message - should not appear")

    # --- verify ---
    output = err_buf.getvalue()
    assert "test trace message - should not appear" not in output


def test_detail_respects_log_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that detail() respects log level setting."""
    # --- setup ---
    # Capture output
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # Get root logger and configure it
    root_logger = mod_alogs.getLogger("")
    root_logger.setLevel("INFO")  # Set to INFO, so DETAIL should not log
    # Clear any existing handlers
    root_logger.handlers.clear()
    # Add a handler to capture output
    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter())
    root_logger.addHandler(handler)

    # --- execute ---
    mod_alogs.detail("test detail message - should not appear")

    # --- verify ---
    output = out_buf.getvalue()
    assert "test detail message - should not appear" not in output


def test_brief_respects_log_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that brief() respects log level setting."""
    # --- setup ---
    # Capture output
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # Get root logger and configure it
    root_logger = mod_alogs.getLogger("")
    root_logger.setLevel("WARNING")  # Set to WARNING, so BRIEF should not log
    # Clear any existing handlers
    root_logger.handlers.clear()
    # Add a handler to capture output
    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter())
    root_logger.addHandler(handler)

    # --- execute ---
    mod_alogs.brief("test brief message - should not appear")

    # --- verify ---
    output = out_buf.getvalue()
    assert "test brief message - should not appear" not in output


def test_custom_level_functions_work_with_format_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that custom level functions support format arguments."""
    # --- setup ---
    # Capture output
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # Get root logger and configure it
    root_logger = mod_alogs.getLogger("")
    root_logger.setLevel("TRACE")
    # Clear any existing handlers
    root_logger.handlers.clear()
    # Add a handler to capture output
    handler = mod_alogs.DualStreamHandler()
    root_logger.addHandler(handler)

    # --- execute ---
    mod_alogs.trace("test %s message with %d args", "trace", 2)
    mod_alogs.detail("test %s message with %d args", "detail", 2)
    mod_alogs.brief("test %s message with %d args", "brief", 2)

    # --- verify ---
    err_output = err_buf.getvalue()
    out_output = out_buf.getvalue()
    assert "test trace message with 2 args" in err_output
    assert "test detail message with 2 args" in out_output
    assert "test brief message with 2 args" in out_output
