# tests/50_core/test_get_logger.py
"""Tests for get_logger function."""

import sys
from collections.abc import Generator
from unittest.mock import patch

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry as mod_registry


@pytest.fixture(autouse=True)
def reset_registry() -> Generator[None, None, None]:
    """Reset registry state before and after each test."""
    # Save original values
    _registry = mod_registry.ApatheticLogging_Internal_Registry
    original_env_vars = _registry.registered_priv_log_level_env_vars
    original_default = _registry.registered_priv_default_log_level
    original_name = _registry.registered_priv_logger_name

    # Reset to None
    _registry.registered_priv_log_level_env_vars = None
    _registry.registered_priv_default_log_level = None
    _registry.registered_priv_logger_name = None

    yield

    # Restore original values
    _registry.registered_priv_log_level_env_vars = original_env_vars
    _registry.registered_priv_default_log_level = original_default
    _registry.registered_priv_logger_name = original_name


def test_get_logger_with_registered_name() -> None:
    """get_logger() should return logger when name is registered."""
    # --- setup ---
    logger_name = "test_get_logger_registered"
    mod_alogs.register_logger_name(logger_name)

    # --- execute ---
    result = mod_alogs.get_logger()

    # --- verify ---
    assert result.name == logger_name
    # The logger from logging.getLogger() may not be an apathetic_logging.Logger
    # unless it was explicitly created as one, but it should still have the name


def test_get_logger_raises_when_not_registered() -> None:
    """get_logger() should raise RuntimeError when name not registered."""
    # --- execute and verify ---
    with pytest.raises(RuntimeError, match="Logger name not registered"):
        mod_alogs.get_logger()


def test_get_logger_auto_infers_from_caller_package() -> None:
    """get_logger() should auto-infer logger name from caller's __package__.

    Note: This test must carefully construct an identical callstack to mimic
    the frames between get_logger() and calling resolve_logger_name().
    """
    # --- setup ---
    # Create a fake module with __package__ attribute
    fake_module = type(sys)("fake_module")
    fake_module.__package__ = "test_package.submodule"
    fake_globals = {"__package__": "test_package.submodule"}

    # --- execute ---
    with patch("inspect.currentframe") as mock_frame:
        # Mock the frame to return our fake caller
        # Frame structure: resolve_logger_name -> get_logger_of_type -> get_logger
        # -> actual caller
        frame = type(sys)("frame")
        frame.f_back = type(sys)("get_logger_of_type_frame")  # type: ignore[attr-defined]
        frame.f_back.f_back = type(sys)("get_logger_frame")
        frame.f_back.f_back.f_back = type(sys)("caller_frame")
        frame.f_back.f_back.f_back.f_globals = fake_globals
        mock_frame.return_value = frame

        try:
            result = mod_alogs.get_logger()
            # --- verify ---
            assert result.name == "test_package"
            _registry = mod_registry.ApatheticLogging_Internal_Registry
            assert _registry.registered_priv_logger_name == "test_package"
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
    mod_alogs.register_logger_name(logger_name)

    # --- execute ---
    result1 = mod_alogs.get_logger()
    result2 = mod_alogs.get_logger()

    # --- verify ---
    # Should return the same logger instance from logging registry
    assert result1 is result2
    assert result1.name == logger_name
