# tests/conftest.py
"""Shared test setup for project.

Each pytest run now targets a single runtime mode:
- Package mode (default): uses src/<package> when RUNTIME_MODE=package
- Stitched mode: uses dist/<package>.py when RUNTIME_MODE=stitched
- Zipapp mode: uses dist/<package>.pyz when RUNTIME_MODE=zipapp

Switch mode with: RUNTIME_MODE=stitched pytest or RUNTIME_MODE=zipapp pytest
"""

import logging
import os
import sys
from collections.abc import Generator

import apathetic_utils as alib_utils
import pytest

import apathetic_logging as alib_logging
from tests.utils import (
    PROGRAM_PACKAGE,
    PROGRAM_SCRIPT,
    PROJ_ROOT,
    direct_logger,
    module_logger,
)


# early jank hook, must happen before importing the <package>
# so we get the stitched/zipapp version in the right mode
alib_utils.runtime_swap(
    root=PROJ_ROOT,
    package_name=PROGRAM_PACKAGE,
    script_name=PROGRAM_SCRIPT,
)


# These fixtures are intentionally re-exported so pytest can discover them.
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


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _mode() -> str:
    return os.getenv("RUNTIME_MODE", "package")


def _filter_debug_tests(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    # detect if the user is filtering for debug tests
    keywords = config.getoption("-k") or ""
    running_debug = "debug" in keywords.lower()

    if running_debug:
        return  # user explicitly requested them, don't skip

    for item in items:
        # Check for the actual @pytest.mark.debug marker, not just "debug" in keywords
        # (parametrized values can add "debug" to keywords, causing false positives)
        if item.get_closest_marker("debug") is not None:
            item.add_marker(
                pytest.mark.skip(reason="Skipped debug test (use -k debug to run)"),
            )


def _filter_runtime_mode_tests(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    mode = _mode()
    # Check if verbose mode is enabled (verbose > 0 means user wants verbose output)
    verbose = getattr(config.option, "verbose", 0)
    is_quiet = verbose <= 0

    # Only track included tests if not in quiet mode (for later reporting)
    included_map: dict[str, int] | None = {} if not is_quiet else None
    root = str(config.rootpath)
    testpaths: list[str] = config.getini("testpaths") or []

    # Identify mode-specific files by a custom variable defined at module scope
    for item in list(items):
        mod = item.getparent(pytest.Module)
        if mod is None or not hasattr(mod, "obj"):
            continue

        runtime_marker = getattr(mod.obj, "__runtime_mode__", None)

        if runtime_marker and runtime_marker != mode:
            items.remove(item)
            continue

        # Only track if not in quiet mode
        if runtime_marker and runtime_marker == mode and included_map is not None:
            file_path = str(item.fspath)
            # Make path relative to project root dir
            if file_path.startswith(root):
                file_path = os.path.relpath(file_path, root)
                for tp in testpaths:
                    if file_path.startswith(tp.rstrip("/") + os.sep):
                        file_path = file_path[len(tp.rstrip("/") + os.sep) :]
                        break

            included_map[file_path] = included_map.get(file_path, 0) + 1

    # Store results for later reporting (only if not in quiet mode)
    if included_map is not None:
        config._included_map = included_map  # type: ignore[attr-defined]  # noqa: SLF001
        config._runtime_mode = mode  # type: ignore[attr-defined]  # noqa: SLF001


# ----------------------------------------------------------------------
# Hooks
# ----------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest options based on verbosity."""
    verbose = getattr(config.option, "verbose", 0)
    if verbose <= 0:
        # In quiet mode, modify reportchars to exclude skipped tests ('s')
        # The -ra flag in pytest.ini shows all, but hide skipped in quiet mode
        reportchars = getattr(config.option, "reportchars", "")
        if reportchars == "a":
            # 'a' means "all except passed", change to exclude skipped and passed output
            # Use explicit chars: f (failed), E (error), x (xfailed), X (xpassed)
            config.option.reportchars = "fExX"
        elif "s" in reportchars or "P" in reportchars:
            # Remove 's' (skipped) and 'P' (passed with output) in quiet mode
            config.option.reportchars = reportchars.replace("s", "").replace("P", "")


def pytest_report_header(config: pytest.Config) -> str:  # noqa: ARG001 # pyright: ignore[reportUnknownParameterType]
    mode = _mode()
    return f"Runtime mode: {mode}"


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Filter and record runtime-specific tests for later reporting.

    also automatically skips debug tests unless asked for
    """
    _filter_debug_tests(config, items)
    _filter_runtime_mode_tests(config, items)


def pytest_unconfigure(config: pytest.Config) -> None:
    """Print summary of included runtime-specific tests at the end."""
    included_map: dict[str, int] = getattr(config, "_included_map", {})
    mode = getattr(config, "_runtime_mode", "package")

    if not included_map:
        return

    # Only print if pytest is not in quiet mode (verbose > 0 means verbose mode)
    verbose = getattr(config.option, "verbose", 0)
    if verbose <= 0:
        return

    total_tests = sum(included_map.values())
    print(
        f"🧪 Included {total_tests} {mode}-specific tests"
        f" across {len(included_map)} files:",
    )
    for path, count in sorted(included_map.items()):
        print(f"   • ({count}) {path}")
