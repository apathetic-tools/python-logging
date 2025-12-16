# tests/50_core/test_module_logger_fixture.py
"""Tests for module_logger fixture behavior.

Tests verify that the module_logger fixture correctly sets propagate=False
and that handlers are attached appropriately.
"""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_module_logger_fixture_sets_propagate_false(
    module_logger: mod_alogs.Logger,
) -> None:
    """Test that module_logger fixture sets propagate=False."""
    # --- verify ---
    # Fixture should set propagate=False explicitly (line 70 in log_fixtures.py)
    assert module_logger.propagate is False
    assert getattr(module_logger, "_propagate_explicit", False) is True


def test_module_logger_fixture_has_handler(module_logger: mod_alogs.Logger) -> None:
    """Test that module_logger fixture has handler attached (propagate=False)."""
    # --- setup ---
    # Verify fixture set propagate=False
    assert module_logger.propagate is False
    module_logger.setLevel("DEBUG")
    # Clear handlers and reset _last_stream_ids to test handler reattachment
    # Remove all handlers explicitly (not just clear the list)
    for handler in list(module_logger.handlers):
        module_logger.removeHandler(handler)
    # Reset _last_stream_ids to ensure manageHandlers rebuilds handler
    if hasattr(module_logger, "_last_stream_ids"):
        module_logger._last_stream_ids = None  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    # --- execute ---
    # Explicitly call manageHandlers to ensure handler is attached
    module_logger.manageHandlers(manage_handlers=True)
    # Verify handler is attached after manageHandlers call
    assert len(module_logger.handlers) > 0, (
        "Handler should be attached after manageHandlers()"
    )
    # Check handler type by class name (works in both package and stitched modes
    # where the same class may be imported via different paths)
    assert any(
        type(h).__name__ == "DualStreamHandler" for h in module_logger.handlers
    ), "Handler should be DualStreamHandler"

    # Log a message to verify handler works (this also triggers manageHandlers())
    module_logger.info("test message")

    # --- verify ---
    # Handler should still be present after logging
    assert len(module_logger.handlers) > 0, (
        "Handler should still be present after logging"
    )
    assert any(
        type(h).__name__ == "DualStreamHandler" for h in module_logger.handlers
    ), "Handler should still be DualStreamHandler after logging"


def test_module_logger_fixture_isolated_from_root(
    module_logger: mod_alogs.Logger,
) -> None:
    """Test that module_logger fixture is isolated from root logger."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("WARNING")
    root.handlers.clear()

    module_logger.setLevel("DEBUG")
    module_logger.handlers.clear()

    # --- execute ---
    # Log to module_logger
    module_logger.info("module message")

    # --- verify ---
    # Module logger should have its own handler (propagate=False)
    assert len(module_logger.handlers) > 0
    # Root should not receive the message (propagate=False)
    assert len(root.handlers) == 0

    # --- cleanup ---
    root.setLevel(original_root_level)


def test_module_logger_fixture_level_setting(module_logger: mod_alogs.Logger) -> None:
    """Test that module_logger fixture sets level to 'test'."""
    # --- verify ---
    # Fixture should set level to "test" for maximum verbosity
    _constants = mod_alogs.apathetic_logging
    assert module_logger.level == _constants.TEST_LEVEL
    assert module_logger.levelName == "TEST"


def test_module_logger_fixture_handlers_managed_correctly(
    module_logger: mod_alogs.Logger,
) -> None:
    """Test that module_logger fixture handlers are managed correctly."""
    # --- setup ---
    module_logger.handlers.clear()
    module_logger.setLevel("DEBUG")

    # --- execute ---
    # Change propagate setting and verify handler management
    module_logger.setPropagate(True)

    # --- verify ---
    # With propagate=True, handler should be removed
    assert len(module_logger.handlers) == 0

    # Change back to propagate=False
    module_logger.setPropagate(False)

    # --- verify ---
    # Trigger handler attachment
    module_logger.info("test")
    assert len(module_logger.handlers) > 0
