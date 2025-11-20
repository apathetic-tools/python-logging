# tests/30_independant/test_register_logger_name.py
"""Tests for register_logger_name function."""

import sys
from typing import Any
from unittest.mock import patch

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_logger_name_explicit_name() -> None:
    """register_logger_name() should store explicit logger name."""
    # --- setup ---
    logger_name = "my_app"

    # --- execute ---
    mod_alogs.register_logger_name(logger_name)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == logger_name


def test_register_logger_name_overwrites_previous() -> None:
    """register_logger_name() should overwrite previous value."""
    # --- setup ---
    mod_alogs.register_logger_name("old_name")

    # --- execute ---
    mod_alogs.register_logger_name("new_name")

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == "new_name"


def test_register_logger_name_auto_infer_from_package() -> None:
    """register_logger_name() should auto-infer from __package__ when None."""
    # --- setup ---
    # Mock frame to have __package__ in caller's globals
    # Frame chain: register_logger_name -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger_name) -> frame.f_back.f_back (caller)
    with patch("inspect.currentframe") as mock_frame:
        frame: Any = type(sys)("frame")
        frame.f_back = type(sys)("register_logger_name_frame")
        frame.f_back.f_back = type(sys)("caller_frame")
        frame.f_back.f_back.f_globals = {"__package__": "test_package.submodule"}
        mock_frame.return_value = frame

        try:
            # --- execute ---
            mod_alogs.register_logger_name()

            # --- verify ---
            _registry = mod_registry.ApatheticLogging_Internal_RegistryData
            assert _registry.registered_internal_logger_name == "test_package"
        finally:
            # Clean up frame reference
            del frame


def test_register_logger_name_auto_infer_single_package() -> None:
    """register_logger_name() should handle single-level package."""
    # --- setup ---
    # Mock frame to have __package__ in caller's globals
    # Frame chain: register_logger_name -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger_name) -> frame.f_back.f_back (caller)
    with patch("inspect.currentframe") as mock_frame:
        frame: Any = type(sys)("frame")
        frame.f_back = type(sys)("register_logger_name_frame")
        frame.f_back.f_back = type(sys)("caller_frame")
        frame.f_back.f_back.f_globals = {"__package__": "singlepackage"}
        mock_frame.return_value = frame

        try:
            # --- execute ---
            mod_alogs.register_logger_name()

            # --- verify ---
            _registry = mod_registry.ApatheticLogging_Internal_RegistryData
            assert _registry.registered_internal_logger_name == "singlepackage"
        finally:
            # Clean up frame reference
            del frame


def test_register_logger_name_auto_infer_fails_without_package() -> None:
    """register_logger_name() should raise RuntimeError if __package__ missing."""
    # --- setup ---
    # Mock frame to not have __package__ in caller's globals
    # Frame chain: register_logger_name -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger_name) -> frame.f_back.f_back (caller)
    with patch("inspect.currentframe") as mock_frame:
        frame: Any = type(sys)("frame")
        frame.f_back = type(sys)("register_logger_name_frame")
        frame.f_back.f_back = type(sys)("caller_frame")
        # No __package__ in caller's globals
        frame.f_back.f_back.f_globals = {}
        mock_frame.return_value = frame

        try:
            # --- execute and verify ---
            with pytest.raises(RuntimeError, match="Cannot auto-infer logger name"):
                mod_alogs.register_logger_name()
        finally:
            # Clean up frame reference
            del frame
