# tests/30_independant/test_set_root_level.py
"""Tests for setRootLevel function."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_set_root_level_sets_root_logger_level() -> None:
    """Test that setRootLevel sets the level on root logger."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG")

    # --- verify ---
    assert root.level == logging.DEBUG
    # levelName may not exist on standard RootLogger
    if hasattr(root, "levelName"):
        assert root.levelName == "DEBUG"  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    # --- cleanup ---
    root.setLevel(original_level)


def test_set_root_level_with_string_level() -> None:
    """Test that setRootLevel accepts string level names."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level

    # --- execute ---
    mod_alogs.setRootLevel("INFO")

    # --- verify ---
    assert root.level == logging.INFO
    # levelName may not exist on standard RootLogger
    if hasattr(root, "levelName"):
        assert root.levelName == "INFO"  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    # --- cleanup ---
    root.setLevel(original_level)


def test_set_root_level_with_custom_levels() -> None:
    """Test that setRootLevel works with custom levels."""
    # --- setup ---
    root = logging.getLogger("")
    original_level = root.level
    _constants = mod_alogs.apathetic_logging

    # --- execute ---
    mod_alogs.setRootLevel("TRACE")

    # --- verify ---
    assert root.level == _constants.TRACE_LEVEL

    # --- cleanup ---
    root.setLevel(original_level)


def test_set_root_level_affects_child_loggers_with_propagate() -> None:
    """Test that setting root level affects child loggers when propagate=True."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    child1 = mod_alogs.getLogger("test_child1")
    child2 = mod_alogs.getLogger("test_child2")
    # Start with NOTSET so they inherit (default behavior)
    # Don't call setLevel(NOTSET) - loggers default to NOTSET

    # Ensure they're propagating
    child1.propagate = True
    child2.propagate = True

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG")

    # --- verify ---
    # Child loggers inherit effective level from root (since they're NOTSET)
    assert child1.effectiveLevel == logging.DEBUG
    assert child2.effectiveLevel == logging.DEBUG
    # Explicit levels remain NOTSET (inheriting)
    assert child1.level == logging.NOTSET
    assert child2.level == logging.NOTSET

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_set_root_level_apply_to_children_false() -> None:
    """Test that apply_to_children=False only sets root level."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    child = mod_alogs.getLogger("test_child_apply_false")
    child.setLevel("WARNING")
    child.propagate = True

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG", apply_to_children=False)

    # --- verify ---
    assert root.level == logging.DEBUG
    # Child's explicit level unchanged
    assert child.level == logging.WARNING
    # Effective level is still WARNING (explicit level, not inherited)
    assert child.effectiveLevel == logging.WARNING

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_set_root_level_apply_to_children_updates_non_notset() -> None:
    """Test that apply_to_children=True updates child loggers that aren't NOTSET."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    child_with_level = mod_alogs.getLogger("test_child_with_level")
    child_notset = mod_alogs.getLogger("test_child_notset")
    child_with_level.setLevel("WARNING")
    # child_notset is already NOTSET by default
    child_with_level.propagate = True
    child_notset.propagate = True

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG", apply_to_children=True, set_children_to_level=True)

    # --- verify ---
    assert root.level == logging.DEBUG
    # Child with explicit level gets updated
    assert child_with_level.level == logging.DEBUG
    # Child with NOTSET stays NOTSET (not updated)
    assert child_notset.level == logging.NOTSET

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_set_root_level_set_children_to_level_false() -> None:
    """Test that set_children_to_level=False sets children to NOTSET."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    child = mod_alogs.getLogger("test_child_to_notset")
    child.setLevel("WARNING")
    child.propagate = True

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG", set_children_to_level=False)

    # --- verify ---
    assert root.level == logging.DEBUG
    # Child is set to NOTSET to inherit from root
    assert child.level == logging.NOTSET
    assert child.effectiveLevel == logging.DEBUG

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture


def test_set_root_level_with_named_root() -> None:
    """Test that root parameter works with named loggers."""
    # --- setup ---
    parent = mod_alogs.getLogger("test_parent")
    original_parent_level = parent.level
    # If original level is NOTSET, set to a valid level for cleanup
    if original_parent_level == logging.NOTSET:
        original_parent_level = logging.WARNING

    child1 = mod_alogs.getLogger("test_parent.child1")
    child2 = mod_alogs.getLogger("test_parent.child2")
    child1.setLevel("WARNING")
    child2.setLevel("ERROR")
    child1.propagate = True
    child2.propagate = True

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG", root=parent)

    # --- verify ---
    assert parent.level == logging.DEBUG
    # Children of parent are affected
    assert child1.effectiveLevel == logging.DEBUG
    assert child2.effectiveLevel == logging.DEBUG

    # --- cleanup ---
    # Only restore if it wasn't NOTSET originally
    if original_parent_level != logging.NOTSET:
        parent.setLevel(original_parent_level)
    # Loggers will be cleaned up by test fixture


def test_set_root_level_only_affects_children_of_root() -> None:
    """Test that setRootLevel only affects children of the specified root."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level

    parent = mod_alogs.getLogger("test_parent")
    parent.setLevel("WARNING")

    sibling = mod_alogs.getLogger("test_sibling")
    sibling.setLevel("ERROR")

    child = mod_alogs.getLogger("test_parent.child")
    child.setLevel("INFO")
    child.propagate = True

    # --- execute ---
    mod_alogs.setRootLevel("DEBUG", root=parent)

    # --- verify ---
    assert parent.level == logging.DEBUG
    # Child of parent is affected
    assert child.effectiveLevel == logging.DEBUG
    # Sibling (not a child) is not affected
    assert sibling.level == logging.ERROR
    assert sibling.effectiveLevel == logging.ERROR

    # --- cleanup ---
    root.setLevel(original_root_level)
    # Loggers will be cleaned up by test fixture
