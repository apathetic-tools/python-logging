# tests/30_independant/test_register_logger.py
"""Tests for register_logger function."""

import inspect
import logging
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


def test_register_logger_explicit_name() -> None:
    """register_logger() should store explicit logger name."""
    # --- setup ---
    logger_name = "my_app"

    # --- execute ---
    mod_alogs.registerLogger(logger_name)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == logger_name


def test_register_logger_overwrites_previous() -> None:
    """register_logger() should overwrite previous value."""
    # --- setup ---
    mod_alogs.registerLogger("old_name")

    # --- execute ---
    mod_alogs.registerLogger("new_name")

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == "new_name"


def test_register_logger_auto_infer_from_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """register_logger() should auto-infer from __package__ when None."""
    # --- setup ---
    # Mock frame to have __package__ in caller's globals
    # Frame chain: register_logger -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger) -> frame.f_back.f_back (caller)
    frame: Any = type(sys)("frame")
    frame.f_back = type(sys)("register_logger_frame")
    frame.f_back.f_back = type(sys)("caller_frame")
    frame.f_back.f_back.f_globals = {"__package__": "test_package.submodule"}
    mock_frame = MagicMock(return_value=frame)
    monkeypatch.setattr(inspect, "currentframe", mock_frame)

    try:
        # --- execute ---
        mod_alogs.registerLogger()

        # --- verify ---
        _registry = mod_registry.ApatheticLogging_Internal_RegistryData
        assert _registry.registered_internal_logger_name == "test_package"
    finally:
        # Clean up frame reference
        del frame


def test_register_logger_auto_infer_single_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """register_logger() should handle single-level package."""
    # --- setup ---
    # Mock frame to have __package__ in caller's globals
    # Frame chain: register_logger -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger) -> frame.f_back.f_back (caller)
    frame: Any = type(sys)("frame")
    frame.f_back = type(sys)("register_logger_frame")
    frame.f_back.f_back = type(sys)("caller_frame")
    frame.f_back.f_back.f_globals = {"__package__": "singlepackage"}
    mock_frame = MagicMock(return_value=frame)
    monkeypatch.setattr(inspect, "currentframe", mock_frame)

    try:
        # --- execute ---
        mod_alogs.registerLogger()

        # --- verify ---
        _registry = mod_registry.ApatheticLogging_Internal_RegistryData
        assert _registry.registered_internal_logger_name == "singlepackage"
    finally:
        # Clean up frame reference
        del frame


def test_register_logger_auto_infer_fails_without_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """register_logger() should raise RuntimeError if __package__ missing."""
    # --- setup ---
    # Mock frame to not have __package__ in caller's globals
    # Frame chain: register_logger -> resolve_logger_name -> _infer_from_frame
    # skip_frames=1 means we skip 1 frame from frame.f_back, so we need:
    # frame -> frame.f_back (register_logger) -> frame.f_back.f_back (caller)
    frame: Any = type(sys)("frame")
    frame.f_back = type(sys)("register_logger_frame")
    frame.f_back.f_back = type(sys)("caller_frame")
    # No __package__ in caller's globals
    frame.f_back.f_back.f_globals = {}
    mock_frame = MagicMock(return_value=frame)
    monkeypatch.setattr(inspect, "currentframe", mock_frame)

    try:
        # --- execute and verify ---
        with pytest.raises(RuntimeError, match="Cannot auto-infer logger name"):
            mod_alogs.registerLogger()
    finally:
        # Clean up frame reference
        del frame


def test_register_logger_extends_logging_module() -> None:
    """register_logger() should call extendLoggingModule() on Logger class."""
    # --- setup ---
    # Verify TRACE exists (from import-time extension)
    # register_logger should ensure it's extended even if called again
    assert hasattr(logging, "TRACE")

    # --- execute ---
    # register_logger should extend the logging module
    mod_alogs.registerLogger("test_extend")

    # --- verify ---
    # Should have extended logging module with custom levels
    assert hasattr(logging, "TRACE")
    assert hasattr(logging, "DETAIL")
    assert hasattr(logging, "BRIEF")
    assert hasattr(logging, "SILENT")
    # Verify logger name was registered
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == "test_extend"


def test_register_logger_with_custom_class() -> None:
    """register_logger() should call extendLoggingModule() on custom class."""

    # --- setup ---
    # Create a custom logger class
    class CustomLogger(mod_alogs.Logger):
        _logging_module_extended = False

        @classmethod
        def extendLoggingModule(
            cls,
        ) -> bool:
            """Custom extend that sets a flag."""
            if cls._logging_module_extended:
                return False
            cls._logging_module_extended = True
            # Call parent to actually extend
            return super().extendLoggingModule()

    # --- execute ---
    mod_alogs.registerLogger("test_custom", CustomLogger)

    # --- verify ---
    # Should have called extend on custom class
    assert CustomLogger._logging_module_extended is True  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
    # Verify logger name was registered
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_logger_name == "test_custom"


def test_register_logger_with_target_python_version() -> None:
    """register_logger() should set target_python_version via convenience parameter."""
    # --- setup ---
    version = (3, 11)

    # --- execute ---
    mod_alogs.registerLogger("test", target_python_version=version)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_target_python_version == version
    assert _registry.registered_internal_logger_name == "test"


def test_register_logger_with_log_level_env_vars() -> None:
    """register_logger() should set log_level_env_vars via convenience parameter."""
    # --- setup ---
    env_vars = ["TEST_LOG_LEVEL"]

    # --- execute ---
    mod_alogs.registerLogger("test", log_level_env_vars=env_vars)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_log_level_env_vars == env_vars
    assert _registry.registered_internal_logger_name == "test"


def test_register_logger_with_default_log_level() -> None:
    """register_logger() should set default_log_level via convenience parameter."""
    # --- setup ---
    default_level = "debug"

    # --- execute ---
    mod_alogs.registerLogger("test", default_log_level=default_level)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_default_log_level == default_level
    assert _registry.registered_internal_logger_name == "test"


def test_register_logger_with_propagate() -> None:
    """register_logger() should set propagate via convenience parameter."""
    # --- setup ---
    propagate = True

    # --- execute ---
    mod_alogs.registerLogger("test", propagate=propagate)

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_propagate == propagate
    assert _registry.registered_internal_logger_name == "test"


def test_register_logger_with_all_convenience_parameters() -> None:
    """register_logger() should set all convenience parameters at once."""
    # --- setup ---
    version = (3, 12)
    env_vars = ["TEST_LOG_LEVEL"]
    default_level = "warning"
    propagate = False

    # --- execute ---
    mod_alogs.registerLogger(
        "test",
        target_python_version=version,
        log_level_env_vars=env_vars,
        default_log_level=default_level,
        propagate=propagate,
    )

    # --- verify ---
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    assert _registry.registered_internal_target_python_version == version
    assert _registry.registered_internal_log_level_env_vars == env_vars
    assert _registry.registered_internal_default_log_level == default_level
    assert _registry.registered_internal_propagate == propagate
    assert _registry.registered_internal_logger_name == "test"


def test_register_logger_with_none_convenience_parameters() -> None:
    """register_logger() should handle None convenience parameters (no change)."""
    # --- setup ---
    mod_alogs.registerTargetPythonVersion((3, 11))
    mod_alogs.registerLogLevelEnvVars(["OLD_VAR"])
    mod_alogs.registerDefaultLogLevel("info")
    mod_alogs.registerPropagate(propagate=True)
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_version = _registry.registered_internal_target_python_version
    original_env_vars = _registry.registered_internal_log_level_env_vars
    original_default = _registry.registered_internal_default_log_level
    original_propagate = _registry.registered_internal_propagate

    # --- execute ---
    mod_alogs.registerLogger(
        "test",
        target_python_version=None,
        log_level_env_vars=None,
        default_log_level=None,
        propagate=None,
    )

    # --- verify ---
    # Should not have changed any values
    assert _registry.registered_internal_target_python_version == original_version
    assert _registry.registered_internal_log_level_env_vars == original_env_vars
    assert _registry.registered_internal_default_log_level == original_default
    assert _registry.registered_internal_propagate == original_propagate
    assert _registry.registered_internal_logger_name == "test"
