# tests/50_core/test_tag_formatter.py
"""Tests for TagFormatter class."""

import logging

import pytest

import apathetic_logging as mod_alogs


def test_tag_formatter_adds_tag_prefix() -> None:
    """TagFormatter should add tag prefix to log messages."""
    # --- setup ---
    formatter = mod_alogs.apathetic_logging.TagFormatter()
    # Use DEBUG level which has a tag in TAG_STYLES
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )
    record.levelname = "DEBUG"

    # --- execute ---
    formatted = formatter.format(record)

    # --- verify ---
    # Should contain the tag text from TAG_STYLES
    tag_text = mod_alogs.apathetic_logging.TAG_STYLES.get("DEBUG", ("", ""))[1]
    assert tag_text in formatted
    assert "test message" in formatted


def test_tag_formatter_respects_enable_color_false() -> None:
    """TagFormatter should not add ANSI codes when enable_color is False."""
    # --- setup ---
    formatter = mod_alogs.apathetic_logging.TagFormatter()
    # Use DEBUG level which has a tag in TAG_STYLES
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )
    record.levelname = "DEBUG"
    record.enable_color = False

    # --- execute ---
    formatted = formatter.format(record)

    # --- verify ---
    # Should not contain ANSI escape codes
    assert "\033[" not in formatted
    # Should still contain tag text
    tag_text = mod_alogs.apathetic_logging.TAG_STYLES.get("DEBUG", ("", ""))[1]
    assert tag_text in formatted


def test_tag_formatter_respects_enable_color_true() -> None:
    """TagFormatter should add ANSI codes when enable_color is True."""
    # --- setup ---
    formatter = mod_alogs.apathetic_logging.TagFormatter()
    # Use DEBUG level which has a color in TAG_STYLES
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )
    record.levelname = "DEBUG"
    record.enable_color = True

    # --- execute ---
    formatted = formatter.format(record)

    # --- verify ---
    # Should contain ANSI escape codes (DEBUG has CYAN color)
    assert "\033[" in formatted
    # Should contain tag text
    tag_text = mod_alogs.apathetic_logging.TAG_STYLES.get("DEBUG", ("", ""))[1]
    assert tag_text in formatted


@pytest.mark.parametrize(
    ("level_name", "level_num"),
    [
        ("TRACE", 5),
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ],
)
def test_tag_formatter_all_levels(level_name: str, level_num: int) -> None:
    """TagFormatter should format all log levels correctly."""
    # --- setup ---
    formatter = mod_alogs.apathetic_logging.TagFormatter()
    record = logging.LogRecord(
        name="test",
        level=level_num,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )
    record.levelname = level_name
    record.enable_color = False

    # --- execute ---
    formatted = formatter.format(record)

    # --- verify ---
    # Should contain the tag text if it exists in TAG_STYLES
    if level_name in mod_alogs.apathetic_logging.TAG_STYLES:
        tag_text = mod_alogs.apathetic_logging.TAG_STYLES[level_name][1]
        assert tag_text in formatted
    assert "test message" in formatted


def test_tag_formatter_unknown_level_no_tag() -> None:
    """TagFormatter should handle unknown log levels gracefully."""
    # --- setup ---
    formatter = mod_alogs.apathetic_logging.TagFormatter()
    record = logging.LogRecord(
        name="test",
        level=999,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )
    record.levelname = "UNKNOWN"
    record.enable_color = False

    # --- execute ---
    formatted = formatter.format(record)

    # --- verify ---
    # Should still format the message even without a tag
    assert "test message" in formatted
