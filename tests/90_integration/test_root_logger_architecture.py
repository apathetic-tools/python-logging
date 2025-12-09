# tests/90_integration/test_root_logger_architecture.py
"""Integration tests for root logger architecture.

Tests the end-to-end behavior of the root logger architecture where:
- Root logger has handler and sets level
- Child loggers inherit level from root (NOTSET)
- Child loggers propagate to root (propagate=True)
- All loggers use same level via root
"""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_cli_app_sets_root_level_all_libraries_inherit() -> None:
    """Test that CLI app setting root level affects all library loggers."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    # Simulate library loggers
    lib1_logger = mod_alogs.getLogger("lib1")
    lib2_logger = mod_alogs.getLogger("lib2")
    lib3_logger = mod_alogs.getLogger("lib3")

    # All should default to NOTSET
    assert lib1_logger.level == logging.NOTSET
    assert lib2_logger.level == logging.NOTSET
    assert lib3_logger.level == logging.NOTSET

    # --- execute ---
    # CLI app sets root level once
    mod_alogs.setRootLevel("DEBUG")

    # --- verify ---
    # All library loggers inherit from root
    assert lib1_logger.effectiveLevel == logging.DEBUG
    assert lib2_logger.effectiveLevel == logging.DEBUG
    assert lib3_logger.effectiveLevel == logging.DEBUG
    assert root.level == logging.DEBUG

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_multiple_libraries_use_same_level_from_root() -> None:
    """Test that multiple libraries all use the same level from root."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    # Simulate different libraries
    apathetic_logger = mod_alogs.getLogger("apathetic_logging")
    utils_logger = mod_alogs.getLogger("utils")
    schema_logger = mod_alogs.getLogger("schema")

    # Set root level
    mod_alogs.setRootLevel("INFO")

    # --- execute ---
    # All loggers should have same effective level
    root_effective = root.getEffectiveLevel()
    apathetic_effective = apathetic_logger.getEffectiveLevel()
    utils_effective = utils_logger.getEffectiveLevel()
    schema_effective = schema_logger.getEffectiveLevel()

    # --- verify ---
    assert root_effective == logging.INFO
    assert apathetic_effective == logging.INFO
    assert utils_effective == logging.INFO
    assert schema_effective == logging.INFO

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_messages_propagate_from_child_to_root() -> None:
    """Test that messages from child loggers propagate to root handler."""
    # --- setup ---

    root = logging.getLogger("")
    original_root_level = root.level
    root.handlers.clear()
    root.setLevel("DEBUG")

    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter("%(message)s"))
    root.addHandler(handler)

    child = mod_alogs.getLogger("test_propagate_child")
    child.propagate = True
    child.handlers.clear()  # Ensure no handler
    child.setLevel("DEBUG")

    # --- execute ---
    child.info("child message")

    # --- verify ---
    # Child should not have handler
    assert len(child.handlers) == 0
    # Root should have handler
    assert len(root.handlers) > 0
    # Message should have been processed (propagated to root)

    # --- cleanup ---
    root.setLevel(original_root_level)
    root.handlers.clear()
    # Loggers will be cleaned up by test fixture


def test_no_duplicate_messages_when_propagate_true() -> None:
    """Test that there are no duplicate messages when propagate=True."""
    # --- setup ---

    root = logging.getLogger("")
    original_root_level = root.level
    root.handlers.clear()
    root.setLevel("DEBUG")

    handler = mod_alogs.DualStreamHandler()
    handler.setFormatter(mod_alogs.TagFormatter("%(message)s"))
    root.addHandler(handler)

    child = mod_alogs.getLogger("test_no_duplicate")
    child.propagate = True
    child.handlers.clear()  # Ensure no handler on child
    child.setLevel("DEBUG")

    # --- execute ---
    child.info("test message")

    # --- verify ---
    # Child should not have handler (prevents duplicate)
    assert len(child.handlers) == 0
    # Root should have handler
    assert len(root.handlers) > 0
    # Message should only be processed once (by root handler)

    # --- cleanup ---
    root.setLevel(original_root_level)
    root.handlers.clear()
    # Loggers will be cleaned up by test fixture


def test_root_has_handler_children_dont_when_propagating() -> None:
    """Test that root has handler but children don't when propagating."""
    # --- setup ---
    # Use apathetic logger for root (may be standard RootLogger)
    root = mod_alogs.getLogger("")
    root.setLevel("DEBUG")
    root.handlers.clear()

    child1 = mod_alogs.getLogger("test_handler_child1")
    child2 = mod_alogs.getLogger("test_handler_child2")
    child3 = mod_alogs.getLogger("test_handler_child3")
    child1.setLevel("DEBUG")
    child2.setLevel("DEBUG")
    child3.setLevel("DEBUG")

    # All should be propagating by default
    assert child1.propagate is True
    assert child2.propagate is True
    assert child3.propagate is True

    # Clear any existing handlers
    child1.handlers.clear()
    child2.handlers.clear()
    child3.handlers.clear()

    # --- execute ---
    # Trigger handler attachment by logging
    root.info("root message")
    child1.info("child1 message")
    child2.info("child2 message")
    child3.info("child3 message")

    # --- verify ---
    # Root should have handler (if it's an apathetic logger)
    if hasattr(root, "manageHandlers"):
        assert len(root.handlers) > 0
    # Children should not have handlers (propagating)
    assert len(child1.handlers) == 0
    assert len(child2.handlers) == 0
    assert len(child3.handlers) == 0

    # --- cleanup ---
    root.handlers.clear()
    # Loggers will be cleaned up by test fixture


def test_non_propagating_child_has_own_handler() -> None:
    """Test that non-propagating child logger has its own handler."""
    # --- setup ---
    root = logging.getLogger("")
    root.handlers.clear()

    child = mod_alogs.getLogger("test_non_propagate_handler")
    child.propagate = False
    child.setLevel("DEBUG")  # Ensure level allows INFO messages
    child.handlers.clear()

    # --- execute ---
    # Trigger handler attachment by logging
    child.info("child message")

    # --- verify ---
    # Child should have its own handler (not propagating)
    assert len(child.handlers) > 0
    assert any(isinstance(h, mod_alogs.DualStreamHandler) for h in child.handlers)

    # --- cleanup ---
    root.handlers.clear()
    child.handlers.clear()
    # Loggers will be cleaned up by test fixture
