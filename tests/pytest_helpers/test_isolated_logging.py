"""Tests for the isolated_logging fixture."""

import logging

import pytest


def test_isolated_logging_resets_logger_state(isolated_logging: object) -> None:
    """Test that isolated_logging works in first test."""
    # Just verify the fixture is available and works
    isolation = isolated_logging  # type: ignore[assignment]
    root = isolation.get_root_logger()
    root.setLevel(logging.DEBUG)
    assert root.level == logging.DEBUG


def test_isolated_logging_state_reset_between_tests(isolated_logging: object) -> None:
    """Test that isolated_logging resets state between tests."""
    # Verify state is reset from previous test
    isolation = isolated_logging  # type: ignore[assignment]
    root = isolation.get_root_logger()
    # Root level should be reset, not DEBUG from previous test
    assert root.level != logging.DEBUG


def test_isolated_logging_clears_loggers(isolated_logging: object) -> None:
    """Test that isolated_logging clears all loggers between tests."""
    isolation = isolated_logging  # type: ignore[assignment]
    logger = isolation.get_logger("test.app")
    logger.setLevel(logging.DEBUG)
    assert "test.app" in logging.Logger.manager.loggerDict


@pytest.mark.usefixtures("isolated_logging")
def test_isolated_logging_clears_in_next_test() -> None:
    """Test that logger from previous test is removed."""
    # Logger from previous test should be removed (fixture provides isolation)
    assert "test.app" not in logging.Logger.manager.loggerDict


def test_isolated_logging_get_logger(isolated_logging: object) -> None:
    """Test that get_logger creates loggers correctly."""
    isolation = isolated_logging  # type: ignore[assignment]
    logger = isolation.get_logger("myapp.module")
    assert logger.name == "myapp.module"
    assert isinstance(logger, logging.Logger)


def test_isolated_logging_set_root_level_string(isolated_logging: object) -> None:
    """Test that set_root_level works with string levels."""
    isolation = isolated_logging  # type: ignore[assignment]
    isolation.set_root_level("DEBUG")
    root = isolation.get_root_logger()
    assert root.level == logging.DEBUG


def test_isolated_logging_set_root_level_int(isolated_logging: object) -> None:
    """Test that set_root_level works with int levels."""
    isolation = isolated_logging  # type: ignore[assignment]
    isolation.set_root_level(logging.INFO)
    root = isolation.get_root_logger()
    assert root.level == logging.INFO


def test_isolated_logging_assert_root_level_passes(isolated_logging: object) -> None:
    """Test that assert_root_level passes when level matches."""
    isolation = isolated_logging  # type: ignore[assignment]
    isolation.set_root_level("DEBUG")
    isolation.assert_root_level("DEBUG")  # Should not raise


def test_isolated_logging_assert_root_level_fails(isolated_logging: object) -> None:
    """Test that assert_root_level fails when level doesn't match."""
    isolation = isolated_logging  # type: ignore[assignment]
    isolation.set_root_level("DEBUG")
    with pytest.raises(AssertionError):
        isolation.assert_root_level("INFO")


def test_isolated_logging_assert_logger_level(isolated_logging: object) -> None:
    """Test that assert_logger_level works correctly."""
    isolation = isolated_logging  # type: ignore[assignment]
    logger = isolation.get_logger("myapp")
    logger.setLevel(logging.DEBUG)
    isolation.assert_logger_level("myapp", logging.DEBUG)


def test_isolated_logging_assert_logger_level_fails(isolated_logging: object) -> None:
    """Test that assert_logger_level fails when level doesn't match."""
    isolation = isolated_logging  # type: ignore[assignment]
    logger = isolation.get_logger("myapp")
    logger.setLevel(logging.DEBUG)
    with pytest.raises(AssertionError):
        isolation.assert_logger_level("myapp", logging.INFO)


def test_isolated_logging_get_all_loggers(isolated_logging: object) -> None:
    """Test that get_all_loggers returns all loggers."""
    isolation = isolated_logging  # type: ignore[assignment]
    isolation.get_logger("app.module1")
    isolation.get_logger("app.module2")

    all_loggers = isolation.get_all_loggers()
    assert "app.module1" in all_loggers
    assert "app.module2" in all_loggers


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING"])
def test_isolated_logging_with_parametrized_tests(
    isolated_logging: object,
    level: str,
) -> None:
    """Test that isolated_logging works with parametrized tests."""
    isolation = isolated_logging  # type: ignore[assignment]
    isolation.set_root_level(level)
    isolation.assert_root_level(level)


class TestIsolatedLoggingClassBased:
    """Class-based tests with isolated_logging."""

    def test_one(self, isolated_logging: object) -> None:
        """Test in class - first method."""
        isolation = isolated_logging  # type: ignore[assignment]
        isolation.set_root_level(logging.DEBUG)
        assert isolation.get_root_logger().level == logging.DEBUG

    def test_two(self, isolated_logging: object) -> None:
        """Test in class - second method."""
        isolation = isolated_logging  # type: ignore[assignment]
        # State should be reset from previous test
        assert isolation.get_root_logger().level != logging.DEBUG
