# tests/70_snake/test_module_std_snake.py
"""Test module-level stdlib snake_case convenience functions."""

from __future__ import annotations

import logging
import sys
from contextlib import suppress
from unittest.mock import patch

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.constants as mod_constants
import apathetic_logging.logging_utils as mod_logging_utils
import apathetic_logging.registry_data as mod_registry_data
from tests.utils.level_validation import validate_test_level


MIN_PYTHON_VERSION = (
    mod_constants.ApatheticLogging_Internal_Constants.MIN_PYTHON_VERSION
)

# Safe test level value (26 is between MINIMAL=25 and WARNING=30)
TEST_LEVEL_VALUE = 26
validate_test_level(TEST_LEVEL_VALUE)

# List of all stdlib module-level snake_case functions and their test parameters
# Format: (function_name, args, kwargs, mock_target, min_python_version)
# min_python_version is (major, minor) tuple or None if available in MIN_PYTHON_VERSION+
MODULE_STD_SNAKE_TESTS: list[
    tuple[str, tuple[object, ...], dict[str, object], str, tuple[int, int] | None]
] = [
    ("basic_config", (), {}, "logging.basicConfig", None),
    (
        "add_level_name",
        (TEST_LEVEL_VALUE, "CUSTOM_TEST_LEVEL"),
        {},
        "logging.addLevelName",
        None,
    ),
    ("get_level_name", (logging.DEBUG,), {}, "logging.getLevelName", None),
    ("get_level_names_mapping", (), {}, "logging.getLevelNamesMapping", (3, 11)),
    ("get_logger_class", (), {}, "logging.getLoggerClass", None),
    ("set_logger_class", (object,), {}, "logging.setLoggerClass", None),
    ("get_log_record_factory", (), {}, "logging.getLogRecordFactory", None),
    ("set_log_record_factory", (object,), {}, "logging.setLogRecordFactory", None),
    ("shutdown", (), {}, "logging.shutdown", None),
    ("disable", (logging.DEBUG,), {}, "logging.disable", None),
    ("capture_warnings", (True,), {}, "logging.captureWarnings", None),
    ("critical", ("test",), {}, "logging.critical", None),
    ("debug", ("test",), {}, "logging.debug", None),
    ("error", ("test",), {}, "logging.error", None),
    ("exception", ("test",), {"exc_info": True}, "logging.exception", None),
    ("fatal", ("test",), {}, "logging.fatal", None),
    ("info", ("test",), {}, "logging.info", None),
    ("log", (logging.INFO, "test"), {}, "logging.log", None),
    ("warn", ("test",), {}, "logging.warning", None),
    ("warning", ("test",), {}, "logging.warning", None),
    ("get_logger", ("test",), {}, "logging.getLogger", None),
    ("make_log_record", ({"name": "test"},), {}, "logging.makeLogRecord", None),
    ("currentframe", (), {}, "logging.currentframe", None),
    ("get_handler_names", (), {}, "logging.getHandlerNames", (3, 12)),
    ("get_handler_by_name", ("test",), {}, "logging.getHandlerByName", (3, 12)),
]


@pytest.mark.parametrize(
    ("func_name", "args", "kwargs", "mock_target", "min_version"),
    MODULE_STD_SNAKE_TESTS,
)
def test_module_std_snake_function(  # noqa: PLR0915
    func_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    mock_target: str,
    min_version: tuple[int, int] | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test module-level stdlib snake_case functions call camelCase function.

    This is a "happy path" test that verifies each snake_case wrapper function
    exists and calls the underlying stdlib function correctly.

    For functions with min_version > MIN_PYTHON_VERSION, also tests that they raise
    NotImplementedError on older versions by mocking sys.version_info.
    """
    # Get the snake_case function
    snake_func = getattr(mod_alogs, func_name)
    assert snake_func is not None, (
        f"Function {func_name} not found on apathetic_logging"
    )

    # For functions with version requirements, test exception case
    if min_version is not None:
        # Mock an older target version to test that NotImplementedError is raised
        # Also mock sys.version_info in logging_utils for runtime check
        older_version = (min_version[0], min_version[1] - 1)
        _registry = mod_registry_data.ApatheticLogging_Internal_RegistryData
        original_target = _registry.registered_internal_target_python_version
        _registry.registered_internal_target_python_version = older_version
        # Also mock runtime version in logging_utils
        monkeypatch.setattr(mod_logging_utils.sys, "version_info", older_version)  # type: ignore[attr-defined]
        try:
            with pytest.raises(NotImplementedError):
                snake_func(*args, **kwargs)
        finally:
            _registry.registered_internal_target_python_version = original_target
            monkeypatch.undo()

    # Test the success case (either naturally or by mocking to sufficient version)
    if min_version is not None and sys.version_info < min_version:
        # If we're actually on an older version, mock to a sufficient version
        # But first check if the underlying function exists in the logging module
        # If it doesn't exist, we can't patch it, so skip the test
        module_name, func_name_in_module = mock_target.rsplit(".", 1)
        if module_name == "logging" and not hasattr(logging, func_name_in_module):
            # Check if the function exists in the logging module
            pytest.skip(
                f"{func_name} requires Python {min_version[0]}.{min_version[1]}+ "
                f"but {func_name_in_module} doesn't exist in logging module"
            )
        # Set target version and mock runtime version
        _registry = mod_registry_data.ApatheticLogging_Internal_RegistryData
        original_target = _registry.registered_internal_target_python_version
        _registry.registered_internal_target_python_version = min_version
        monkeypatch.setattr(mod_logging_utils.sys, "version_info", min_version)  # type: ignore[attr-defined]
        try:
            with patch(mock_target) as mock_func:
                with suppress(Exception):
                    snake_func(*args, **kwargs)
                mock_func.assert_called_once_with(*args, **kwargs)
        finally:
            _registry.registered_internal_target_python_version = original_target
            monkeypatch.undo()
    else:
        # We're on a sufficient version, test normally
        # But first check if the underlying function exists
        module_name, func_name_in_module = mock_target.rsplit(".", 1)
        if module_name == "logging" and not hasattr(logging, func_name_in_module):
            # Check if the function exists in the logging module
            py_version = f"{sys.version_info[0]}.{sys.version_info[1]}"
            pytest.skip(
                f"{func_name} requires {func_name_in_module} which doesn't exist "
                f"in logging module on Python {py_version}"
            )
        # Ensure target version is set appropriately if this function has a min version
        _registry = mod_registry_data.ApatheticLogging_Internal_RegistryData
        original_target = _registry.registered_internal_target_python_version
        if min_version is not None and (
            original_target is None or original_target < min_version
        ):
            # Set target version to at least min_version to allow the function to work
            _registry.registered_internal_target_python_version = min_version
        try:
            with patch(mock_target) as mock_func:
                # Call the snake_case function
                # Some functions may raise (e.g., if logging is already configured)
                # That's okay - we just want to verify the mock was called
                with suppress(Exception):
                    snake_func(*args, **kwargs)

                # Verify the underlying function was called
                mock_func.assert_called_once_with(*args, **kwargs)
        finally:
            if min_version is not None:
                _registry.registered_internal_target_python_version = original_target


def test_module_std_snake_function_exists() -> None:
    """Verify all expected snake_case functions exist on apathetic_logging."""
    for func_name, _, _, _, _ in MODULE_STD_SNAKE_TESTS:
        assert hasattr(mod_alogs, func_name), (
            f"Function {func_name} should exist on apathetic_logging"
        )
