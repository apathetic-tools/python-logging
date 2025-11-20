# tests/95_app_integration/conftest.py
"""Shared fixtures and helper classes for custom logger integration tests."""

import argparse
import logging
import os
from typing import TYPE_CHECKING

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Helper Classes for Testing
# ----------------------------------------------------------------------


class AppLoggerForTest(Logger):
    """Test application logger with custom log level resolution."""

    def determineLogLevel(
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
