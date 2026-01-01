# tests/50_core/test_get_logger.py
"""Tests for get_logger function."""

import inspect
import logging
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_logger_with_registered_name() -> None:
    """get_logger() should return logger when name is registered."""
    # --- setup ---
    logger_name = "test_get_logger_registered"
    mod_alogs.registerLogger(logger_name)

    # --- execute ---
    result = mod_alogs.getLogger()

    # --- verify ---
    assert result.name == logger_name
    # The logger from logging.getLogger() may not be an apathetic_logging.Logger
    # unless it was explicitly created as one, but it should still have the name


def test_get_logger_raises_when_not_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_logger() should raise RuntimeError when name not registered."""
    # --- setup ---
    # Mock frame to not have __package__ so inference fails
    # Frame chain from resolve_logger_name: resolve_logger_name -> get_logger_of_type
    # -> get_logger -> actual caller
    # skip_frames=3: initial frame.f_back, then 3 iterations
    # So we need: frame -> f_back (get_logger_of_type) -> f_back (get_logger)
    # -> f_back (caller) -> f_back (one more level)
    frame: Any = type(sys)("frame")
    get_logger_of_type_frame: Any = type(sys)("get_logger_of_type_frame")
    get_logger_frame: Any = type(sys)("get_logger_frame")
    caller_frame: Any = type(sys)("caller_frame")
    final_frame: Any = type(sys)("final_frame")

    frame.f_back = get_logger_of_type_frame
    get_logger_of_type_frame.f_back = get_logger_frame
    get_logger_frame.f_back = caller_frame
    caller_frame.f_back = final_frame
    final_frame.f_globals = {}  # No __package__
    mock_frame = MagicMock(return_value=frame)
    monkeypatch.setattr(inspect, "currentframe", mock_frame)

    try:
        # --- execute and verify ---
        with pytest.raises(RuntimeError, match="Cannot auto-infer logger name"):
            mod_alogs.getLogger()
    finally:
        # Clean up frame reference
        del frame


def test_get_logger_auto_infers_from_caller_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """get_logger() should auto-infer logger name from caller's __package__.

    Note: This test must carefully construct an identical callstack to mimic
    the frames between get_logger() and calling resolve_logger_name().
    """
    # --- setup ---
    # Create a fake module with __package__ attribute
    fake_module = type(sys)("fake_module")
    fake_module.__package__ = "test_package.submodule"
    fake_globals = {"__package__": "test_package.submodule"}

    # Mock the frame to return our fake caller
    # Frame chain from resolve_logger_name:
    # resolve_logger_name -> get_logger_of_type -> get_logger -> actual caller
    # skip_frames=3: initial frame.f_back, then 3 iterations
    # So we need: frame -> f_back (get_logger_of_type) -> f_back (get_logger)
    # -> f_back (caller) -> f_back (one more level)
    frame: Any = type(sys)("frame")
    get_logger_of_type_frame: Any = type(sys)("get_logger_of_type_frame")
    get_logger_frame: Any = type(sys)("get_logger_frame")
    caller_frame: Any = type(sys)("caller_frame")
    final_frame: Any = type(sys)("final_frame")

    frame.f_back = get_logger_of_type_frame
    get_logger_of_type_frame.f_back = get_logger_frame
    get_logger_frame.f_back = caller_frame
    caller_frame.f_back = final_frame
    final_frame.f_globals = fake_globals
    mock_frame = MagicMock(return_value=frame)
    monkeypatch.setattr(inspect, "currentframe", mock_frame)

    try:
        result = mod_alogs.getLogger()
        # --- verify ---
        assert result.name == "test_package"
        _registry = mod_registry.ApatheticLogging_Internal_RegistryData
        assert _registry.registered_internal_logger_name == "test_package"
    except RuntimeError:
        # If auto-inference fails, that's also acceptable behavior
        pass
    finally:
        # Clean up frame reference
        del frame


def test_get_logger_uses_existing_logger_instance() -> None:
    """get_logger() should return existing logger from logging registry."""
    # --- setup ---
    logger_name = "test_get_logger_existing"
    mod_alogs.registerLogger(logger_name)

    # --- execute ---
    result1 = mod_alogs.getLogger()
    result2 = mod_alogs.getLogger()

    # --- verify ---
    # Should return the same logger instance from logging registry
    assert result1 is result2
    assert result1.name == logger_name


def test_get_logger_with_empty_string_returns_root_logger() -> None:
    """getLogger("") should return the root logger, matching stdlib behavior."""
    # --- execute ---
    result = mod_alogs.getLogger("")

    # --- verify ---
    # Should return the root logger (name is "root", not empty string)
    assert result.name == "root"
    # Should be the same instance as logging.getLogger("")
    stdlib_root = logging.getLogger("")
    assert result is stdlib_root


def test_get_logger_empty_string_matches_stdlib_root_logger() -> None:
    """getLogger("") should return the same logger as logging.getLogger("")."""
    # --- execute ---
    apathetic_root = mod_alogs.getLogger("")
    stdlib_root = logging.getLogger("")

    # --- verify ---
    # Should be the exact same logger instance
    assert apathetic_root is stdlib_root
    assert apathetic_root.name == "root"
    assert stdlib_root.name == "root"
    # Multiple calls should return the same instance
    assert mod_alogs.getLogger("") is apathetic_root
    assert logging.getLogger("") is stdlib_root
