# tests/70_snake/test_logger_std_camel.py
"""Test module-level stdlib camelCase convenience functions."""

from __future__ import annotations

import logging
import sys
from contextlib import suppress
from unittest.mock import MagicMock

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.logging_utils as mod_logging_utils
import apathetic_logging.registry_data as mod_registry_data
from tests.utils.level_validation import validate_test_level
from tests.utils.patch_everywhere import patch_everywhere
from tests.utils.version_info_mock import create_version_info


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
def test_module_std_camel_function(  # noqa: PLR0915
    func_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    mock_target: str,
    min_version: tuple[int, int] | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test module-level stdlib camelCase functions call camelCase function.

    This is a "happy path" test that verifies each camelCase wrapper function
    exists and calls the underlying stdlib function correctly.

    For functions with min_version > MIN_PYTHON_VERSION, also tests that they raise
    NotImplementedError on older versions by mocking sys.version_info.
    """
    # Get the camelCase function
    camel_func = getattr(mod_alogs, func_name)
    assert camel_func is not None, (
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
        monkeypatch.setattr(
            mod_logging_utils.sys,  # type: ignore[attr-defined]
            "version_info",
            create_version_info(older_version[0], older_version[1], 0),
        )
        try:
            with pytest.raises(NotImplementedError):
                camel_func(*args, **kwargs)
        finally:
            _registry.registered_internal_target_python_version = original_target
            monkeypatch.undo()

    # Test the success case (either naturally or by mocking to sufficient version)
    if min_version is not None and sys.version_info < min_version:
        # If we're actually on an older version, mock to a sufficient version
        # Set target version and mock runtime version
        _registry = mod_registry_data.ApatheticLogging_Internal_RegistryData
        original_target = _registry.registered_internal_target_python_version
        _registry.registered_internal_target_python_version = min_version
        monkeypatch.setattr(
            mod_logging_utils.sys,  # type: ignore[attr-defined]
            "version_info",
            create_version_info(min_version[0], min_version[1], 0),
        )
        try:
            # Use patch_everywhere with create_if_missing=True for missing functions
            module_name, func_name_in_module = mock_target.rsplit(".", 1)
            mock_func = MagicMock()
            if module_name == "logging":
                patch_everywhere(
                    monkeypatch,
                    logging,
                    func_name_in_module,
                    mock_func,
                    create_if_missing=True,
                )
            else:
                # For non-logging modules, use standard patching
                pytest.skip(f"Unsupported module: {module_name}")
            with suppress(Exception):
                camel_func(*args, **kwargs)
            mock_func.assert_called_once_with(*args, **kwargs)
        finally:
            _registry.registered_internal_target_python_version = original_target
            monkeypatch.undo()
    else:
        # We're on a sufficient version, test normally
        # Ensure target version is set appropriately if this function has a min version
        _registry = mod_registry_data.ApatheticLogging_Internal_RegistryData
        original_target = _registry.registered_internal_target_python_version
        if min_version is not None and (
            original_target is None or original_target < min_version
        ):
            # Set target version to at least min_version to allow the function to work
            _registry.registered_internal_target_python_version = min_version
        try:
            # Use patch_everywhere with create_if_missing=True for missing functions
            module_name, func_name_in_module = mock_target.rsplit(".", 1)
            mock_func = MagicMock()
            if module_name == "logging":
                patch_everywhere(
                    monkeypatch,
                    logging,
                    func_name_in_module,
                    mock_func,
                    create_if_missing=True,
                )
            else:
                # For non-logging modules, use standard patching
                pytest.skip(f"Unsupported module: {module_name}")
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
            monkeypatch.undo()


def test_module_std_camel_function_exists() -> None:
    """Verify all expected camelCase functions exist on apathetic_logging."""
    for func_name, _, _, _, _ in MODULE_STD_CAMEL_TESTS:
        assert hasattr(mod_alogs, func_name), (
            f"Function {func_name} should exist on apathetic_logging"
        )
