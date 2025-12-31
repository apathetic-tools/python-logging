# tests/conftest.py
"""Shared test setup for project.

Each pytest run now targets a single runtime mode:
- Package mode (default): uses src/<package> when RUNTIME_MODE=package
- Stitched mode: uses dist/<package>.py when RUNTIME_MODE=stitched
- Zipapp mode: uses dist/<package>.pyz when RUNTIME_MODE=zipapp

Switch mode with: RUNTIME_MODE=stitched pytest or RUNTIME_MODE=zipapp pytest
"""

import logging
import sys
from collections.abc import Generator

import apathetic_testing as alib_test
import pytest

import apathetic_logging as alib_logging


# early jank hook, must happen before importing the <package>
# so we get the stitched/zipapp version in the right mode
alib_test.runtime_swap()

from tests.utils import (  # noqa: E402
    direct_logger,
    module_logger,
)


# These utilities are intentionally re-exported so pytest can discover them.
__all__ = [
    "direct_logger",
    "module_logger",
]

safe_trace = alib_logging.makeSafeTrace("⚡️")


# Import after runtime_swap to ensure we get the right module
import apathetic_logging as mod_alogs  # noqa: E402
import apathetic_logging.registry_data as mod_registry  # noqa: E402


# ----------------------------------------------------------------------
# Helper functions for fixture
# ----------------------------------------------------------------------


def _save_ensure_root_logger_flag() -> bool | None:
    """Save the current state of the _root_logger_user_configured flag."""
    logger_module = sys.modules.get("apathetic_logging.logger")
    return (
        getattr(logger_module, "_root_logger_user_configured", None)
        if logger_module
        else None
    )


def _reset_ensure_root_logger_flag() -> None:
    """Reset the _root_logger_user_configured flag for test isolation."""
    logger_module = sys.modules.get("apathetic_logging.logger")
    if logger_module and hasattr(logger_module, "_root_logger_user_configured"):
        delattr(logger_module, "_root_logger_user_configured")


def _restore_ensure_root_logger_flag(*, original_value: bool | None) -> None:
    """Restore the _root_logger_user_configured flag to its original state."""
    logger_module = sys.modules.get("apathetic_logging.logger")
    if logger_module:
        if original_value is None:
            # If it wasn't set before, remove it now
            if hasattr(logger_module, "_root_logger_user_configured"):
                delattr(logger_module, "_root_logger_user_configured")
        else:
            # If it was set before, restore the original value
            logger_module._root_logger_user_configured = original_value  # type: ignore[attr-defined]  # noqa: SLF001


def _reset_registry_state(
    *,
    logger_name: str | None = None,
    default_log_level: str | None = None,
    log_level_env_vars: list[str] | None = None,
    compatibility_mode: bool | None = None,
    propagate: bool | None = None,
) -> None:
    """Reset registry state and re-register custom level names.

    Optionally accepts keyword arguments to set registry values. If not provided,
    defaults (None) are used. This handles both test setup (clearing to None) and
    test teardown (restoring original values).

    Args:
        logger_name: Logger name to register (or None to clear)
        default_log_level: Default log level to register (or None to clear)
        log_level_env_vars: Log level environment variables (or None to clear)
        compatibility_mode: Compatibility mode setting (or None to clear)
        propagate: Propagate setting (or None to clear)
    """
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    _constants = mod_alogs.apathetic_logging

    # Register custom level names
    mod_alogs.Logger.addLevelName(_constants.TEST_LEVEL, "TEST")
    mod_alogs.Logger.addLevelName(_constants.TRACE_LEVEL, "TRACE")
    mod_alogs.Logger.addLevelName(_constants.DETAIL_LEVEL, "DETAIL")
    mod_alogs.Logger.addLevelName(_constants.BRIEF_LEVEL, "BRIEF")
    mod_alogs.Logger.addLevelName(_constants.SILENT_LEVEL, "SILENT")

    # Set registry state
    _registry.registered_internal_logger_name = logger_name
    _registry.registered_internal_default_log_level = default_log_level
    _registry.registered_internal_log_level_env_vars = log_level_env_vars
    _registry.registered_internal_compatibility_mode = compatibility_mode
    _registry.registered_internal_propagate = propagate


@pytest.fixture(autouse=True)
def reset_logger_class_and_registry() -> Generator[None, None, None]:
    """Reset logger class and registry state before and after each test.

    This ensures that tests that set a custom logger class or modify registry
    state don't affect subsequent tests. This is the lowest common denominator
    needed by almost all tests.
    """
    # Save original state
    original_logger_class = logging.getLoggerClass()
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_name = _registry.registered_internal_logger_name
    original_default = _registry.registered_internal_default_log_level
    original_env_vars = _registry.registered_internal_log_level_env_vars
    original_compatibility_mode = _registry.registered_internal_compatibility_mode
    original_propagate = _registry.registered_internal_propagate
    # Save ensureRootLogger flag state
    original_user_configured = _save_ensure_root_logger_flag()

    # Clear any existing loggers from the registry
    _logging_utils = mod_alogs.apathetic_logging
    logger_names = list(logging.Logger.manager.loggerDict.keys())
    for logger_name in logger_names:
        _logging_utils.removeLogger(logger_name)

    # Reset to defaults before test
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    # Reset registry state and re-register custom level names
    _reset_registry_state()
    # Reset ensureRootLogger flag for test isolation
    _reset_ensure_root_logger_flag()

    yield

    # Clear root logger state to prevent test pollution
    root = logging.getLogger("")
    root.handlers.clear()
    root.setLevel(logging.WARNING)
    root.disabled = False
    root.propagate = True
    root.filters.clear()
    # Clear root logger's instance-level cache
    if hasattr(root, "__dict__") and "_last_stream_ids" in root.__dict__:
        del root.__dict__["_last_stream_ids"]

    # Clear loggers again after test
    logger_names = list(logging.Logger.manager.loggerDict.keys())
    for logger_name in logger_names:
        _logging_utils.removeLogger(logger_name)

    # Restore original state after test
    logging.setLoggerClass(original_logger_class)
    mod_alogs.Logger.extendLoggingModule()
    # Restore registry state and re-register custom level names
    _reset_registry_state(
        logger_name=original_name,
        default_log_level=original_default,
        log_level_env_vars=original_env_vars,
        compatibility_mode=original_compatibility_mode,
        propagate=original_propagate,
    )
    # Restore ensureRootLogger flag state
    _restore_ensure_root_logger_flag(original_value=original_user_configured)
