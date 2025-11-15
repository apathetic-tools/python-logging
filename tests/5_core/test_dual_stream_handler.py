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


def test_dual_stream_handler_test_level_bypasses_capture(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """TEST level bypasses capsys via __stderr__ for TRACE/DEBUG/TEST messages."""
    # --- setup ---
    # Use a unique logger name to avoid conflicts
    logger_name = "test_bypass_unique"
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    # Get logger through logging.getLogger to ensure handler sees the same instance
    logger = logging.getLogger(logger_name)
    # Ensure it's our Logger class
    if not isinstance(logger, mod_alogs.Logger):
        # Create a new logger if it's not our type
        logger = mod_alogs.Logger(logger_name)
    logger.setLevel("test")  # Set to TEST level
    logger.addHandler(handler)

    # Capture sys.__stderr__ to verify bypass messages are written there
    bypass_buf = io.StringIO()
    monkeypatch.setattr(sys, "__stderr__", bypass_buf)

    # --- execute ---
    logger.test("test level message")
    logger.trace("trace level message")
    logger.debug("debug level message")
    logger.warning("warning level message")  # Should still go to normal stderr

    # --- verify ---
    # Check capsys - TRACE/DEBUG/TEST messages should NOT be captured here
    captured = capsys.readouterr()
    out = captured.out.lower()
    err = captured.err.lower()

    # Check bypass buffer - TRACE/DEBUG/TEST messages SHOULD be written here
    bypass_output = bypass_buf.getvalue().lower()

    # Verify TRACE/DEBUG/TEST messages are NOT in capsys (they bypass capture)
    assert "[test" not in out, (
        "TEST messages should bypass capsys and write to sys.__stderr__ instead. "
        f"Found in capsys.out: {out[:200]}"
    )
    assert "[trace" not in out, (
        "TRACE messages should bypass capsys and write to sys.__stderr__ instead. "
        f"Found in capsys.out: {out[:200]}"
    )
    assert "[debug" not in out, (
        "DEBUG messages should bypass capsys and write to sys.__stderr__ instead. "
        f"Found in capsys.out: {out[:200]}"
    )
    assert "[test" not in err, (
        "TEST messages should bypass capsys and write to sys.__stderr__ instead. "
        f"Found in capsys.err: {err[:200]}"
    )
    assert "[trace" not in err, (
        "TRACE messages should bypass capsys and write to sys.__stderr__ instead. "
        f"Found in capsys.err: {err[:200]}"
    )
    assert "[debug" not in err, (
        "DEBUG messages should bypass capsys and write to sys.__stderr__ instead. "
        f"Found in capsys.err: {err[:200]}"
    )

    # Verify TRACE/DEBUG/TEST messages ARE in the bypass buffer (sys.__stderr__)
    assert "test level message" in bypass_output, (
        "TEST messages should appear in sys.__stderr__ bypass buffer. "
        f"Bypass buffer length: {len(bypass_output)} chars"
    )
    assert "trace level message" in bypass_output, (
        "TRACE messages should appear in sys.__stderr__ bypass buffer. "
        f"Bypass buffer length: {len(bypass_output)} chars"
    )
    assert "debug level message" in bypass_output, (
        "DEBUG messages should appear in sys.__stderr__ bypass buffer. "
        f"Bypass buffer length: {len(bypass_output)} chars"
    )

    # Verify WARNING still goes to normal stderr (not bypassed)
    assert "warning level message" in err, (
        "WARNING messages should still go to normal stderr, not bypassed. "
        f"Found in capsys.err: {err[:200]}"
    )
    assert "warning level message" not in bypass_output, (
        "WARNING messages should not be in bypass buffer. "
        f"Bypass buffer: {bypass_output[:200]}"
    )
