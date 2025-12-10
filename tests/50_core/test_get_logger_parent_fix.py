# tests/50_core/test_get_logger_parent_fix.py
"""Tests for parent logger fix in getLogger() and getLoggerOfType()."""

import logging

import apathetic_logging as mod_alogs


def test_get_logger_fixes_parent_when_old_root() -> None:
    """getLogger() should fix parent if it points to old root logger."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.DEBUG)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Replace root logger with apathetic logger
    mod_alogs.Logger.extendLoggingModule(replace_root=True)

    # Get new root logger
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    assert isinstance(new_root, mod_alogs.Logger)

    # --- execute ---
    # Create a new logger - it might initially get standard_root as parent
    # but should be fixed to point to new_root
    child = mod_alogs.getLogger("test_parent_fix")

    # --- verify ---
    # Parent should be new_root (not standard_root)
    assert child.parent is new_root
    assert child.parent is not standard_root

    # Should inherit from new root
    assert child.effectiveLevel == new_root.level  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)


def test_get_logger_preserves_intermediate_parent() -> None:
    """getLogger() should preserve intermediate parent (not force to root)."""
    # --- setup ---
    # Create a parent logger
    parent = mod_alogs.getLogger("test_parent")
    parent.setLevel(logging.INFO)

    # --- execute ---
    # Create a child logger
    child = mod_alogs.getLogger("test_parent.child")

    # --- verify ---
    # Parent should be the intermediate logger, not root
    assert child.parent is parent
    assert child.parent is not logging.getLogger("")

    # Should inherit from parent
    assert child.effectiveLevel == logging.INFO  # pyright: ignore[reportAttributeAccessIssue]


def test_get_logger_of_type_fixes_parent_when_old_root() -> None:
    """getLoggerOfType() should fix parent if it points to old root logger."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.DEBUG)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Replace root logger with apathetic logger
    mod_alogs.Logger.extendLoggingModule(replace_root=True)

    # Get new root logger
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    assert isinstance(new_root, mod_alogs.Logger)

    # --- execute ---
    # Create a new logger using getLoggerOfType
    child = mod_alogs.getLoggerOfType("test_parent_fix_type", mod_alogs.Logger)

    # --- verify ---
    # Parent should be new_root (not standard_root)
    assert child.parent is new_root
    assert child.parent is not standard_root

    # Should inherit from new root
    assert child.effectiveLevel == new_root.level  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)
