# tests/70_snake/test_module_std_snake.py
"""Test module-level stdlib snake_case convenience functions."""

from __future__ import annotations

import logging
from contextlib import suppress
from unittest.mock import patch

import pytest

import apathetic_logging as mod_alogs
from tests.utils.level_validation import validate_test_level


# Safe test level value (26 is between MINIMAL=25 and WARNING=30)
TEST_LEVEL_VALUE = 26
validate_test_level(TEST_LEVEL_VALUE)

# List of all stdlib module-level snake_case functions and their test parameters
# Format: (function_name, args, kwargs, mock_target)
MODULE_STD_SNAKE_TESTS: list[tuple[str, tuple[object, ...], dict[str, object], str]] = [
    ("basic_config", (), {}, "logging.basicConfig"),
    (
        "add_level_name",
        (TEST_LEVEL_VALUE, "CUSTOM_TEST_LEVEL"),
        {},
        "logging.addLevelName",
    ),
    ("get_level_name", (logging.DEBUG,), {}, "logging.getLevelName"),
    ("get_level_names_mapping", (), {}, "logging.getLevelNamesMapping"),
    ("get_logger_class", (), {}, "logging.getLoggerClass"),
    ("set_logger_class", (object,), {}, "logging.setLoggerClass"),
    ("get_log_record_factory", (), {}, "logging.getLogRecordFactory"),
    ("set_log_record_factory", (object,), {}, "logging.setLogRecordFactory"),
    ("shutdown", (), {}, "logging.shutdown"),
    ("disable", (logging.DEBUG,), {}, "logging.disable"),
    ("capture_warnings", (True,), {}, "logging.captureWarnings"),
    ("critical", ("test",), {}, "logging.critical"),
    ("debug", ("test",), {}, "logging.debug"),
    ("error", ("test",), {}, "logging.error"),
    ("exception", ("test",), {"exc_info": True}, "logging.exception"),
    ("fatal", ("test",), {}, "logging.fatal"),
    ("info", ("test",), {}, "logging.info"),
    ("log", (logging.INFO, "test"), {}, "logging.log"),
    ("warn", ("test",), {}, "logging.warning"),
    ("warning", ("test",), {}, "logging.warning"),
    ("get_logger", ("test",), {}, "logging.getLogger"),
    ("make_log_record", ({"name": "test"},), {}, "logging.makeLogRecord"),
    ("currentframe", (), {}, "logging.currentframe"),
    ("get_handler_names", (), {}, "logging.getHandlerNames"),
    ("get_handler_by_name", ("test",), {}, "logging.getHandlerByName"),
]


@pytest.mark.parametrize(
    ("func_name", "args", "kwargs", "mock_target"),
    MODULE_STD_SNAKE_TESTS,
)
def test_module_std_snake_function(
    func_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    mock_target: str,
) -> None:
    """Test module-level stdlib snake_case functions call camelCase function.

    This is a "happy path" test that verifies each snake_case wrapper function
    exists and calls the underlying stdlib function correctly.
    """
    # Get the snake_case function
    snake_func = getattr(mod_alogs, func_name)
    assert snake_func is not None, (
        f"Function {func_name} not found on apathetic_logging"
    )

    # Mock the underlying stdlib function
    with patch(mock_target) as mock_func:
        # Call the snake_case function
        # Some functions may raise (e.g., if logging is already configured)
        # That's okay - we just want to verify the mock was called
        with suppress(Exception):
            snake_func(*args, **kwargs)

        # Verify the underlying function was called
        mock_func.assert_called_once_with(*args, **kwargs)


def test_module_std_snake_function_exists() -> None:
    """Verify all expected snake_case functions exist on apathetic_logging."""
    for func_name, _, _, _ in MODULE_STD_SNAKE_TESTS:
        assert hasattr(mod_alogs, func_name), (
            f"Function {func_name} should exist on apathetic_logging"
        )
