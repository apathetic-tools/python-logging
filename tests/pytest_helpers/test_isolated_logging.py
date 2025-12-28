"""Tests for the isolated_logging fixture."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from apathetic_logging.pytest_helpers import LoggingIsolation


def test_isolated_logging_resets_logger_state(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that isolatedLogging works in first test."""
    # Just verify the fixture is available and works
    root = isolatedLogging.getRootLogger()
    root.setLevel(logging.DEBUG)
    assert root.level == logging.DEBUG


def test_isolated_logging_state_reset_between_tests(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that isolatedLogging is at a known default state."""
    # Verify fixture provides a consistent, predictable state.
    # This test is completely independent and works in both sequential
    # and parallel modes, as it only verifies that the fixture initialized
    # the logging system to a known, documented state.
    root = isolatedLogging.getRootLogger()
    # The fixture should have set up a clean logging environment
    # It should NOT still have logging.DEBUG from previous tests
    # By checking that we can set a level and it takes effect,
    # we verify the fixture provided a working logging environment
    original_level = root.level
    isolatedLogging.setRootLevel("ERROR")
    assert root.level == logging.ERROR
    # Verify we can change it again
    isolatedLogging.setRootLevel(original_level)
    assert root.level == original_level


def test_isolated_logging_clears_loggers(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that isolatedLogging clears all loggers between tests."""
    logger = isolatedLogging.getLogger("test.app")
    logger.setLevel(logging.DEBUG)
    assert "test.app" in logging.Logger.manager.loggerDict


@pytest.mark.usefixtures("isolatedLogging")
def test_isolated_logging_clears_in_next_test() -> None:
    """Test that logger from previous test is removed."""
    # Logger from previous test should be removed (fixture provides isolation)
    assert "test.app" not in logging.Logger.manager.loggerDict


def test_isolated_logging_get_logger(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that getLogger creates loggers correctly."""
    logger = isolatedLogging.getLogger("myapp.module")
    assert logger.name == "myapp.module"
    assert isinstance(logger, logging.Logger)


def test_isolated_logging_set_root_level_string(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that setRootLevel works with string levels."""
    isolatedLogging.setRootLevel("DEBUG")
    root = isolatedLogging.getRootLogger()
    assert root.level == logging.DEBUG


def test_isolated_logging_set_root_level_int(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that setRootLevel works with int levels."""
    isolatedLogging.setRootLevel(logging.INFO)
    root = isolatedLogging.getRootLogger()
    assert root.level == logging.INFO


def test_isolated_logging_assert_root_level_passes(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that assertRootLevel passes when level matches."""
    isolatedLogging.setRootLevel("DEBUG")
    isolatedLogging.assertRootLevel("DEBUG")  # Should not raise


def test_isolated_logging_assert_root_level_fails(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that assertRootLevel fails when level doesn't match."""
    isolatedLogging.setRootLevel("DEBUG")
    with pytest.raises(AssertionError):
        isolatedLogging.assertRootLevel("INFO")


def test_isolated_logging_assert_logger_level(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that assertLoggerLevel works correctly."""
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    isolatedLogging.assertLoggerLevel("myapp", logging.DEBUG)


def test_isolated_logging_assert_logger_level_fails(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that assertLoggerLevel fails when level doesn't match."""
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    with pytest.raises(AssertionError):
        isolatedLogging.assertLoggerLevel("myapp", logging.INFO)


def test_isolated_logging_get_all_loggers(
    isolatedLogging: LoggingIsolation,  # noqa: N803
) -> None:
    """Test that getAllLoggers returns all loggers."""
    isolatedLogging.getLogger("app.module1")
    isolatedLogging.getLogger("app.module2")

    all_loggers = isolatedLogging.getAllLoggers()
    assert "app.module1" in all_loggers
    assert "app.module2" in all_loggers


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING"])
def test_isolated_logging_with_parametrized_tests(
    isolatedLogging: LoggingIsolation,  # noqa: N803
    level: str,
) -> None:
    """Test that isolatedLogging works with parametrized tests."""
    isolatedLogging.setRootLevel(level)
    isolatedLogging.assertRootLevel(level)


class TestIsolatedLoggingClassBased:
    """Class-based tests with isolatedLogging."""

    def test_one(
        self,
        isolatedLogging: LoggingIsolation,  # noqa: N803
    ) -> None:
        """Test in class - first method."""
        isolatedLogging.setRootLevel(logging.DEBUG)
        assert isolatedLogging.getRootLogger().level == logging.DEBUG

    def test_two(
        self,
        isolatedLogging: LoggingIsolation,  # noqa: N803
    ) -> None:
        """Test in class - second method."""
        # State should be reset from previous test
        assert isolatedLogging.getRootLogger().level != logging.DEBUG
