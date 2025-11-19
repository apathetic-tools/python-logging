# tests/utils/log_fixtures.py
"""Reusable fixtures for testing the Apathetic logger system."""

import uuid
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs

from .patch_everywhere import patch_everywhere
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
    return logger


@pytest.fixture
def module_logger(monkeypatch: pytest.MonkeyPatch) -> Logger:
    """Replace get_logger() everywhere with a new isolated instance.

    Ensures all modules calling get_logger()
    will use this test logger for the duration of the test.

    Automatically reverts after test completion.

    Default log level is set to "test" for maximum verbosity in test output.
    """
    new_logger = mod_alogs.Logger(f"isolated_logger{_suffix()}")
    new_logger.setLevel("test")
    patch_everywhere(monkeypatch, mod_alogs, "get_logger", lambda: new_logger)
    safe_trace(
        "module_logger fixture",
        f"id={id(new_logger)}",
        f"level={new_logger.level_name}",
        f"handlers={[type(h).__name__ for h in new_logger.handlers]}",
    )
    return new_logger
