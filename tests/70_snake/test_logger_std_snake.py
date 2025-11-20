# tests/70_snake/test_logger_std_snake.py
"""Test Logger instance stdlib snake_case convenience methods."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

import apathetic_logging.logger_std_snake as mod_logger_std_snake
from tests.utils.mock_superclass import create_mock_superclass_test


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    import apathetic_logging as mod_alogs

    Logger = mod_alogs.Logger


# List of all stdlib Logger instance snake_case methods and their test parameters
# Format: (method_name, args, kwargs, camel_case_method_name)
LOGGER_STD_SNAKE_TESTS: list[tuple[str, tuple[object, ...], dict[str, object], str]] = [
    ("add_filter", (logging.Filter(),), {}, "addFilter"),
    ("remove_filter", (logging.Filter(),), {}, "removeFilter"),
    ("add_handler", (logging.StreamHandler(),), {}, "addHandler"),
    ("remove_handler", (logging.StreamHandler(),), {}, "removeHandler"),
    (
        "call_handlers",
        (logging.LogRecord("name", 0, "", 0, "", (), None),),
        {},
        "callHandlers",
    ),
    ("has_handlers", (), {}, "hasHandlers"),
    ("set_level", (logging.DEBUG,), {}, "setLevel"),
    ("get_effective_level", (), {}, "getEffectiveLevel"),
    ("is_enabled_for", (logging.DEBUG,), {}, "isEnabledFor"),
    ("get_child", ("child",), {}, "getChild"),
    ("get_children", (), {}, "getChildren"),
    (
        "make_record",
        ("name", logging.INFO, "path", 1, "msg", (), None),
        {},
        "makeRecord",
    ),
    ("find_caller", (), {"stack_info": False, "stacklevel": 1}, "findCaller"),
]


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "camel_case_method_name"),
    LOGGER_STD_SNAKE_TESTS,
)
def test_logger_std_snake_method(
    method_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    camel_case_method_name: str,
) -> None:
    """Test Logger instance stdlib snake_case methods call camelCase method.

    This is a "happy path" test that verifies each snake_case wrapper method
    exists and calls the underlying stdlib Logger method correctly.
    """
    # Use helper to create test class with controlled MRO for super() resolution
    create_mock_superclass_test(
        mixin_class=mod_logger_std_snake.ApatheticLogging_Internal_StdLoggerSnakeCase,
        parent_class=logging.Logger,
        method_name=method_name,
        camel_case_method_name=camel_case_method_name,
        args=args,
        kwargs=kwargs,
    )


def test_logger_std_snake_method_exists(
    direct_logger: Logger,
) -> None:
    """Verify all expected snake_case methods exist on Logger instances."""
    for method_name, _, _, _ in LOGGER_STD_SNAKE_TESTS:
        assert hasattr(direct_logger, method_name), (
            f"Method {method_name} should exist on Logger instances"
        )
