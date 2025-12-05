# tests/50_core/test_logger.py

import io
import logging
import re
import sys
from typing import TYPE_CHECKING, Any

import pytest

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences for color safety."""
    return ANSI_PATTERN.sub("", s)


def capture_log_output(
    monkeypatch: pytest.MonkeyPatch,
    logger: Logger,
    msg_level: str,
    *,
    msg: str | None = None,
    enable_color: bool = False,
    log_level: str = "TRACE",
    **kwargs: Any,
) -> tuple[str, str]:
    """Temporarily capture stdout/stderr during a log() call.

    Returns (stdout_text, stderr_text) as plain strings.
    Automatically restores sys.stdout/sys.stderr afterwards.
    """
    logger.enable_color = enable_color
    logger.setLevel(log_level.upper())

    # Preserve original streams for proper restoration
    old_out, old_err = sys.stdout, sys.stderr

    # --- capture output temporarily ---
    out_buf, err_buf = io.StringIO(), io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    # --- execute ---
    try:
        method = getattr(logger, msg_level.lower(), None)
        if callable(method):
            final_msg: str = msg or f"msg:{msg_level}"
            method(final_msg, **kwargs)
    finally:
        # Always restore, even if log() crashes
        monkeypatch.setattr(sys, "stdout", old_out)
        monkeypatch.setattr(sys, "stderr", old_err)

    # --- return captured text ---
    return out_buf.getvalue(), err_buf.getvalue()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("msg_level", "expected_stream"),
    [
        ("debug", "stderr"),
        ("detail", "stdout"),
        ("info", "stdout"),
        ("brief", "stdout"),
        ("warning", "stderr"),
        ("error", "stderr"),
        ("critical", "stderr"),
        ("trace", "stderr"),
    ],
)
def test_log_routes_correct_stream(
    monkeypatch: pytest.MonkeyPatch,
    msg_level: str,
    expected_stream: str,
    direct_logger: Logger,
) -> None:
    """Ensure messages go to the correct stream based on severity."""
    # --- setup, patch, and execute ---
    text = f"msg:{msg_level}"
    out, err = capture_log_output(monkeypatch, direct_logger, msg_level, msg=text)
    out, err = strip_ansi(out.strip()), strip_ansi(err.strip())

    # --- verify ---
    combined = out or err
    assert text in combined  # message always present

    if expected_stream == "stdout":
        assert out  # message goes to stdout
        assert not err
    else:
        assert err  # message goes to stderr
        assert not out


def test_formatter_includes_expected_tags(
    capsys: pytest.CaptureFixture[str],
    direct_logger: Logger,
) -> None:
    """Each log level should include its corresponding prefix/tag."""
    # --- setup ---
    direct_logger.setLevel("test")  # most verbose to see all levels

    # --- execute, and verify ---
    for level_name, (_, expected_tag) in mod_alogs.apathetic_logging.TAG_STYLES.items():
        # Skip TEST level - it bypasses capture so won't appear in capsys
        if level_name == "TEST":
            continue
        method = getattr(direct_logger, level_name.lower(), None)
        if callable(method):
            method("sample")
            capture = capsys.readouterr()
            out = (capture.out + capture.err).lower()
            assert expected_tag.strip().lower() in out, (
                f"{level_name} missing expected tag"
            )


def test_formatter_adds_ansi_when_color_enabled(
    monkeypatch: pytest.MonkeyPatch,
    direct_logger: Logger,
) -> None:
    """When color is enabled, ANSI codes should appear in output."""
    # --- patch and execute ---
    _out, err = capture_log_output(
        monkeypatch, direct_logger, "debug", enable_color=True, msg="colored"
    )

    # --- verify ---
    # DEBUG messages go to stderr, not stdout
    assert "\033[" in err


def test_log_dynamic_unknown_level(
    capsys: pytest.CaptureFixture[str],
    direct_logger: Logger,
) -> None:
    """Unknown string levels are handled gracefully."""
    # --- execute ---
    direct_logger.logDynamic("nonsense", "This should not crash")

    # --- verify ---
    out = capsys.readouterr().err.lower()
    assert "Unknown log level".lower() in out


def test_use_level_context_manager_changes_temporarily(
    direct_logger: Logger,
) -> None:
    """use_level() should temporarily change the logger level."""
    # --- setup ---
    orig_level = direct_logger.level

    # --- execute and verify ---
    with direct_logger.useLevel("error"):
        assert direct_logger.levelName == "ERROR"
    assert direct_logger.level == orig_level


def test_use_level_minimum_prevents_downgrade(
    direct_logger: Logger,
) -> None:
    """use_level(minimum=True) should not downgrade from more verbose levels."""
    # --- setup ---
    direct_logger.setLevel("TRACE")
    orig_level = direct_logger.level
    assert direct_logger.levelName == "TRACE"

    # --- execute and verify: TRACE should not downgrade to DEBUG ---
    with direct_logger.useLevel("DEBUG", minimum=True):
        # Should stay at TRACE (more verbose than DEBUG)
        assert direct_logger.levelName == "TRACE"
        assert direct_logger.level == orig_level
    # Should restore to original TRACE
    assert direct_logger.level == orig_level

    # --- setup: now test that it does upgrade when current is less verbose ---
    direct_logger.setLevel("INFO")
    orig_level = direct_logger.level
    assert direct_logger.levelName == "INFO"

    # --- execute and verify: INFO should upgrade to DEBUG (more verbose) ---
    with direct_logger.useLevel("DEBUG", minimum=True):
        # Should change to DEBUG (more verbose than INFO)
        assert direct_logger.levelName == "DEBUG"
        assert direct_logger.level != orig_level
    # Should restore to original INFO
    assert direct_logger.level == orig_level
    assert direct_logger.levelName == "INFO"


def test_use_level_minimum_with_effective_level_inheritance() -> None:
    """use_level(minimum=True) should compare against effectiveLevel.

    This test verifies that useLevel(minimum=True) compares against effectiveLevel
    (what's actually used for logging), ensuring consistency with
    setLevel(minimum=True). Even when explicit and effective levels are the same,
    the comparison should use effectiveLevel to match setLevel's behavior.
    """
    # --- setup: create parent/child logger hierarchy ---
    parent = mod_alogs.getLogger("test_use_level_parent")
    parent.setLevel("WARNING")  # Parent has explicit WARNING

    child = mod_alogs.getLogger("test_use_level_parent.child")
    # Child will have a default level set (likely DETAIL or INFO), but we'll test
    # that useLevel(minimum=True) compares against effectiveLevel consistently

    # Get the current effective level (what's actually being used)
    current_effective = child.effectiveLevel
    current_explicit = child.level

    # Verify that useLevel(minimum=True) compares against effectiveLevel
    # by testing with a level more verbose than current effective
    more_verbose_level = logging.DEBUG  # More verbose than WARNING/INFO/DETAIL
    if more_verbose_level < current_effective:
        # Should upgrade to DEBUG (more verbose than current effective)
        with child.useLevel("DEBUG", minimum=True):
            assert child.effectiveLevel == logging.DEBUG
            assert child.levelName == "DEBUG"
        # Should restore to original explicit level
        assert child.level == current_explicit
        assert child.effectiveLevel == current_effective

    # Test that it doesn't downgrade when requested level is less verbose
    less_verbose_level = logging.ERROR  # Less verbose than WARNING
    if less_verbose_level > current_effective:
        with child.useLevel("ERROR", minimum=True):
            # Should stay at current effective level (not downgrade)
            assert child.effectiveLevel == current_effective
            assert child.level == current_explicit
        # Should still be at original level
        assert child.level == current_explicit
        assert child.effectiveLevel == current_effective

    # Key test: Verify consistency with setLevel(minimum=True)
    # Both should compare against effectiveLevel
    child.setLevel("TRACE")  # Set explicit to TRACE
    assert child.effectiveLevel == logging.DEBUG - 5  # TRACE level
    assert child.level == logging.DEBUG - 5

    # Now test that useLevel(minimum=True) behaves the same as setLevel(minimum=True)
    # Both should compare against the current effective level (TRACE)
    with child.useLevel("DEBUG", minimum=True):
        # Should NOT downgrade from TRACE to DEBUG
        assert child.effectiveLevel == logging.DEBUG - 5  # Still TRACE
        assert child.levelName == "TRACE"


def test_log_dynamic_accepts_numeric_level(
    capsys: pytest.CaptureFixture[str],
    direct_logger: Logger,
) -> None:
    """log_dynamic() should work with int levels too."""
    # --- execute ---
    direct_logger.logDynamic(
        mod_alogs.apathetic_logging.TRACE_LEVEL, "Numeric trace log works"
    )

    # --- verify ---
    captured = capsys.readouterr()
    combined = (captured.out + captured.err).lower()
    assert "Numeric trace log works".lower() in combined
