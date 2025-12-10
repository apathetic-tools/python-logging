# tests/30_independant/test_register_replace_root_logger.py
"""Tests for registerReplaceRootLogger() function."""

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_replace_root_logger_stores_value() -> None:
    """registerReplaceRootLogger() should store the value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_replace_root_logger

    # --- execute ---
    mod_alogs.registerReplaceRootLogger(replace_root=False)

    # --- verify ---
    assert _registry.registered_internal_replace_root_logger is False

    # --- cleanup ---
    _registry.registered_internal_replace_root_logger = original_value


def test_register_replace_root_logger_overwrites_previous() -> None:
    """registerReplaceRootLogger() should overwrite previous value."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_replace_root_logger

    # Set initial value
    mod_alogs.registerReplaceRootLogger(replace_root=False)

    # --- execute ---
    mod_alogs.registerReplaceRootLogger(replace_root=True)

    # --- verify ---
    assert _registry.registered_internal_replace_root_logger is True

    # --- cleanup ---
    _registry.registered_internal_replace_root_logger = original_value


def test_register_replace_root_logger_accepts_none() -> None:
    """registerReplaceRootLogger() should accept None and skip registration."""
    # --- setup ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_replace_root_logger

    # Set initial value
    mod_alogs.registerReplaceRootLogger(replace_root=False)

    # --- execute ---
    mod_alogs.registerReplaceRootLogger(replace_root=None)

    # --- verify ---
    # Value should be unchanged (None means skip)
    assert _registry.registered_internal_replace_root_logger is False

    # --- cleanup ---
    _registry.registered_internal_replace_root_logger = original_value


@pytest.mark.parametrize("replace_root", [True, False])
def test_register_replace_root_logger_accepts_boolean_values(
    replace_root: bool,  # noqa: FBT001
) -> None:
    """registerReplaceRootLogger() should accept True and False."""
    # --- setup ---

    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_value = _registry.registered_internal_replace_root_logger

    # --- execute ---
    mod_alogs.registerReplaceRootLogger(replace_root=replace_root)

    # --- verify ---
    assert _registry.registered_internal_replace_root_logger is replace_root

    # --- cleanup ---
    _registry.registered_internal_replace_root_logger = original_value
