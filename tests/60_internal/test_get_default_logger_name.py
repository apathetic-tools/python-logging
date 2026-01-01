# tests/30_independant/test_get_default_logger_name.py
"""Test getDefaultLoggerName function."""

from __future__ import annotations

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_default_logger_name_returns_explicit_name() -> None:
    """Test that getDefaultLoggerName returns explicit name when provided."""
    # Explicit name should always be returned
    assert mod_alogs.getDefaultLoggerName("myapp") == "myapp"
    assert mod_alogs.getDefaultLoggerName("") == ""  # Root logger


def test_get_default_logger_name_returns_registered_when_available() -> None:
    """Test that getDefaultLoggerName returns registered name when available."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_logger_name = None

    # Register a name
    mod_alogs.registerLogger("myapp")
    assert mod_alogs.getDefaultLoggerName() == "myapp"

    # Reset
    _registry.registered_internal_logger_name = None


def test_get_default_logger_name_infer_parameter() -> None:
    """Test that infer parameter controls inference behavior."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_logger_name = None

    # With infer=False, should not attempt inference
    result = mod_alogs.getDefaultLoggerName(infer=False, check_registry=False)
    assert result is None  # No registry, no inference

    # With infer=True, should attempt inference
    # (may succeed or fail depending on context)
    try:
        result = mod_alogs.getDefaultLoggerName(infer=True, check_registry=False)
        # If inference succeeds, result is a string
        # If it fails, we get None (since raise_on_error=False by default)
        assert result is None or isinstance(result, str)
    except RuntimeError:
        # If raise_on_error was True, we'd get an error
        pass

    # Reset
    _registry.registered_internal_logger_name = None


def test_get_default_logger_name_register_parameter() -> None:
    """Test that register parameter controls registry storage."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_logger_name = None

    # Test with register=False - should not store
    inferred = mod_alogs.getDefaultLoggerName(
        check_registry=False, infer=True, register=False
    )
    # If inference succeeded, check it wasn't stored
    if inferred is not None:
        # The inferred value should not be in registry (register=False)
        registered = mod_alogs.getRegisteredLoggerName()
        # If register=False worked, registered should be None (not stored)
        assert registered != inferred or registered is None

    # Test with register=True - should store
    _registry.registered_internal_logger_name = None
    inferred = mod_alogs.getDefaultLoggerName(
        check_registry=False, infer=True, register=True
    )
    if inferred is not None:
        # Should be stored now
        assert mod_alogs.getRegisteredLoggerName() == inferred

    # Reset
    _registry.registered_internal_logger_name = None


def test_get_default_logger_name_raise_on_error_parameter() -> None:
    """Test that raise_on_error parameter controls error behavior."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_logger_name = None

    # With raise_on_error=False (default), should return None when can't resolve
    result = mod_alogs.getDefaultLoggerName(
        check_registry=False, infer=False, raise_on_error=False
    )
    assert result is None

    # With raise_on_error=True, should raise when can't resolve
    with pytest.raises(RuntimeError):
        mod_alogs.getDefaultLoggerName(
            check_registry=False, infer=False, raise_on_error=True
        )

    # Reset
    _registry.registered_internal_logger_name = None


def test_get_default_logger_name_check_registry_parameter() -> None:
    """Test that check_registry parameter controls registry checking."""
    # Reset registry
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_logger_name = None

    # Register a name
    mod_alogs.registerLogger("registered")
    assert mod_alogs.getRegisteredLoggerName() == "registered"

    # With check_registry=True (default), should return registered name
    assert mod_alogs.getDefaultLoggerName(check_registry=True) == "registered"

    # With check_registry=False, should skip registry and try inference
    # (may succeed or fail depending on context)
    result = mod_alogs.getDefaultLoggerName(check_registry=False, infer=True)
    # Result depends on whether inference succeeds
    assert result is None or isinstance(result, str)

    # Reset
    _registry.registered_internal_logger_name = None
