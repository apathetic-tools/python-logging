"""Tests for the isolated_logging fixture."""

import logging

import pytest


def test_isolated_logging_resets_logger_state(isolatedLogging: object) -> None:  # noqa: N803
    """Test that isolatedLogging works in first test."""
    # Just verify the fixture is available and works
    isolation = isolatedLogging  # type: ignore[assignment]
    root = isolation.getRootLogger()
    root.setLevel(logging.DEBUG)
    assert root.level == logging.DEBUG


def test_isolated_logging_state_reset_between_tests(isolatedLogging: object) -> None:  # noqa: N803
    """Test that isolatedLogging resets state between tests."""
    # Verify state is reset from previous test
    isolation = isolatedLogging  # type: ignore[assignment]
    root = isolation.getRootLogger()
    # Root level should be reset, not DEBUG from previous test
    assert root.level != logging.DEBUG


def test_isolated_logging_clears_loggers(isolatedLogging: object) -> None:  # noqa: N803
    """Test that isolatedLogging clears all loggers between tests."""
    isolation = isolatedLogging  # type: ignore[assignment]
    logger = isolation.getLogger("test.app")
    logger.setLevel(logging.DEBUG)
    assert "test.app" in logging.Logger.manager.loggerDict


@pytest.mark.usefixtures("isolatedLogging")
def test_isolated_logging_clears_in_next_test() -> None:
    """Test that logger from previous test is removed."""
    # Logger from previous test should be removed (fixture provides isolation)
    assert "test.app" not in logging.Logger.manager.loggerDict


def test_isolated_logging_get_logger(isolatedLogging: object) -> None:  # noqa: N803
    """Test that getLogger creates loggers correctly."""
    isolation = isolatedLogging  # type: ignore[assignment]
    logger = isolation.getLogger("myapp.module")
    assert logger.name == "myapp.module"
    assert isinstance(logger, logging.Logger)


def test_isolated_logging_set_root_level_string(isolatedLogging: object) -> None:  # noqa: N803
    """Test that setRootLevel works with string levels."""
    isolation = isolatedLogging  # type: ignore[assignment]
    isolation.setRootLevel("DEBUG")
    root = isolation.getRootLogger()
    assert root.level == logging.DEBUG


def test_isolated_logging_set_root_level_int(isolatedLogging: object) -> None:  # noqa: N803
    """Test that setRootLevel works with int levels."""
    isolation = isolatedLogging  # type: ignore[assignment]
    isolation.setRootLevel(logging.INFO)
    root = isolation.getRootLogger()
    assert root.level == logging.INFO


def test_isolated_logging_assert_root_level_passes(isolatedLogging: object) -> None:  # noqa: N803
    """Test that assertRootLevel passes when level matches."""
    isolation = isolatedLogging  # type: ignore[assignment]
    isolation.setRootLevel("DEBUG")
    isolation.assertRootLevel("DEBUG")  # Should not raise


def test_isolated_logging_assert_root_level_fails(isolatedLogging: object) -> None:  # noqa: N803
    """Test that assertRootLevel fails when level doesn't match."""
    isolation = isolatedLogging  # type: ignore[assignment]
    isolation.setRootLevel("DEBUG")
    with pytest.raises(AssertionError):
        isolation.assertRootLevel("INFO")


def test_isolated_logging_assert_logger_level(isolatedLogging: object) -> None:  # noqa: N803
    """Test that assertLoggerLevel works correctly."""
    isolation = isolatedLogging  # type: ignore[assignment]
    logger = isolation.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    isolation.assertLoggerLevel("myapp", logging.DEBUG)


def test_isolated_logging_assert_logger_level_fails(isolatedLogging: object) -> None:  # noqa: N803
    """Test that assertLoggerLevel fails when level doesn't match."""
    isolation = isolatedLogging  # type: ignore[assignment]
    logger = isolation.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    with pytest.raises(AssertionError):
        isolation.assertLoggerLevel("myapp", logging.INFO)


def test_isolated_logging_get_all_loggers(isolatedLogging: object) -> None:  # noqa: N803
    """Test that getAllLoggers returns all loggers."""
    isolation = isolatedLogging  # type: ignore[assignment]
    isolation.getLogger("app.module1")
    isolation.getLogger("app.module2")

    all_loggers = isolation.getAllLoggers()
    assert "app.module1" in all_loggers
    assert "app.module2" in all_loggers


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING"])
def test_isolated_logging_with_parametrized_tests(
    isolatedLogging: object,  # noqa: N803
    level: str,
) -> None:
    """Test that isolatedLogging works with parametrized tests."""
    isolation = isolatedLogging  # type: ignore[assignment]
    isolation.setRootLevel(level)
    isolation.assertRootLevel(level)


class TestIsolatedLoggingClassBased:
    """Class-based tests with isolatedLogging."""

    def test_one(self, isolatedLogging: object) -> None:  # noqa: N803
        """Test in class - first method."""
        isolation = isolatedLogging  # type: ignore[assignment]
        isolation.setRootLevel(logging.DEBUG)
        assert isolation.getRootLogger().level == logging.DEBUG

    def test_two(self, isolatedLogging: object) -> None:  # noqa: N803
        """Test in class - second method."""
        isolation = isolatedLogging  # type: ignore[assignment]
        # State should be reset from previous test
        assert isolation.getRootLogger().level != logging.DEBUG
