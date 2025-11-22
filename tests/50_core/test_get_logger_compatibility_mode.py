# tests/50_core/test_get_logger_compatibility_mode.py
"""Tests for getLogger compatibility mode behavior."""

from __future__ import annotations

import logging

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_get_logger_none_returns_root_in_compatibility_mode() -> None:
    """getLogger(None) should return root logger when compatibility mode enabled."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = True

    try:
        # --- execute ---
        result = mod_alogs.getLogger(None)

        # --- verify ---
        # Should return root logger (name is "root")
        assert result.name == "root"
        assert result is logging.getLogger()  # Root logger
    finally:
        # Reset
        _registry.registered_internal_compatibility_mode = None


def test_get_logger_none_auto_infers_when_compatibility_mode_disabled() -> None:
    """getLogger(None) should auto-infer when compatibility mode disabled."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = False
    # Register a logger name so inference doesn't fail
    mod_alogs.registerLogger("test_package")

    try:
        # --- execute ---
        result = mod_alogs.getLogger(None)

        # --- verify ---
        # Should return registered logger, not root
        assert result.name == "test_package"
        assert result.name != ""  # Not root logger
    finally:
        # Reset
        _registry.registered_internal_compatibility_mode = None
        _registry.registered_internal_logger_name = None


def test_get_logger_none_defaults_to_auto_infer() -> None:
    """getLogger(None) should default to auto-infer when compatibility mode not set."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = None
    # Register a logger name so inference doesn't fail
    mod_alogs.registerLogger("test_package")

    try:
        # --- execute ---
        result = mod_alogs.getLogger(None)

        # --- verify ---
        # Should return registered logger, not root (default is False)
        assert result.name == "test_package"
        assert result.name != ""  # Not root logger
    finally:
        # Reset
        _registry.registered_internal_compatibility_mode = None
        _registry.registered_internal_logger_name = None


def test_register_logger_with_compatibility_mode() -> None:
    """registerLogger() should accept compatibility_mode parameter."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = None

    try:
        # --- execute ---
        mod_alogs.registerLogger("test_package", compat_mode=True)

        # --- verify ---
        assert _registry.registered_internal_compatibility_mode is True

        # Change via registerLogger
        mod_alogs.registerLogger("test_package", compat_mode=False)
        assert _registry.registered_internal_compatibility_mode is False
    finally:
        # Reset
        _registry.registered_internal_compatibility_mode = None
        _registry.registered_internal_logger_name = None


def test_register_logger_snake_case_with_compatibility_mode() -> None:
    """register_logger() should accept compatibility_mode parameter."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _registry.registered_internal_compatibility_mode = None

    try:
        # --- execute ---
        mod_alogs.registerLogger("test_package", compat_mode=True)

        # --- verify ---
        assert _registry.registered_internal_compatibility_mode is True
    finally:
        # Reset
        _registry.registered_internal_compatibility_mode = None
        _registry.registered_internal_logger_name = None
