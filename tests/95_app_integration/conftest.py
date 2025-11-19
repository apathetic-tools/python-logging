# tests/95_app_integration/conftest.py
"""Shared fixtures and helper classes for custom logger integration tests."""

import argparse
import logging
import os
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry_data as mod_registry


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_registry_and_env() -> Generator[None, None, None]:
    """Reset registry state, environment variables, and logger class.

    Runs before and after each test.
    """
    # Save original state
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData
    original_name = _registry.registered_internal_logger_name
    original_default = _registry.registered_internal_default_log_level
    original_env_vars = _registry.registered_internal_log_level_env_vars
    original_env = os.environ.get("TESTAPP_LOG_LEVEL")
    original_log_level = os.environ.get("LOG_LEVEL")
    original_logger_class = logging.getLoggerClass()

    # Reset state
    _registry.registered_internal_logger_name = None
    _registry.registered_internal_default_log_level = None
    _registry.registered_internal_log_level_env_vars = None
    if "TESTAPP_LOG_LEVEL" in os.environ:
        del os.environ["TESTAPP_LOG_LEVEL"]
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]
    # Clear any existing loggers from the registry
    _logging_utils = mod_alogs.apathetic_logging
    logger_names = list(logging.Logger.manager.loggerDict.keys())
    for logger_name in logger_names:
        _logging_utils.remove_logger(logger_name)
    # Reset logger class to default before test (may have been changed by other tests)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extend_logging_module()

    yield

    # Restore original state
    _registry.registered_internal_logger_name = original_name
    _registry.registered_internal_default_log_level = original_default
    _registry.registered_internal_log_level_env_vars = original_env_vars
    if original_env is not None:
        os.environ["TESTAPP_LOG_LEVEL"] = original_env
    if original_log_level is not None:
        os.environ["LOG_LEVEL"] = original_log_level
    # Reset logger class to original after test
    logging.setLoggerClass(original_logger_class)
    # Re-extend with the default Logger class to ensure it's set correctly
    mod_alogs.Logger.extend_logging_module()


# ----------------------------------------------------------------------
# Helper Classes for Testing
# ----------------------------------------------------------------------


class AppLoggerForTest(Logger):
    """Test application logger with custom log level resolution."""

    def determine_log_level(
        self,
        *,
        args: argparse.Namespace | None = None,
        root_log_level: str | None = None,
    ) -> str:
        """Resolve log level from CLI → env → root config → default."""
        # Check command-line arguments first
        if args is not None:
            args_level = getattr(args, "log_level", None)
            if args_level is not None and args_level:
                return str(args_level).upper()

        # Check environment variables
        env_vars = ["TESTAPP_LOG_LEVEL", "LOG_LEVEL"]
        for env_var in env_vars:
            env_log_level = os.getenv(env_var)
            if env_log_level:
                return env_log_level.upper()

        # Fall back to root logger level if set
        if root_log_level:
            return root_log_level.upper()

        # Use application default
        return "INFO"


class AppLoggerWithCustomMethodForTest(Logger):
    """Test logger with custom application-specific methods."""

    def log_operation(self, operation: str, status: str) -> None:
        """Log an operation with consistent formatting."""
        self.info(f"[{operation}] Status: {status}")

    def log_performance(self, metric: str, value: float) -> None:
        """Log performance metrics."""
        if self.isEnabledFor(logging.DEBUG):
            self.debug(f"Performance: {metric} = {value:.2f}")
