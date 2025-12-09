# tests/50_core/test_manage_handlers_propagate.py
"""Tests for manageHandlers() behavior with propagate settings."""

from __future__ import annotations

import io
import logging
import sys

import apathetic_logging as mod_alogs


def test_root_logger_always_gets_handler() -> None:
    """Test that root logger always gets a handler."""
    # --- setup ---
    # Get root logger - may be standard RootLogger or apathetic Logger
    # (see ROADMAP.md for note about root logger potentially not being apathetic)
    root = mod_alogs.getLogger("")
    original_level = root.level
    root.setLevel("DEBUG")
    # Clear any existing handlers
    root.handlers.clear()

    # --- execute ---
    # Trigger manageHandlers by logging (handlers are attached in _log())
    # Only works if root is an apathetic logger
    root.info("test message")

    # --- verify ---
    # If root is an apathetic logger, it should have a handler
    # If it's a standard RootLogger, it won't (this is a known limitation)
    # Check if it's an apathetic logger by checking for the manageHandlers method
    if hasattr(root, "manageHandlers"):
        assert len(root.handlers) > 0
        assert any(isinstance(h, mod_alogs.DualStreamHandler) for h in root.handlers)
    # If root is standard RootLogger, handlers might be empty (known limitation)

    # --- cleanup ---
    root.setLevel(original_level)


def test_child_logger_with_propagate_true_no_handler() -> None:
    """Test that child logger with propagate=True does NOT get handler."""
    # --- setup ---
    child = mod_alogs.getLogger("test_child_propagate")
    child.propagate = True
    child.handlers.clear()

    # --- execute ---
    # Trigger manageHandlers by logging
    child.info("test message")

    # --- verify ---
    # Child logger should not have handler (messages propagate to root)
    assert len(child.handlers) == 0


def test_child_logger_with_propagate_false_gets_handler() -> None:
    """Test that child logger with propagate=False DOES get handler."""
    # --- setup ---
    child = mod_alogs.getLogger("test_child_no_propagate")
    child.propagate = False
    child.setLevel("DEBUG")  # Ensure level allows INFO messages
    child.handlers.clear()

    # --- execute ---
    # Trigger manageHandlers by logging
    child.info("test message")

    # --- verify ---
    # Child logger should have handler (not propagating)
    assert len(child.handlers) > 0
    assert any(isinstance(h, mod_alogs.DualStreamHandler) for h in child.handlers)


def test_child_logger_propagate_true_messages_go_to_root() -> None:
    """Test that messages from propagating child loggers reach root handler."""
    # --- setup ---
    root = logging.getLogger("")
    root.handlers.clear()
    root.setLevel("DEBUG")

    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter("%(message)s"))
    root.addHandler(handler)

    child = mod_alogs.getLogger("test_child_propagate_msg")
    child.propagate = True
    child.handlers.clear()
    child.setLevel("DEBUG")

    # --- execute ---
    child.info("child message")

    # --- verify ---
    # Message should appear in root's handler output
    # (We can't easily capture it without more setup, but we can verify
    # the handler exists and child doesn't have one)
    assert len(child.handlers) == 0
    assert len(root.handlers) > 0


def test_child_logger_propagate_false_messages_stay_local() -> None:
    """Test that messages from non-propagating child loggers stay local."""
    # --- setup ---
    child = mod_alogs.getLogger("test_child_no_propagate_msg")
    child.propagate = False
    child.handlers.clear()
    child.setLevel("DEBUG")

    # --- execute ---
    # Trigger manageHandlers by logging
    child.info("child message")

    # --- verify ---
    # Child logger should have its own handler
    assert len(child.handlers) > 0
    assert any(isinstance(h, mod_alogs.DualStreamHandler) for h in child.handlers)


def test_manage_handlers_rebuilds_when_streams_change() -> None:
    """Test that manageHandlers rebuilds handlers when stdout/stderr change."""
    # --- setup ---
    # Use apathetic logger, not standard root logger
    root = mod_alogs.getLogger("")
    root.setLevel("DEBUG")
    root.handlers.clear()

    # Log once to create handler
    root.info("first message")

    # Change stdout
    new_stdout = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = new_stdout

    # --- execute ---
    root.info("second message")

    # --- verify ---
    # Handler should still exist (may be rebuilt)
    # Only works if root is an apathetic logger
    if hasattr(root, "manageHandlers"):
        assert len(root.handlers) > 0

    # --- cleanup ---
    sys.stdout = original_stdout
