# tests/70_snake/test_logger_std_camel.py
"""Test module-level stdlib camelCase convenience functions."""

from __future__ import annotations

import logging
import sys
from contextlib import suppress
from unittest.mock import patch

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry_data
from tests.utils.level_validation import validate_test_level


# Safe test level value (26 is between MINIMAL=25 and WARNING=30)
TEST_LEVEL_VALUE = 26
validate_test_level(TEST_LEVEL_VALUE)

# List of all stdlib module-level camelCase functions and their test parameters
# Format: (function_name, args, kwargs, mock_target, min_python_version)
# min_python_version is (major, minor) tuple or None if available in MIN_PYTHON_VERSION+
MODULE_STD_CAMEL_TESTS: list[
    tuple[str, tuple[object, ...], dict[str, object], str, tuple[int, int] | None]
] = [
    ("basicConfig", (), {}, "logging.basicConfig", None),
    (
        "addLevelName",
        (TEST_LEVEL_VALUE, "CUSTOM_TEST_LEVEL"),
        {},
        "logging.addLevelName",
        None,
    ),
    ("getLevelName", (logging.DEBUG,), {}, "logging.getLevelName", None),
    ("getLevelNamesMapping", (), {}, "logging.getLevelNamesMapping", (3, 11)),
    ("getLoggerClass", (), {}, "logging.getLoggerClass", None),
    ("setLoggerClass", (object,), {}, "logging.setLoggerClass", None),
    ("getLogRecordFactory", (), {}, "logging.getLogRecordFactory", None),
    ("setLogRecordFactory", (object,), {}, "logging.setLogRecordFactory", None),
    ("shutdown", (), {}, "logging.shutdown", None),
    ("disable", (logging.DEBUG,), {}, "logging.disable", None),
    ("captureWarnings", (True,), {}, "logging.captureWarnings", None),
    ("critical", ("test",), {}, "logging.critical", None),
    ("debug", ("test",), {}, "logging.debug", None),
    ("error", ("test",), {}, "logging.error", None),
    ("exception", ("test",), {"exc_info": True}, "logging.exception", None),
    ("fatal", ("test",), {}, "logging.fatal", None),
    ("info", ("test",), {}, "logging.info", None),
    ("log", (logging.INFO, "test"), {}, "logging.log", None),
    ("warn", ("test",), {}, "logging.warning", None),
    ("warning", ("test",), {}, "logging.warning", None),
    ("getLogger", ("test",), {}, "logging.getLogger", None),
    ("makeLogRecord", ({"name": "test"},), {}, "logging.makeLogRecord", None),
    ("currentframe", (), {}, "logging.currentframe", None),
    ("getHandlerNames", (), {}, "logging.getHandlerNames", (3, 12)),
    ("getHandlerByName", ("test",), {}, "logging.getHandlerByName", (3, 12)),
]


@pytest.mark.parametrize(
    ("func_name", "args", "kwargs", "mock_target", "min_version"),
    MODULE_STD_CAMEL_TESTS,
)
def test_module_std_camel_function(
    func_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    mock_target: str,
    min_version: tuple[int, int] | None,
) -> None:
    """Test module-level stdlib camelCase functions call camelCase function.

    This is a "happy path" test that verifies each camelCase wrapper function
    exists and calls the underlying stdlib function correctly.
    """
    # Get the camelCase function
    camel_func = getattr(mod_alogs, func_name)
    assert camel_func is not None, (
        f"Function {func_name} not found on apathetic_logging"
    )

    # Check if the underlying function exists before trying to patch it
    # Some functions don't exist in Python 3.10
    # (e.g., getLevelNamesMapping, getHandlerNames, getHandlerByName)
    module_name, func_name_in_module = mock_target.rsplit(".", 1)
    if module_name == "logging" and not hasattr(logging, func_name_in_module):
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
        # Mock the underlying stdlib function
        with patch(mock_target) as mock_func:
            # Call the camelCase function
            # Some functions may raise (e.g., if logging is already configured)
            # That's okay - we just want to verify the mock was called
            with suppress(Exception):
                camel_func(*args, **kwargs)

            # Verify the underlying function was called
            mock_func.assert_called_once_with(*args, **kwargs)
    finally:
        if min_version is not None:
            _registry.registered_internal_target_python_version = original_target


def test_module_std_camel_function_exists() -> None:
    """Verify all expected camelCase functions exist on apathetic_logging."""
    for func_name, _, _, _, _ in MODULE_STD_CAMEL_TESTS:
        assert hasattr(mod_alogs, func_name), (
            f"Function {func_name} should exist on apathetic_logging"
        )
