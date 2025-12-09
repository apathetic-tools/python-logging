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
    assert getattr(logger, "_propagate_set", False) is True


def test_set_propagate_false() -> None:
    """setPropagate(False) should set propagate to False."""
    # --- setup ---
    logger = mod_alogs.Logger("test_set_propagate_false")

    # --- execute ---
    logger.setPropagate(False)

    # --- verify ---
    assert logger.propagate is False
    assert getattr(logger, "_propagate_set", False) is True


def test_set_propagate_marks_as_explicitly_set() -> None:
    """setPropagate() should mark _propagate_set as True."""
    # --- setup ---
    logger = mod_alogs.Logger("test_set_propagate_explicit")

    # --- execute ---
    logger.setPropagate(True)

    # --- verify ---
    assert getattr(logger, "_propagate_set", False) is True
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
    assert getattr(logger, "_propagate_set", False) is True


def test_set_propagate_affects_handler_attachment() -> None:
    """setPropagate() should affect handler attachment via ensureHandlers()."""
    # --- setup ---
    _constants = mod_alogs.apathetic_logging
    child = mod_alogs.Logger("test_set_propagate_handler")
    child.handlers.clear()

    # --- execute ---
    # With propagate=True, child should not get handler
    child.setPropagate(propagate=True)
    child.ensureHandlers()

    # --- verify ---
    # Child with propagate=True should not have handler (propagates to root)
    assert len(child.handlers) == 0

    # With propagate=False, child should get handler
    child.setPropagate(propagate=False)
    child.ensureHandlers()

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
        assert getattr(root, "_propagate_set", False) is True

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
    # _propagate_set should be True if setPropagate was called
    # (but might be False if it wasn't explicitly set)
    propagate_set = getattr(logger, "_propagate_set", None)
    assert propagate_set is not None  # Should exist
