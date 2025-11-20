# tests/70_snake/test_logger_lib_snake.py
"""Test Logger instance library snake_case convenience methods."""

from __future__ import annotations

import logging
from contextlib import suppress
from types import MethodType
from typing import TYPE_CHECKING
from unittest import mock

import pytest

import apathetic_logging as mod_alogs
from tests.utils.level_validation import validate_test_level


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger

# Safe test level value (26 is between MINIMAL=25 and WARNING=30)
TEST_LEVEL_VALUE = 26
validate_test_level(TEST_LEVEL_VALUE)

# List of all library Logger instance snake_case methods and their test parameters
# Format: (method_name, args, kwargs, camel_case_method_name)
LOGGER_LIB_SNAKE_TESTS: list[tuple[str, tuple[object, ...], dict[str, object], str]] = [
    ("ensure_handlers", (), {}, "ensureHandlers"),
    ("add_level_name", (TEST_LEVEL_VALUE, "CUSTOM_TEST_LEVEL"), {}, "addLevelName"),
    (
        "determine_log_level",
        (),
        {"args": None, "root_log_level": None},
        "determineLogLevel",
    ),
    ("resolve_level_name", ("DEBUG",), {}, "resolveLevelName"),
    ("error_if_not_debug", ("test",), {}, "errorIfNotDebug"),
    ("critical_if_not_debug", ("test",), {}, "criticalIfNotDebug"),
    ("log_dynamic", (logging.INFO, "test"), {}, "logDynamic"),
    ("use_level", (logging.DEBUG,), {"minimum": False}, "useLevel"),
]


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "camel_case_method_name"),
    LOGGER_LIB_SNAKE_TESTS,
)
def test_logger_lib_snake_method(  # noqa: PLR0912
    direct_logger: Logger,
    method_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    camel_case_method_name: str,
) -> None:
    """Test Logger instance library snake_case methods call camelCase method.

    This is a "happy path" test that verifies each snake_case wrapper method
    exists and calls the underlying library Logger method correctly.
    """
    # Get the snake_case method
    snake_method = getattr(direct_logger, method_name)
    assert snake_method is not None, f"Method {method_name} not found on Logger"

    # Check if it's a static method (not bound to instance)
    is_static = not isinstance(snake_method, MethodType)

    if is_static:
        # For static methods, patch on the class
        # Note: add_level_name calls ApatheticLogging_Internal_LoggerCore.addLevelName
        # directly, so we need to patch that
        if camel_case_method_name == "addLevelName":
            # Clean up the level name attribute if it exists to avoid conflicts
            if len(args) > 1 and isinstance(args[1], str):
                level_name = args[1]
                level_value = args[0] if args else None
                # Clean up attribute if it exists
                if hasattr(logging, level_name):
                    delattr(logging, level_name)
                # Clean up level name mapping if it exists
                if (
                    level_value is not None
                    and isinstance(level_value, int)
                    and hasattr(logging, "_levelToName")
                ):
                    # Save original level name if it exists
                    original_level_name = logging.getLevelName(level_value)
                    # Remove the level name mapping if it matches our test level name
                    if original_level_name == level_name:
                        # Restore to default "Level X" format
                        logging._levelToName.pop(level_value, None)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

            # Get the LoggerCore class from the logger instance's MRO
            # In singlefile mode, the module class and instance class are
            # different objects
            logger_class = type(direct_logger)
            logger_core_class = None
            for cls in logger_class.__mro__:
                if cls.__name__ == "ApatheticLogging_Internal_LoggerCore":
                    logger_core_class = cls
                    break
            assert logger_core_class is not None, (
                "Could not find ApatheticLogging_Internal_LoggerCore in MRO"
            )

            camel_method = getattr(logger_core_class, camel_case_method_name)
            with mock.patch.object(
                logger_core_class,
                camel_case_method_name,
                wraps=camel_method,
            ) as mock_method:
                # Call the snake_case method (can call on instance or class)
                with suppress(Exception):
                    snake_method(*args, **kwargs)

                # Verify the underlying method was called
                mock_method.assert_called_once_with(*args, **kwargs)
        else:
            camel_method = getattr(mod_alogs.Logger, camel_case_method_name)
            with mock.patch.object(
                mod_alogs.Logger, camel_case_method_name, wraps=camel_method
            ) as mock_method:
                # Call the snake_case method (can call on instance or class)
                with suppress(Exception):
                    snake_method(*args, **kwargs)

                # Verify the underlying method was called
                mock_method.assert_called_once_with(*args, **kwargs)
    else:
        # For instance methods, patch on the instance
        camel_method = getattr(direct_logger, camel_case_method_name)
        with mock.patch.object(
            direct_logger, camel_case_method_name, wraps=camel_method
        ) as mock_method:
            # Call the snake_case method
            # Special handling for context managers (use_level)
            if method_name == "use_level":
                # Context managers need to be used with 'with' statement
                with suppress(Exception), snake_method(*args, **kwargs):
                    pass  # Enter and exit the context
            else:
                with suppress(Exception):
                    snake_method(*args, **kwargs)

            # Verify the underlying method was called
            # Some wrappers modify kwargs (e.g., error_if_not_debug adds stacklevel)
            expected_kwargs = kwargs.copy()
            if method_name in ("error_if_not_debug", "critical_if_not_debug"):
                # These wrappers add stacklevel=3 to account for the wrapper frame
                expected_kwargs["stacklevel"] = 3
            mock_method.assert_called_once_with(*args, **expected_kwargs)


def test_logger_lib_snake_method_exists(
    direct_logger: Logger,
) -> None:
    """Verify all expected snake_case methods exist on Logger instances."""
    for method_name, _, _, _ in LOGGER_LIB_SNAKE_TESTS:
        assert hasattr(direct_logger, method_name), (
            f"Method {method_name} should exist on Logger instances"
        )
