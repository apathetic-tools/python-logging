# tests/70_snake/test_module_lib_snake.py
"""Test module-level library snake_case convenience functions."""

from __future__ import annotations

from contextlib import suppress
from unittest.mock import patch

import pytest

import apathetic_logging as mod_alogs


# List of all library module-level snake_case functions and their test parameters
# Format: (function_name, args, kwargs, mock_target_module, mock_target_function)
MODULE_LIB_SNAKE_TESTS: list[
    tuple[str, tuple[object, ...], dict[str, object], str, str]
] = [
    ("get_logger", (None,), {}, "apathetic_logging.get_logger", "getLogger"),
    (
        "get_logger_of_type",
        ("test", object),
        {},
        "apathetic_logging.get_logger",
        "getLoggerOfType",
    ),
    ("has_logger", ("test",), {}, "apathetic_logging.logging_utils", "hasLogger"),
    (
        "remove_logger",
        ("test",),
        {},
        "apathetic_logging.logging_utils",
        "removeLogger",
    ),
    (
        "register_default_log_level",
        ("INFO",),
        {},
        "apathetic_logging.registry",
        "registerDefaultLogLevel",
    ),
    (
        "register_log_level_env_vars",
        (["LOG_LEVEL"],),
        {},
        "apathetic_logging.registry",
        "registerLogLevelEnvVars",
    ),
    (
        "register_logger",
        ("test",),
        {},
        "apathetic_logging.registry",
        "registerLogger",
    ),
    (
        "resolve_logger_name",
        ("test",),
        {},
        "apathetic_logging.logging_utils",
        "resolveLoggerName",
    ),
    ("safe_log", ("test",), {}, "apathetic_logging.safe_logging", "safeLog"),
    (
        "safe_trace",
        ("test",),
        {},
        "apathetic_logging.safe_logging",
        "safeTrace",
    ),
    (
        "make_safe_trace",
        ("test",),
        {},
        "apathetic_logging.safe_logging",
        "makeSafeTrace",
    ),
]


@pytest.mark.parametrize(
    ("func_name", "args", "kwargs", "mock_target_module", "mock_target_function"),
    MODULE_LIB_SNAKE_TESTS,
)
def test_module_lib_snake_function(
    func_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    mock_target_module: str,
    mock_target_function: str,
) -> None:
    """Test module-level library snake_case functions call camelCase function.

    This is a "happy path" test that verifies each snake_case wrapper function
    exists and calls the underlying library function correctly.
    """
    # Get the snake_case function
    snake_func = getattr(mod_alogs, func_name)
    assert snake_func is not None, (
        f"Function {func_name} not found on apathetic_logging"
    )

    # Mock the underlying library function
    # For library functions, patch the internal class method that the snake_case
    # function calls
    if mock_target_module.startswith("apathetic_logging."):
        # The snake_case functions call internal class methods directly
        # Patch the internal class method
        # (e.g., apathetic_logging.get_logger.
        # ApatheticLogging_Internal_GetLogger.getLogger)

        if mock_target_module == "apathetic_logging.get_logger":
            patch_target = (
                f"apathetic_logging.get_logger."
                f"ApatheticLogging_Internal_GetLogger.{mock_target_function}"
            )
        elif mock_target_module == "apathetic_logging.logging_utils":
            patch_target = (
                f"apathetic_logging.logging_utils."
                f"ApatheticLogging_Internal_LoggingUtils.{mock_target_function}"
            )
        elif mock_target_module == "apathetic_logging.registry":
            patch_target = (
                f"apathetic_logging.registry."
                f"ApatheticLogging_Internal_Registry.{mock_target_function}"
            )
        elif mock_target_module == "apathetic_logging.safe_logging":
            patch_target = (
                f"apathetic_logging.safe_logging."
                f"ApatheticLogging_Internal_SafeLogging.{mock_target_function}"
            )
        else:
            # Fallback: try namespace class
            patch_target = f"apathetic_logging.apathetic_logging.{mock_target_function}"
    else:
        # For stdlib functions, use the original target
        patch_target = f"{mock_target_module}.{mock_target_function}"
    with patch(patch_target) as mock_func:
        # Call the snake_case function
        # Some functions may raise (e.g., if logger doesn't exist)
        # That's okay - we just want to verify the mock was called
        with suppress(Exception):
            snake_func(*args, **kwargs)

        # Verify the underlying function was called
        # For "happy path" tests, we just verify the function was called
        # (exact argument matching may vary due to defaults)
        assert mock_func.called, f"{mock_target_function} was not called by {func_name}"


def test_module_lib_snake_function_exists() -> None:
    """Verify all expected snake_case functions exist on apathetic_logging."""
    for func_name, _, _, _, _ in MODULE_LIB_SNAKE_TESTS:
        assert hasattr(mod_alogs, func_name), (
            f"Function {func_name} should exist on apathetic_logging"
        )
