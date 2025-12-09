# tests/50_core/test_use_level_and_propagate.py
"""Tests for Logger.useLevelAndPropagate() context manager."""

import logging

import apathetic_logging as mod_alogs


def test_use_level_and_propagate_inherit_sets_propagate_true() -> None:
    """useLevelAndPropagate(INHERIT_LEVEL) should set propagate=True."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_use_level_and_propagate_inherit")
    child.setPropagate(False)  # Start with propagate=False
    child.setLevel("debug")  # Start with explicit level
    orig_level = child.level
    orig_propagate = child.propagate

    # --- execute ---
    with child.useLevelAndPropagate(_constants.INHERIT_LEVEL):
        # --- verify ---
        assert child.level == _constants.INHERIT_LEVEL
        assert child.propagate is True

    # --- verify restoration ---
    assert child.level == orig_level
    assert child.propagate == orig_propagate


def test_use_level_and_propagate_specific_level_sets_propagate_false() -> None:
    """useLevelAndPropagate(specific level) should set propagate=False."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_use_level_and_propagate_specific")
    child.setPropagate(True)  # Start with propagate=True
    child.setLevel(_constants.INHERIT_LEVEL, allow_inherit=True)
    orig_level = child.level
    orig_propagate = child.propagate

    # --- execute ---
    with child.useLevelAndPropagate("debug"):
        # --- verify ---
        assert child.level == logging.DEBUG
        assert child.propagate is False

    # --- verify restoration ---
    assert child.level == orig_level
    assert child.propagate == orig_propagate


def test_use_level_and_propagate_on_root_only_sets_level() -> None:
    """useLevelAndPropagate() on root logger should only set level, not propagate."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    root = mod_alogs.getLogger("")
    original_propagate = root.propagate
    original_level = root.level

    # --- execute ---
    # Only test if root is an apathetic logger (has useLevelAndPropagate method)
    if hasattr(root, "useLevelAndPropagate"):
        with root.useLevelAndPropagate("debug"):
            # --- verify ---
            assert root.level == logging.DEBUG
            assert root.propagate == original_propagate  # Should be unchanged

        # --- verify restoration ---
        assert root.level == original_level
        assert root.propagate == original_propagate

        # Test with INHERIT_LEVEL
        with root.useLevelAndPropagate(_constants.INHERIT_LEVEL):
            # --- verify ---
            assert root.level == _constants.INHERIT_LEVEL
            assert root.propagate == original_propagate  # Should still be unchanged

        # --- verify restoration ---
        assert root.level == original_level
        assert root.propagate == original_propagate
    else:
        # Root logger is not an apathetic logger - skip this test
        pass


def test_use_level_and_propagate_with_string_level() -> None:
    """useLevelAndPropagate() should accept string level names."""
    # --- setup ---
    child = mod_alogs.Logger("test_use_level_and_propagate_string")
    orig_level = child.level
    orig_propagate = child.propagate

    # --- execute ---
    with child.useLevelAndPropagate("info"):
        # --- verify ---
        assert child.level == logging.INFO
        assert child.propagate is False

    # --- verify restoration ---
    assert child.level == orig_level
    assert child.propagate == orig_propagate


def test_use_level_and_propagate_with_minimum() -> None:
    """useLevelAndPropagate() should respect minimum parameter."""
    # --- setup ---
    child = mod_alogs.Logger("test_use_level_and_propagate_minimum")
    child.setLevel("trace")  # More verbose than debug
    original_level = child.level
    original_propagate = child.propagate

    # --- execute ---
    # Try to set to debug with minimum=True (should not downgrade)
    with child.useLevelAndPropagate("debug", minimum=True):
        # --- verify ---
        assert child.level == original_level  # Should not have changed
        assert child.propagate is False  # But propagate should still be set

    # --- verify restoration ---
    assert child.level == original_level
    assert child.propagate == original_propagate

    # Now try with a more verbose level (should work)
    with child.useLevelAndPropagate("test", minimum=True):
        # --- verify ---
        assert child.level < original_level  # Should have changed to more verbose
        assert child.propagate is False

    # --- verify restoration ---
    assert child.level == original_level
    assert child.propagate == original_propagate


def test_use_level_and_propagate_affects_handler_attachment() -> None:
    """useLevelAndPropagate() should affect handler attachment during context."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_use_level_and_propagate_handler")
    child.handlers.clear()
    child.setPropagate(True)  # Start with propagate=True (no handler)
    assert len(child.handlers) == 0

    # --- execute ---
    with child.useLevelAndPropagate("debug"):
        # With propagate=False, child should have handler
        assert len(child.handlers) > 0

    # --- verify ---
    # After context, should restore to propagate=True (no handler)
    assert child.propagate is True
    # Handler should be removed when propagate is restored to True
    assert len(child.handlers) == 0


def test_use_level_and_propagate_with_manage_handlers() -> None:
    """useLevelAndPropagate() should pass manage_handlers to setPropagate()."""
    # --- setup ---
    child = mod_alogs.Logger("test_use_level_and_propagate_manage_handlers")
    child.handlers.clear()
    orig_level = child.level
    orig_propagate = child.propagate

    # --- execute ---
    with child.useLevelAndPropagate("debug", manage_handlers=True):
        # --- verify ---
        assert child.level == logging.DEBUG
        assert child.propagate is False
        assert len(child.handlers) > 0  # Handler should be attached

    # --- verify restoration ---
    assert child.level == orig_level
    assert child.propagate == orig_propagate


def test_use_level_and_propagate_nested_contexts() -> None:
    """useLevelAndPropagate() should work correctly with nested contexts."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_use_level_and_propagate_nested")
    child.setLevel("info")
    child.setPropagate(True)
    orig_level = child.level
    orig_propagate = child.propagate

    # --- execute ---
    with child.useLevelAndPropagate("debug"):
        assert child.level == logging.DEBUG
        assert child.propagate is False
        with child.useLevelAndPropagate(_constants.INHERIT_LEVEL):
            assert child.level == _constants.INHERIT_LEVEL
            assert child.propagate is True
        # Should restore to debug/False (inner context)
        assert child.level == logging.DEBUG
        assert child.propagate is False
    # Should restore to info/True (outer context / original)
    assert child.level == orig_level
    assert child.propagate == orig_propagate


def test_use_level_and_propagate_restores_on_exception() -> None:
    """useLevelAndPropagate() should restore settings even if exception occurs."""
    # --- setup ---
    child = mod_alogs.Logger("test_use_level_and_propagate_exception")
    orig_level = child.level
    orig_propagate = child.propagate

    # --- execute ---
    test_exception_msg = "Test exception"
    try:
        with child.useLevelAndPropagate("debug"):
            assert child.level == logging.DEBUG
            assert child.propagate is False
            raise ValueError(test_exception_msg)  # noqa: TRY301
    except ValueError:
        pass

    # --- verify restoration ---
    assert child.level == orig_level
    assert child.propagate == orig_propagate
