# tests/30_independant/test_register_logger.py
"""Tests for register_logger function."""

import logging
import sys
from typing import Any
from unittest.mock import patch

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_logger_explicit_name() -> None:
    """register_logger() should store explicit logger name."""
    # --- setup ---
    logger_name = "my_app"

    # --- execute ---
    mod_alogs.register_logger(logger_name)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == logger_name


def test_register_logger_overwrites_previous() -> None:
    """register_logger() should overwrite previous value."""
    # --- setup ---
    mod_alogs.register_logger("old_name")

    # --- execute ---
    mod_alogs.register_logger("new_name")

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == "new_name"


def test_register_logger_auto_infer_from_package() -> None:
    """register_logger() should auto-infer from __package__ when None."""
    # --- setup ---
    # Mock frame to have __package__ in caller's globals
    # Frame chain: register_logger -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger) -> frame.f_back.f_back (caller)
    with patch("inspect.currentframe") as mock_frame:
        frame: Any = type(sys)("frame")
        frame.f_back = type(sys)("register_logger_frame")
        frame.f_back.f_back = type(sys)("caller_frame")
        frame.f_back.f_back.f_globals = {"__package__": "test_package.submodule"}
        mock_frame.return_value = frame

        try:
            # --- execute ---
            mod_alogs.register_logger()

            # --- verify ---
            _registry = mod_registry.ApatheticLogging_Internal_RegistryData
            assert _registry.registered_internal_logger_name == "test_package"
        finally:
            # Clean up frame reference
            del frame


def test_register_logger_auto_infer_single_package() -> None:
    """register_logger() should handle single-level package."""
    # --- setup ---
    # Mock frame to have __package__ in caller's globals
    # Frame chain: register_logger -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger) -> frame.f_back.f_back (caller)
    with patch("inspect.currentframe") as mock_frame:
        frame: Any = type(sys)("frame")
        frame.f_back = type(sys)("register_logger_frame")
        frame.f_back.f_back = type(sys)("caller_frame")
        frame.f_back.f_back.f_globals = {"__package__": "singlepackage"}
        mock_frame.return_value = frame

        try:
            # --- execute ---
            mod_alogs.register_logger()

            # --- verify ---
            _registry = mod_registry.ApatheticLogging_Internal_RegistryData
            assert _registry.registered_internal_logger_name == "singlepackage"
        finally:
            # Clean up frame reference
            del frame


def test_register_logger_auto_infer_fails_without_package() -> None:
    """register_logger() should raise RuntimeError if __package__ missing."""
    # --- setup ---
    # Mock frame to not have __package__ in caller's globals
    # Frame chain: register_logger -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger) -> frame.f_back.f_back (caller)
    with patch("inspect.currentframe") as mock_frame:
        frame: Any = type(sys)("frame")
        frame.f_back = type(sys)("register_logger_frame")
        frame.f_back.f_back = type(sys)("caller_frame")
        # No __package__ in caller's globals
        frame.f_back.f_back.f_globals = {}
        mock_frame.return_value = frame

        try:
            # --- execute and verify ---
            with pytest.raises(RuntimeError, match="Cannot auto-infer logger name"):
                mod_alogs.register_logger()
        finally:
            # Clean up frame reference
            del frame


def test_register_logger_extends_logging_module() -> None:
    """register_logger() should call extend_logging_module() on Logger class."""
    # --- setup ---
    # Verify TRACE exists (from import-time extension)
    # register_logger should ensure it's extended even if called again
    assert hasattr(logging, "TRACE")

    # --- execute ---
    # register_logger should extend the logging module
    mod_alogs.register_logger("test_extend")

    # --- verify ---
    # Should have extended logging module with custom levels
    assert hasattr(logging, "TRACE")
    assert hasattr(logging, "DETAIL")
    assert hasattr(logging, "MINIMAL")
    assert hasattr(logging, "SILENT")
    # Verify logger name was registered
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == "test_extend"


def test_register_logger_with_custom_class() -> None:
    """register_logger() should call extend_logging_module() on custom class."""

    # --- setup ---
    # Create a custom logger class
    class CustomLogger(mod_alogs.Logger):
        _logging_module_extended = False

        @classmethod
        def extend_logging_module(cls) -> bool:
            """Custom extend that sets a flag."""
            if cls._logging_module_extended:
                return False
            cls._logging_module_extended = True
            # Call parent to actually extend
            return super().extend_logging_module()

    # --- execute ---
    mod_alogs.register_logger("test_custom", CustomLogger)

    # --- verify ---
    # Should have called extend on custom class
    assert CustomLogger._logging_module_extended is True  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
    # Verify logger name was registered
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == "test_custom"
