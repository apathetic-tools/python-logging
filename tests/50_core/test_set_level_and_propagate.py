# tests/50_core/test_set_level_and_propagate.py
"""Tests for Logger.setLevelAndPropagate() method."""

import logging

import apathetic_logging as mod_alogs


def test_set_level_and_propagate_inherit_sets_propagate_true() -> None:
    """setLevelAndPropagate(INHERIT_LEVEL) should set propagate=True."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_set_level_and_propagate_inherit")
    child.setPropagate(False)  # Start with propagate=False
    child.setLevel("debug")  # Start with explicit level

    # --- execute ---
    child.setLevelAndPropagate(_constants.INHERIT_LEVEL, allow_inherit=True)

    # --- verify ---
    assert child.level == _constants.INHERIT_LEVEL
    assert child.propagate is True


def test_set_level_and_propagate_specific_level_sets_propagate_false() -> None:
    """setLevelAndPropagate(specific level) should set propagate=False."""
    # --- setup ---
    child = mod_alogs.Logger("test_set_level_and_propagate_specific")
    child.setPropagate(True)  # Start with propagate=True
    child.setLevel(mod_alogs.apathetic_logging.INHERIT_LEVEL, allow_inherit=True)

    # --- execute ---
    child.setLevelAndPropagate("debug")

    # --- verify ---
    assert child.level == logging.DEBUG
    assert child.propagate is False


def test_set_level_and_propagate_on_root_only_sets_level() -> None:
    """setLevelAndPropagate() on root logger should only set level, not propagate."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    root = mod_alogs.getLogger("")
    original_propagate = root.propagate
    original_level = root.level

    # --- execute ---
    # Only test if root is an apathetic logger (has setLevelAndPropagate method)
    if hasattr(root, "setLevelAndPropagate"):
        root.setLevelAndPropagate("debug")

        # --- verify ---
        assert root.level == logging.DEBUG
        assert root.propagate == original_propagate  # Should be unchanged

        # Test with INHERIT_LEVEL
        root.setLevelAndPropagate(_constants.INHERIT_LEVEL, allow_inherit=True)

        # --- verify ---
        assert root.level == _constants.INHERIT_LEVEL
        assert root.propagate == original_propagate  # Should still be unchanged

        # --- cleanup ---
        root.setLevel(original_level, allow_inherit=True)
        root.setPropagate(original_propagate)
    else:
        # Root logger is not an apathetic logger - skip this test
        pass


def test_set_level_and_propagate_with_string_level() -> None:
    """setLevelAndPropagate() should accept string level names."""
    # --- setup ---
    child = mod_alogs.Logger("test_set_level_and_propagate_string")

    # --- execute ---
    child.setLevelAndPropagate("info")

    # --- verify ---
    assert child.level == logging.INFO
    assert child.propagate is False


def test_set_level_and_propagate_with_minimum() -> None:
    """setLevelAndPropagate() should respect minimum parameter."""
    # --- setup ---
    child = mod_alogs.Logger("test_set_level_and_propagate_minimum")
    child.setLevel("trace")  # More verbose than debug
    original_level = child.level

    # --- execute ---
    # Try to set to debug with minimum=True (should not downgrade)
    child.setLevelAndPropagate("debug", minimum=True)

    # --- verify ---
    assert child.level == original_level  # Should not have changed
    assert child.propagate is False  # But propagate should still be set

    # Now try with a more verbose level (should work)
    child.setLevelAndPropagate("test", minimum=True)

    # --- verify ---
    assert child.level < original_level  # Should have changed to more verbose
    assert child.propagate is False


def test_set_level_and_propagate_affects_handler_attachment() -> None:
    """setLevelAndPropagate() should automatically manage handlers."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_set_level_and_propagate_handler")
    child.handlers.clear()

    # --- execute ---
    # Set to INHERIT_LEVEL -> propagate=True -> no handler
    child.setLevelAndPropagate(_constants.INHERIT_LEVEL, allow_inherit=True)

    # --- verify ---
    assert len(child.handlers) == 0  # propagate=True means no handler

    # Set to specific level -> propagate=False -> handler
    child.setLevelAndPropagate("debug")

    # --- verify ---
    assert len(child.handlers) > 0  # propagate=False means handler


def test_set_level_and_propagate_with_manage_handlers() -> None:
    """setLevelAndPropagate() should pass manage_handlers to setPropagate()."""
    # --- setup ---
    child = mod_alogs.Logger("test_set_level_and_propagate_manage_handlers")
    child.handlers.clear()

    # --- execute ---
    child.setLevelAndPropagate("debug", manage_handlers=True)

    # --- verify ---
    assert child.level == logging.DEBUG
    assert child.propagate is False
    assert len(child.handlers) > 0  # Handler should be attached


def test_set_level_and_propagate_can_be_called_multiple_times() -> None:
    """setLevelAndPropagate() should work when called multiple times."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_set_level_and_propagate_multiple")

    # --- execute ---
    child.setLevelAndPropagate("debug")
    assert child.level == logging.DEBUG
    assert child.propagate is False

    child.setLevelAndPropagate(_constants.INHERIT_LEVEL, allow_inherit=True)
    assert child.level == _constants.INHERIT_LEVEL
    assert child.propagate is True

    child.setLevelAndPropagate("info")
    assert child.level == logging.INFO
    assert child.propagate is False

    # --- verify ---
    assert child.level == logging.INFO
    assert child.propagate is False
