# tests/50_core/test_manage_handlers_features.py
"""Tests for manageHandlers() new features."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs


def test_manage_handlers_only_manages_apathetic_handlers() -> None:
    """manageHandlers() should only manage DualStreamHandler, not user handlers."""
    # --- setup ---
    child = mod_alogs.Logger("test_manage_only_apathetic")
    child.setPropagate(propagate=False)
    child.handlers.clear()

    # Add a user handler (not DualStreamHandler)
    user_handler = logging.StreamHandler()
    child.addHandler(user_handler)

    # --- execute ---
    # Trigger manageHandlers by logging
    child.info("test message")

    # --- verify ---
    # Should have both apathetic handler and user handler
    handlers = child.handlers
    assert len(handlers) == 2  # noqa: PLR2004
    assert any(isinstance(h, mod_alogs.DualStreamHandler) for h in handlers)
    assert any(
        isinstance(h, logging.StreamHandler)
        and not isinstance(h, mod_alogs.DualStreamHandler)
        for h in handlers
    )


def test_manage_handlers_does_not_remove_manually_added_handlers() -> None:
    """manageHandlers() should not remove manually-added handlers.

    When handlers are manually added to propagating loggers, they should
    not be removed by manageHandlers().
    """
    # --- setup ---
    child = mod_alogs.Logger("test_manage_no_remove_manual")
    child.setPropagate(propagate=True)
    child.handlers.clear()

    # Manually add a DualStreamHandler (simulating user adding it)
    manual_handler = mod_alogs.DualStreamHandler()
    child.addHandler(manual_handler)

    # --- execute ---
    # Trigger manageHandlers by logging
    # Since _last_stream_ids is None, it shouldn't remove the handler
    child.info("test message")

    # --- verify ---
    # Handler should still be there (not removed because we didn't manage it before)
    assert len(child.handlers) == 1
    assert isinstance(child.handlers[0], mod_alogs.DualStreamHandler)


def test_manage_handlers_removes_previously_managed_handlers() -> None:
    """manageHandlers() should remove handlers it previously managed.

    When a logger switches to propagate=True, handlers that were previously
    managed by manageHandlers() should be removed.
    """
    # --- setup ---
    child = mod_alogs.Logger("test_manage_remove_previous")
    child.setPropagate(propagate=False)
    child.handlers.clear()

    # Trigger handler creation (this sets _last_stream_ids)
    child.info("first message")
    assert len(child.handlers) > 0
    assert hasattr(child, "_last_stream_ids")
    assert getattr(child, "_last_stream_ids", None) is not None

    # Now switch to propagate=True
    child.setPropagate(propagate=True)

    # --- execute ---
    # Trigger manageHandlers by logging
    child.info("second message")

    # --- verify ---
    # Handler should be removed (because we previously managed it)
    assert len(child.handlers) == 0


def test_manage_handlers_with_manage_handlers_true() -> None:
    """manageHandlers(manage_handlers=True) should always manage handlers."""
    # --- setup ---
    child = mod_alogs.Logger("test_manage_explicit_true")
    child.setPropagate(propagate=False)
    child.handlers.clear()

    # --- execute ---
    child.manageHandlers(manage_handlers=True)

    # --- verify ---
    assert len(child.handlers) > 0
    assert any(isinstance(h, mod_alogs.DualStreamHandler) for h in child.handlers)


def test_manage_handlers_with_manage_handlers_false() -> None:
    """manageHandlers(manage_handlers=False) should not manage handlers."""
    # --- setup ---
    child = mod_alogs.Logger("test_manage_explicit_false")
    child.setPropagate(propagate=False)
    child.handlers.clear()

    # --- execute ---
    child.manageHandlers(manage_handlers=False)

    # --- verify ---
    # Should not have added handlers
    assert len(child.handlers) == 0


def test_manage_handlers_respects_compat_mode() -> None:
    """manageHandlers() should not manage handlers in compat mode.

    In compatibility mode, manageHandlers() should not manage handlers unless
    explicitly requested via manage_handlers=True.
    """
    # --- setup ---
    import apathetic_logging.registry_data as mod_registry_data  # noqa: PLC0415

    _registry_data = mod_registry_data.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry_data.registered_internal_compatibility_mode

    try:
        # Enable compat mode
        mod_alogs.registerCompatibilityMode(compat_mode=True)

        child = mod_alogs.Logger("test_manage_compat_mode")
        child.setPropagate(propagate=False)
        child.handlers.clear()

        # --- execute ---
        # manageHandlers() with None should not manage in compat mode
        child.manageHandlers(manage_handlers=None)

        # --- verify ---
        # Should not have added handlers (compat mode prevents it)
        assert len(child.handlers) == 0

        # But explicit True should still work
        child.manageHandlers(manage_handlers=True)
        assert len(child.handlers) > 0

    finally:
        # Restore original compat mode
        _registry_data.registered_internal_compatibility_mode = original_compat_mode


def test_set_propagate_manages_handlers_by_default() -> None:
    """setPropagate() should manage handlers by default."""
    # --- setup ---
    child = mod_alogs.Logger("test_set_propagate_manages")
    child.setPropagate(propagate=False)
    child.handlers.clear()

    # --- execute ---
    # setPropagate should call manageHandlers automatically
    child.setPropagate(propagate=False)

    # --- verify ---
    # Should have handler (propagate=False means it needs one)
    assert len(child.handlers) > 0


def test_set_propagate_with_manage_handlers_false() -> None:
    """setPropagate(manage_handlers=False) should not manage handlers."""
    # --- setup ---
    child = mod_alogs.Logger("test_set_propagate_no_manage")
    child.setPropagate(propagate=False)
    child.handlers.clear()

    # --- execute ---
    child.setPropagate(propagate=False, manage_handlers=False)

    # --- verify ---
    # Should not have handler (manage_handlers=False prevents management)
    assert len(child.handlers) == 0


def test_set_propagate_with_manage_handlers_true() -> None:
    """setPropagate(manage_handlers=True) should manage handlers even in compat mode."""
    # --- setup ---
    import apathetic_logging.registry_data as mod_registry_data  # noqa: PLC0415

    _registry_data = mod_registry_data.ApatheticLogging_Internal_RegistryData
    original_compat_mode = _registry_data.registered_internal_compatibility_mode

    try:
        # Enable compat mode
        mod_alogs.registerCompatibilityMode(compat_mode=True)

        child = mod_alogs.Logger("test_set_propagate_explicit_manage")
        child.setPropagate(propagate=False)
        child.handlers.clear()

        # --- execute ---
        # Explicit manage_handlers=True should work even in compat mode
        child.setPropagate(propagate=False, manage_handlers=True)

        # --- verify ---
        assert len(child.handlers) > 0

    finally:
        # Restore original compat mode
        _registry_data.registered_internal_compatibility_mode = original_compat_mode


def test_set_propagate_switching_propagate_manages_handlers() -> None:
    """setPropagate() should manage handlers when switching propagate setting."""
    # --- setup ---
    child = mod_alogs.Logger("test_set_propagate_switch")
    child.setPropagate(propagate=False)
    child.handlers.clear()

    # First, set propagate=False (should add handler)
    child.setPropagate(propagate=False)
    assert len(child.handlers) > 0

    # --- execute ---
    # Switch to propagate=True (should remove handler)
    child.setPropagate(propagate=True)

    # --- verify ---
    # Handler should be removed (propagating loggers don't need handlers)
    assert len(child.handlers) == 0

    # Switch back to propagate=False (should add handler again)
    child.setPropagate(propagate=False)
    assert len(child.handlers) > 0
