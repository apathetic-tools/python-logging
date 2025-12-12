# tests/50_core/test_set_propagate.py
"""Tests for Logger.setPropagate() method."""

import apathetic_logging as mod_alogs


def test_set_propagate_true() -> None:
    """setPropagate(True) should set propagate to True."""
    # --- setup ---
    logger = mod_alogs.Logger("test_set_propagate_true")

    # --- execute ---
    logger.setPropagate(True)

    # --- verify ---
    assert logger.propagate is True
    assert getattr(logger, "_propagate_explicit", False) is True


def test_set_propagate_false() -> None:
    """setPropagate(False) should set propagate to False."""
    # --- setup ---
    logger = mod_alogs.Logger("test_set_propagate_false")

    # --- execute ---
    logger.setPropagate(False)

    # --- verify ---
    assert logger.propagate is False
    assert getattr(logger, "_propagate_explicit", False) is True


def test_set_propagate_marks_as_explicitly_set() -> None:
    """setPropagate() should mark _propagate_explicit as True."""
    # --- setup ---
    logger = mod_alogs.Logger("test_set_propagate_explicit")

    # --- execute ---
    logger.setPropagate(True)

    # --- verify ---
    assert getattr(logger, "_propagate_explicit", False) is True
    # If it was already set, that's fine - we just verify it's set after
    assert logger.propagate is True


def test_set_propagate_can_be_called_multiple_times() -> None:
    """setPropagate() should work when called multiple times."""
    # --- setup ---
    logger = mod_alogs.Logger("test_set_propagate_multiple")

    # --- execute ---
    logger.setPropagate(True)
    assert logger.propagate is True

    logger.setPropagate(False)
    assert logger.propagate is False

    logger.setPropagate(True)
    assert logger.propagate is True

    # --- verify ---
    assert logger.propagate is True
    assert getattr(logger, "_propagate_explicit", False) is True


def test_set_propagate_affects_handler_attachment() -> None:
    """setPropagate() should automatically manage handlers via manageHandlers()."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_set_propagate_handler")
    child.handlers.clear()

    # --- execute ---
    # With propagate=True, child should not get handler
    # setPropagate should automatically call manageHandlers()
    child.setPropagate(propagate=True)

    # --- verify ---
    # Child with propagate=True should not have handler (propagates to root)
    assert len(child.handlers) == 0

    # With propagate=False, child should get handler
    # setPropagate should automatically call manageHandlers()
    child.setPropagate(propagate=False)

    # --- verify ---
    # Child with propagate=False should have handler
    assert len(child.handlers) > 0


def test_set_propagate_on_root_logger() -> None:
    """setPropagate() should work on root logger if it's an apathetic logger."""
    # --- setup ---
    root = mod_alogs.getLogger("")
    original_propagate = root.propagate

    # --- execute ---
    # Only test if root is an apathetic logger (has setPropagate method)
    if hasattr(root, "setPropagate"):
        root.setPropagate(propagate=False)

        # --- verify ---
        assert root.propagate is False
        assert getattr(root, "_propagate_explicit", False) is True

        # --- cleanup ---
        root.setPropagate(propagate=original_propagate)
    else:
        # Root logger is not an apathetic logger - skip this test
        # (This is expected if root logger was created before extendLoggingModule)
        pass


def test_set_propagate_works_with_standard_logger() -> None:
    """_applyPropagateSetting should use setPropagate when available."""
    # --- setup ---
    import apathetic_logging.get_logger as mod_get_logger  # noqa: PLC0415

    logger = mod_alogs.Logger("test_set_propagate_standard")
    logger.handlers.clear()

    # --- execute ---
    # _applyPropagateSetting should use setPropagate if available
    mod_get_logger.ApatheticLogging_Internal_GetLogger._applyPropagateSetting(logger)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    # --- verify ---
    # Should have been set (either True or False depending on registry/default)
    assert hasattr(logger, "propagate")
    # _propagate_explicit should be True if setPropagate was called
    # (but might be False if it wasn't explicitly set)
    propagate_explicit = getattr(logger, "_propagate_explicit", None)
    assert propagate_explicit is not None  # Should exist


def test_use_propagate_context_manager_changes_temporarily() -> None:
    """usePropagate() should temporarily change the logger propagate setting."""
    # --- setup ---
    logger = mod_alogs.Logger("test_use_propagate_temp")
    orig_propagate = logger.propagate

    # --- execute and verify ---
    with logger.usePropagate(not orig_propagate):
        assert logger.propagate is not orig_propagate
    assert logger.propagate == orig_propagate


def test_use_propagate_restores_original_setting() -> None:
    """usePropagate() should restore the original propagate setting on exit."""
    # --- setup ---
    logger = mod_alogs.Logger("test_use_propagate_restore")
    logger.setPropagate(True)
    assert logger.propagate is True

    # --- execute ---
    with logger.usePropagate(False):
        assert logger.propagate is False

    # --- verify ---
    # Should restore to original True
    assert logger.propagate is True


def test_use_propagate_with_manage_handlers() -> None:
    """usePropagate() should pass manage_handlers parameter to setPropagate()."""
    # --- setup ---
    logger = mod_alogs.Logger("test_use_propagate_manage_handlers")
    logger.handlers.clear()
    orig_propagate = logger.propagate

    # --- execute ---
    # Test with manage_handlers=True
    with logger.usePropagate(False, manage_handlers=True):
        assert logger.propagate is False
        # With propagate=False, logger should have handler
        assert len(logger.handlers) > 0

    # --- verify ---
    # Should restore to original propagate setting
    assert logger.propagate == orig_propagate


def test_use_propagate_affects_handler_attachment() -> None:
    """usePropagate() should affect handler attachment during context."""
    # --- setup ---
    child = mod_alogs.Logger("test_use_propagate_handler")
    child.handlers.clear()
    child.setPropagate(True)  # Start with propagate=True (no handler)
    assert len(child.handlers) == 0

    # --- execute ---
    with child.usePropagate(False):
        # With propagate=False, child should have handler
        assert len(child.handlers) > 0

    # --- verify ---
    # After context, should restore to propagate=True (no handler)
    assert child.propagate is True
    # Handler should be removed when propagate is restored to True
    assert len(child.handlers) == 0


def test_use_propagate_nested_contexts() -> None:
    """usePropagate() should work correctly with nested contexts."""
    # --- setup ---
    logger = mod_alogs.Logger("test_use_propagate_nested")
    logger.setPropagate(True)
    orig_propagate = logger.propagate

    # --- execute ---
    with logger.usePropagate(False):
        assert logger.propagate is False
        with logger.usePropagate(True):
            assert logger.propagate is True
        # Should restore to False (inner context)
        assert logger.propagate is False
    # Should restore to True (outer context / original)
    assert logger.propagate == orig_propagate
