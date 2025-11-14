# tests/3_independant/test_register_logger_name.py
"""Tests for register_logger_name function."""

import sys

import pytest

import apathetic_logging as mod_alogs
from apathetic_logging.registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)


@pytest.fixture(autouse=True)
def reset_registry() -> None:
    """Reset registry state before and after each test."""
    # Save original values
    original_env_vars = (
        ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars
    )
    original_default = ApatheticLogging_Priv_Registry.registered_priv_default_log_level
    original_name = ApatheticLogging_Priv_Registry.registered_priv_logger_name

    # Reset to None
    ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars = None
    ApatheticLogging_Priv_Registry.registered_priv_default_log_level = None
    ApatheticLogging_Priv_Registry.registered_priv_logger_name = None

    yield

    # Restore original values
    ApatheticLogging_Priv_Registry.registered_priv_log_level_env_vars = (
        original_env_vars
    )
    ApatheticLogging_Priv_Registry.registered_priv_default_log_level = original_default
    ApatheticLogging_Priv_Registry.registered_priv_logger_name = original_name


def test_register_logger_name_explicit_name() -> None:
    """register_logger_name() should store explicit logger name."""
    # --- setup ---
    logger_name = "my_app"

    # --- execute ---
    mod_alogs.register_logger_name(logger_name)

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_logger_name == logger_name


def test_register_logger_name_overwrites_previous() -> None:
    """register_logger_name() should overwrite previous value."""
    # --- setup ---
    mod_alogs.register_logger_name("old_name")

    # --- execute ---
    mod_alogs.register_logger_name("new_name")

    # --- verify ---
    assert ApatheticLogging_Priv_Registry.registered_priv_logger_name == "new_name"


def test_register_logger_name_auto_infer_from_package() -> None:
    """register_logger_name() should auto-infer from __package__ when None."""
    # --- setup ---
    # Mock the namespace module to have a __package__ attribute
    namespace_module = sys.modules.get("apathetic_logging.namespace")
    if namespace_module is None:
        pytest.skip("Cannot test auto-inference without namespace module")

    original_package = getattr(namespace_module, "__package__", None)

    # --- execute ---
    try:
        # Set a test package name
        namespace_module.__package__ = "test_package.submodule"
        mod_alogs.register_logger_name()

        # --- verify ---
        assert (
            ApatheticLogging_Priv_Registry.registered_priv_logger_name == "test_package"
        )
    finally:
        # Restore original package
        if original_package is not None:
            namespace_module.__package__ = original_package
        else:
            delattr(namespace_module, "__package__")


def test_register_logger_name_auto_infer_single_package() -> None:
    """register_logger_name() should handle single-level package."""
    # --- setup ---
    namespace_module = sys.modules.get("apathetic_logging.namespace")
    if namespace_module is None:
        pytest.skip("Cannot test auto-inference without namespace module")

    original_package = getattr(namespace_module, "__package__", None)

    # --- execute ---
    try:
        namespace_module.__package__ = "singlepackage"
        mod_alogs.register_logger_name()

        # --- verify ---
        assert (
            ApatheticLogging_Priv_Registry.registered_priv_logger_name
            == "singlepackage"
        )
    finally:
        # Restore original package
        if original_package is not None:
            namespace_module.__package__ = original_package
        else:
            delattr(namespace_module, "__package__")


def test_register_logger_name_auto_infer_fails_without_package() -> None:
    """register_logger_name() should raise RuntimeError if __package__ missing."""
    # --- setup ---
    namespace_module = sys.modules.get("apathetic_logging.namespace")
    if namespace_module is None:
        pytest.skip("Cannot test auto-inference without namespace module")

    original_package = getattr(namespace_module, "__package__", None)

    # --- execute and verify ---
    try:
        # Remove __package__ attribute
        if hasattr(namespace_module, "__package__"):
            delattr(namespace_module, "__package__")

        with pytest.raises(RuntimeError, match="Cannot auto-infer logger name"):
            mod_alogs.register_logger_name()
    finally:
        # Restore original package
        if original_package is not None:
            namespace_module.__package__ = original_package
