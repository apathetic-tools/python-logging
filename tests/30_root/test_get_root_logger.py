# tests/30_independant/test_get_root_logger.py
"""Tests for getRootLogger() function.

Note: logger.root is already provided by the standard library's logging.Logger
class, so we don't need to add our own property. These tests verify that
logger.root works correctly with our loggers (inherited from base class).
"""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_get_root_logger_returns_root_logger() -> None:
    """Test that getRootLogger() returns the root logger instance."""
    # --- execute ---
    root = mod_alogs.getRootLogger()  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]

    # --- verify ---
    assert root is logging.getLogger("")
    assert root.name == "root"  # pyright: ignore[reportUnknownMemberType]
    assert isinstance(root, logging.Logger)


def test_get_root_logger_can_set_level() -> None:
    """Test that getRootLogger() returns a logger that can be configured."""
    # --- setup ---
    root = mod_alogs.getRootLogger()  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    original_level = root.level  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]

    # --- execute ---
    root.setLevel("DEBUG")  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]

    # --- verify ---
    assert root.level == logging.DEBUG  # pyright: ignore[reportUnknownMemberType]
    if hasattr(root, "levelName"):  # pyright: ignore[reportUnknownArgumentType]
        assert root.levelName == "DEBUG"  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    # --- cleanup ---
    root.setLevel(original_level)  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]


def test_get_root_logger_same_instance() -> None:
    """Test that getRootLogger() returns the same instance on multiple calls."""
    # --- execute ---
    root1 = mod_alogs.getRootLogger()  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    root2 = mod_alogs.getRootLogger()  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]

    # --- verify ---
    assert root1 is root2
    assert root1 is logging.getLogger("")


def test_logger_root_property_returns_root_logger() -> None:
    """Test that logger.root property returns the root logger instance."""
    # --- setup ---
    child_logger = mod_alogs.getLogger("test_child_for_root_property")

    # --- execute ---
    root = child_logger.root  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]

    # --- verify ---
    assert root is logging.getLogger("")
    assert root.name == "root"  # pyright: ignore[reportUnknownMemberType]
    assert isinstance(root, logging.Logger)


def test_logger_root_property_same_instance() -> None:
    """Test that logger.root property returns the same instance on multiple accesses."""
    # --- setup ---
    child_logger = mod_alogs.getLogger("test_child_for_root_same")

    # --- execute ---
    root1 = child_logger.root  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    root2 = child_logger.root  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]

    # --- verify ---
    assert root1 is root2
    assert root1 is logging.getLogger("")


def test_logger_root_property_can_set_level() -> None:
    """Test that logger.root property returns a logger that can be configured."""
    # --- setup ---
    child_logger = mod_alogs.getLogger("test_child_for_root_set_level")
    root = child_logger.root  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    original_level = root.level  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]

    # --- execute ---
    child_logger.root.setLevel("INFO")  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]

    # --- verify ---
    assert root.level == logging.INFO  # pyright: ignore[reportUnknownMemberType]
    assert child_logger.root.level == logging.INFO  # pyright: ignore[reportUnknownMemberType]
    if hasattr(root, "levelName"):  # pyright: ignore[reportUnknownArgumentType]
        assert root.levelName == "INFO"  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    # --- cleanup ---
    root.setLevel(original_level)  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]


def test_logger_root_property_equals_get_root_logger() -> None:
    """Test that logger.root property returns the same instance as getRootLogger()."""
    # --- setup ---
    child_logger = mod_alogs.getLogger("test_child_for_root_equality")

    # --- execute ---
    root_from_property = child_logger.root  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    root_from_function = mod_alogs.getRootLogger()  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]

    # --- verify ---
    assert root_from_property is root_from_function
    assert root_from_property is logging.getLogger("")


def test_root_logger_root_property_returns_self() -> None:
    """Test that root logger's root property returns itself."""
    # --- setup ---
    root = mod_alogs.getRootLogger()  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]

    # --- execute ---
    root_from_property = root.root  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]

    # --- verify ---
    assert root_from_property is root
    assert root_from_property is logging.getLogger("")
