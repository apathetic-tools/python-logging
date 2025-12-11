# tests/50_core/test_logger_notset_inheritance.py
"""Tests for NOTSET inheritance from root logger."""

from __future__ import annotations

import logging
import os

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

    # If parent is also INHERIT_LEVEL (i.e. NOTSET), child inherits from root
    _constants = mod_alogs.apathetic_logging
    parent.setLevel(_constants.INHERIT_LEVEL, allow_inherit=True)
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


def test_get_logger_without_level_defaults_to_notset() -> None:
    """Test getLogger() without level defaults to NOTSET (not auto-resolving)."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("INFO")

    # Set environment variable (should be ignored when level is not passed)
    original_env = os.environ.get("LOG_LEVEL")
    os.environ["LOG_LEVEL"] = "DEBUG"

    # --- execute ---
    # getLogger() without level parameter should default to NOTSET
    logger = mod_alogs.getLogger("test_get_logger_no_level")

    # --- verify ---
    # Should be NOTSET, not auto-resolved from env
    assert logger.level == logging.NOTSET
    assert logger.levelName == "NOTSET"
    # Effective level inherits from root
    assert logger.effectiveLevel == logging.INFO

    # --- cleanup ---
    root.setLevel(original_root_level)
    if original_env is None:
        os.environ.pop("LOG_LEVEL", None)
    else:
        os.environ["LOG_LEVEL"] = original_env
