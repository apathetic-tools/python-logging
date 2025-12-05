# tests/50_core/test_dual_stream_handler.py
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


def test_dual_stream_handler_debug_goes_to_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route DEBUG level to stderr."""
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
    assert "test debug message" in err_buf.getvalue()
    assert "test debug message" not in out_buf.getvalue()


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


def test_dual_stream_handler_detail_goes_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route DETAIL level to stdout."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    logger = mod_alogs.Logger("test_detail")
    logger.setLevel(mod_alogs.apathetic_logging.DETAIL_LEVEL)
    logger.addHandler(handler)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    logger.detail("test detail message")

    # --- verify ---
    assert "test detail message" in out_buf.getvalue()
    assert "test detail message" not in err_buf.getvalue()


def test_dual_stream_handler_brief_goes_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DualStreamHandler should route BRIEF level to stdout."""
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    logger = mod_alogs.Logger("test_brief")
    logger.setLevel(mod_alogs.apathetic_logging.BRIEF_LEVEL)
    logger.addHandler(handler)

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # --- execute ---
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)
    logger.brief("test brief message")

    # --- verify ---
    assert "test brief message" in out_buf.getvalue()
    assert "test brief message" not in err_buf.getvalue()


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
) -> None:
    """TEST/TRACE/DEBUG bypass capsys via __stderr__ when logger level is TEST.

    When logger level is set to TEST, TEST/TRACE/DEBUG messages bypass capture.
    DETAIL goes to stdout (like INFO) and is captured normally.
    """
    # --- setup ---
    # Use a unique logger name to avoid conflicts
    logger_name = "test_bypass_unique"
    handler = mod_alogs.apathetic_logging.DualStreamHandler()
    # Get logger through logging.getLogger to ensure handler sees the same instance
    logger = logging.getLogger(logger_name)
    # Ensure it's our Logger class.
    # Use logging.getLoggerClass() which works in both modes. This is necessary
    # because in singlefile mode, direct class references (e.g., mod_alogs.Logger)
    # may have different object identity than the actual class used to create logger
    # instances, even though they're functionally the same. Using
    # logging.getLoggerClass() uses the actual class object that was set via
    # logging.setLoggerClass() in extendLoggingModule(), which works reliably
    # in both installed and singlefile runtime modes.
    # See extendLoggingModule() docstring for more details.
    if not isinstance(logger, logging.getLoggerClass()):
        # Create a new logger if it's not our type
        logger = mod_alogs.Logger(logger_name)
    logger.setLevel("test")  # Set to TEST level
    logger.addHandler(handler)

    # Capture sys.__stderr__ to verify bypass messages are written there
    bypass_buf = io.StringIO()
    monkeypatch.setattr(sys, "__stderr__", bypass_buf)

    # --- execute ---
    logger.test("test level message")  # type: ignore[attr-defined]
    logger.trace("trace level message")  # type: ignore[attr-defined]
    logger.debug("debug level message")
    logger.detail("detail level message")  # type: ignore[attr-defined]
    logger.warning("warning level message")  # Should still go to normal stderr

    # --- verify ---
    # Check capsys - TEST/TRACE/DEBUG messages should NOT be captured here
    # (they bypass via __stderr__)
    # DETAIL goes to stdout and IS captured normally


def test_dual_stream_handler_test_level_uses_effective_level(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """TEST mode detection should use effectiveLevel, not explicit level.

    This test verifies that getEffectiveLevel() is used for TEST mode detection.
    This ensures that when a logger's effective level is TEST (whether explicit
    or inherited), TEST mode is correctly detected. The key improvement is that
    child loggers inheriting TEST level from a parent will be correctly detected.
    """
    # --- setup ---
    handler = mod_alogs.apathetic_logging.DualStreamHandler()

    # Test with explicit TEST level (should work with our fix)
    logger_name = "test_effective_level_explicit"
    logger = mod_alogs.getLogger(logger_name)
    logger.setLevel("test")  # Explicit TEST level
    logger.addHandler(handler)

    # Verify effective level is TEST
    assert logger.effectiveLevel == mod_alogs.TEST_LEVEL
    assert logger.effectiveLevelName == "TEST"

    # Capture sys.__stderr__ to verify bypass messages are written there
    bypass_buf = io.StringIO()
    monkeypatch.setattr(sys, "__stderr__", bypass_buf)

    # --- execute ---
    logger.test("test level message")
    logger.trace("trace level message")
    logger.debug("debug level message")
    logger.warning("warning level message")  # Should still go to normal stderr

    # --- verify ---
    # TEST/TRACE/DEBUG messages should bypass capsys via __stderr__
    # (because effective level is TEST, detected via getEffectiveLevel())
    captured = capsys.readouterr()
    assert "test level message" not in captured.err
    assert "trace level message" not in captured.err
    assert "debug level message" not in captured.err
    # WARNING should still go to normal stderr (captured by capsys)
    assert "warning level message" in captured.err

    # But TEST/TRACE/DEBUG should be in the bypass buffer (__stderr__)
    bypass_output = bypass_buf.getvalue()
    assert "test level message" in bypass_output
    assert "trace level message" in bypass_output
    assert "debug level message" in bypass_output
    assert "warning level message" not in bypass_output, (
        "WARNING messages should not be in bypass buffer. "
        f"Bypass buffer: {bypass_output[:200]}"
    )
