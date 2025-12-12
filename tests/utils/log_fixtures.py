# tests/utils/log_fixtures.py
"""Reusable fixtures for testing the Apathetic logger system."""

import logging
import uuid
from collections.abc import Generator
from typing import TYPE_CHECKING

import apathetic_utils
import pytest

import apathetic_logging as mod_alogs

from .constants import PATCH_STITCH_HINTS, PROGRAM_PACKAGE
from .safe_trace import make_safe_trace


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


safe_trace = make_safe_trace(icon="📏")


def _suffix() -> str:
    return "_" + uuid.uuid4().hex[:6]


@pytest.fixture
def direct_logger() -> Logger:
    """Create a brand-new ApatheticLogger with no shared state.

    Only for testing the logger itself.

    This fixture does NOT affect get_logger() or global state —
    it's just a clean logger instance for isolated testing.

    Default log level is set to "test" for maximum verbosity in test output.
    """
    # Give each test's logger a unique name for debug clarity
    name = f"test_logger{_suffix()}"
    logger = mod_alogs.Logger(name)
    logger.setLevel("test")
    # Set propagate=False so logger gets its own handler for isolated testing
    logger.setPropagate(False)
    # Set parent to root logger so it can inherit from the root logger hierarchy.
    # This is needed for tests that check parent-child relationships and
    # level inheritance.
    logger.parent = logging.getLogger("")
    return logger


@pytest.fixture
def module_logger(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Logger, None, None]:
    """Replace getLogger() everywhere with a new isolated instance.

    Ensures all modules (build, config, etc.) calling getLogger()
    will use this test logger for the duration of the test.

    Automatically reverts after test completion, including restoring the
    logging registry to its original state.

    Default log level is set to "test" for maximum verbosity in test output.
    """
    # Use the same logger name as the original logger so that DualStreamHandler
    # can find it when it looks up the logger by name in emit()
    original_logger_name = PROGRAM_PACKAGE
    new_logger = mod_alogs.Logger(original_logger_name)
    new_logger.setLevel("test")
    new_logger.setPropagate(propagate=False)

    # Replace the logger in the logging registry
    registry = logging.Logger.manager.loggerDict
    original_registry_logger = registry.get(original_logger_name)
    registry[original_logger_name] = new_logger

    # Patch logging.getLogger to prevent it from creating new logger instances
    original_get_logger = logging.getLogger

    def patched_get_logger(name: str | None = None) -> logging.Logger:
        if name == original_logger_name:
            return new_logger
        return original_get_logger(name)

    monkeypatch.setattr(logging, "getLogger", patched_get_logger)

    # Patch getLogger everywhere it's imported
    def mock_get_logger(*_args: object, **_kwargs: object) -> Logger:
        return new_logger

    apathetic_utils.patch_everywhere(
        monkeypatch,
        mod_alogs,
        "getLogger",
        mock_get_logger,
        package_prefix=PROGRAM_PACKAGE,
        stitch_hints=PATCH_STITCH_HINTS,
    )

    safe_trace(
        "module_logger fixture",
        f"id={id(new_logger)}",
        f"level={new_logger.levelName}",
        f"handlers={[type(h).__name__ for h in new_logger.handlers]}",
    )

    # Yield the logger for the test to use
    yield new_logger

    # --- Cleanup: Restore the logging registry to its original state ---
    if original_registry_logger is not None:
        registry[original_logger_name] = original_registry_logger
    else:
        logging.Logger.manager.loggerDict.pop(original_logger_name, None)
