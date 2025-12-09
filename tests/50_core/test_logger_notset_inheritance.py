# tests/50_core/test_logger_notset_inheritance.py
"""Tests for NOTSET inheritance from root logger."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_logger_notset_inherits_from_root() -> None:
    """Test that logger with NOTSET inherits level from root."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("INFO")

    child = mod_alogs.getLogger("test_notset_inherit")
    # Child should default to NOTSET
    assert child.level == logging.NOTSET

    # --- verify ---
    # Effective level should inherit from root
    assert child.effectiveLevel == logging.INFO
    assert child.effectiveLevelName == "INFO"
    # Explicit level remains NOTSET
    assert child.level == logging.NOTSET
    assert child.levelName == "NOTSET"

    # --- cleanup ---
    root.setLevel(original_root_level)


def test_changing_root_level_affects_notset_children() -> None:
    """Test that changing root level affects child loggers with NOTSET."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    child = mod_alogs.getLogger("test_notset_change")
    root.setLevel("DEBUG")
    assert child.effectiveLevel == logging.DEBUG

    # --- execute ---
    root.setLevel("WARNING")

    # --- verify ---
    assert child.effectiveLevel == logging.WARNING
    assert child.effectiveLevelName == "WARNING"
    # Explicit level still NOTSET
    assert child.level == logging.NOTSET

    # --- cleanup ---
    root.setLevel(original_root_level)


def test_child_with_explicit_level_does_not_inherit() -> None:
    """Test that child logger with explicit level doesn't inherit from root."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("DEBUG")

    child = mod_alogs.getLogger("test_explicit_no_inherit")
    child.setLevel("ERROR")

    # --- verify ---
    # Effective level matches explicit level, not root
    assert child.level == logging.ERROR
    assert child.effectiveLevel == logging.ERROR
    assert child.effectiveLevelName == "ERROR"

    # Change root - child should not be affected
    root.setLevel("INFO")
    assert child.effectiveLevel == logging.ERROR  # Still ERROR

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_nested_loggers_inherit_chain() -> None:
    """Test that nested loggers inherit through the chain."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("DEBUG")

    parent = mod_alogs.getLogger("test_parent")
    parent.setLevel("INFO")  # Parent has explicit level

    child = mod_alogs.getLogger("test_parent.child")
    # Child defaults to NOTSET

    # --- verify ---
    # Child inherits from parent (not root) because parent has explicit level
    assert child.level == logging.NOTSET
    assert child.effectiveLevel == logging.INFO  # From parent
    assert parent.effectiveLevel == logging.INFO

    # If parent is also NOTSET, child inherits from root
    _constants = mod_alogs.apathetic_logging
    parent.setLevel(_constants.NOTSET_LEVEL, allow_notset=True)
    assert child.effectiveLevel == logging.DEBUG  # From root

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_set_root_level_affects_all_notset_children() -> None:
    """Test that setRootLevel affects all child loggers with NOTSET."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    child1 = mod_alogs.getLogger("test_notset_child1")
    child2 = mod_alogs.getLogger("test_notset_child2")
    child3 = mod_alogs.getLogger("test_notset_child3")

    # All children default to NOTSET
    assert child1.level == logging.NOTSET
    assert child2.level == logging.NOTSET
    assert child3.level == logging.NOTSET

    # --- execute ---
    mod_alogs.setRootLevel("WARNING")

    # --- verify ---
    # All children inherit new root level
    assert child1.effectiveLevel == logging.WARNING
    assert child2.effectiveLevel == logging.WARNING
    assert child3.effectiveLevel == logging.WARNING
    # Explicit levels still NOTSET
    assert child1.level == logging.NOTSET
    assert child2.level == logging.NOTSET
    assert child3.level == logging.NOTSET

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture
