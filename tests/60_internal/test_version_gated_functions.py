# tests/30_independant/test_version_gated_functions.py
"""Tests for version-gated functions with target Python version."""

import logging
import sys
from typing import Any

import apathetic_utils
import pytest
from apathetic_testing import create_mock_version_info

import apathetic_logging as mod_alogs
import apathetic_logging.logging_utils as mod_logging_utils
import apathetic_logging.registry_data as mod_registry_data
from tests.utils import PATCH_STITCH_HINTS, PROGRAM_PACKAGE


# Test data: (function_name, args, kwargs, min_version, mock_return_value, error_match)
VERSION_GATED_FUNCTIONS: list[
    tuple[str, tuple[Any, ...], dict[str, Any], tuple[int, int], Any, str]
] = [
    # Python 3.11+ functions
    (
        "getLevelNamesMapping",
        (),
        {},
        (3, 11),
        {10: "DEBUG", 20: "INFO"},
        "requires Python 3.11",
    ),
    # Python 3.12+ functions
    (
        "getHandlerByName",
        ("test",),
        {},
        (3, 12),
        None,
        "requires Python 3.12",
    ),
    (
        "getHandlerNames",
        (),
        {},
        (3, 12),
        ["handler1", "handler2"],
        "requires Python 3.12",
    ),
]


@pytest.mark.parametrize(
    ("func_name", "args", "kwargs", "min_version", "mock_return_value", "error_match"),
    VERSION_GATED_FUNCTIONS,
)
def test_version_gated_function_raises_when_target_too_low(
    func_name: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    min_version: tuple[int, int],
    mock_return_value: Any,  # noqa: ARG001
    error_match: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Version-gated functions should raise if target version < required version."""
    # --- setup ---
    _registry = mod_registry_data.ApatheticLogging_Internal_RegistryData
    original_target = _registry.registered_internal_target_python_version
    # Set target version to one less than required
    too_low_version = (min_version[0], min_version[1] - 1)
    _registry.registered_internal_target_python_version = too_low_version

    # Mock runtime version to be sufficient so we test target version check, not runtime
    monkeypatch.setattr(
        mod_logging_utils.sys,  # type: ignore[attr-defined]
        "version_info",
        create_mock_version_info(min_version[0], min_version[1], 0),
    )

    try:
        func = getattr(mod_alogs, func_name)
        # --- execute and verify ---
        with pytest.raises(NotImplementedError, match=error_match):
            func(*args, **kwargs)
    finally:
        _registry.registered_internal_target_python_version = original_target
        monkeypatch.undo()


@pytest.mark.parametrize(
    ("func_name", "args", "kwargs", "min_version", "mock_return_value", "error_match"),
    VERSION_GATED_FUNCTIONS,
)
def test_version_gated_function_works_when_target_sufficient(
    func_name: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    min_version: tuple[int, int],
    mock_return_value: Any,
    error_match: str,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Version-gated functions should work if target version >= required version."""
    # --- setup ---
    _registry = mod_registry_data.ApatheticLogging_Internal_RegistryData
    original_target = _registry.registered_internal_target_python_version
    _registry.registered_internal_target_python_version = min_version

    # Mock runtime version if needed
    if sys.version_info < min_version:
        monkeypatch.setattr(
            mod_logging_utils.sys,  # type: ignore[attr-defined]
            "version_info",
            create_mock_version_info(min_version[0], min_version[1], 0),
        )

    try:
        # Determine the underlying stdlib function name
        # camelCase functions map directly to stdlib functions
        stdlib_func_name = func_name

        # Mock the underlying function
        def mock_func(*_args: Any, **_kwargs: Any) -> Any:
            return mock_return_value

        # Use create_if_missing=True to allow patching functions that don't exist
        # (e.g., Python 3.11+ functions on Python 3.10)
        # monkeypatch will automatically clean up created attributes on undo
        apathetic_utils.patch_everywhere(
            monkeypatch,
            logging,
            stdlib_func_name,
            mock_func,
            package_prefix=PROGRAM_PACKAGE,
            stitch_hints=PATCH_STITCH_HINTS,
            create_if_missing=True,
        )
        func = getattr(mod_alogs, func_name)
        # --- execute ---
        result = func(*args, **kwargs)

        # --- verify ---
        assert result == mock_return_value
    finally:
        _registry.registered_internal_target_python_version = original_target
        monkeypatch.undo()
