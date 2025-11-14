"""Shared fixtures and helper classes for custom logger integration tests."""

import argparse
import logging
import os
from collections.abc import Generator

import pytest

import apathetic_logging as mod_alogs
import apathetic_logging.registry as mod_registry


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_registry_and_env() -> Generator[None, None, None]:
    """Reset registry state and environment variables before and after each test."""
    # Save original state
    registry = mod_registry.ApatheticLogging_Priv_Registry  # pyright: ignore[reportPrivateUsage]
    original_name = registry.registered_priv_logger_name
    original_default = registry.registered_priv_default_log_level
    original_env_vars = registry.registered_priv_log_level_env_vars
    original_env = os.environ.get("TESTAPP_LOG_LEVEL")
    original_log_level = os.environ.get("LOG_LEVEL")

    # Reset state
    registry.registered_priv_logger_name = None
    registry.registered_priv_default_log_level = None
    registry.registered_priv_log_level_env_vars = None
    if "TESTAPP_LOG_LEVEL" in os.environ:
        del os.environ["TESTAPP_LOG_LEVEL"]
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]

    yield

    # Restore original state
    registry.registered_priv_logger_name = original_name
    registry.registered_priv_default_log_level = original_default
    registry.registered_priv_log_level_env_vars = original_env_vars
    if original_env is not None:
        os.environ["TESTAPP_LOG_LEVEL"] = original_env
    if original_log_level is not None:
        os.environ["LOG_LEVEL"] = original_log_level


# ----------------------------------------------------------------------
# Helper Classes for Testing
# ----------------------------------------------------------------------


class AppLoggerForTest(mod_alogs.ApatheticLogging.Logger):
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


class AppLoggerWithCustomMethodForTest(mod_alogs.ApatheticLogging.Logger):
    """Test logger with custom application-specific methods."""

    def log_operation(self, operation: str, status: str) -> None:
        """Log an operation with consistent formatting."""
        self.info(f"[{operation}] Status: {status}")

    def log_performance(self, metric: str, value: float) -> None:
        """Log performance metrics."""
        if self.isEnabledFor(logging.DEBUG):
            self.debug(f"Performance: {metric} = {value:.2f}")
