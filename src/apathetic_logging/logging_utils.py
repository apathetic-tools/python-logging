# src/apathetic_logging/logging_utils.py
"""Logging utilities for Apathetic Logging."""

from __future__ import annotations

import logging
from typing import TypeVar, cast


_LoggerType = TypeVar("_LoggerType", bound=logging.Logger)


class ApatheticLogging_Internal_LoggingUtils:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides helper functions for the standard logging module.

    This class contains utility functions that operate directly on or replace
    standard library `logging.*` utilities and functions. These helpers extend
    or wrap the built-in logging module functionality to provide enhanced
    capabilities or safer alternatives.

    When mixed into apathetic_logging, it provides utility functions that
    interact with Python's standard logging module.
    """

    @staticmethod
    def has_logger(logger_name: str) -> bool:
        """Check if a logger exists in the logging manager's registry.

        Args:
            logger_name: The name of the logger to check.

        Returns:
            True if the logger exists in the registry, False otherwise.
        """
        return logger_name in logging.Logger.manager.loggerDict

    @staticmethod
    def remove_logger(logger_name: str) -> None:
        """Remove a logger from the logging manager's registry.

        Args:
            logger_name: The name of the logger to remove.
        """
        logging.Logger.manager.loggerDict.pop(logger_name, None)

    @staticmethod
    def set_logger_class_temporarily(
        logger_name: str, logger_class: type[_LoggerType]
    ) -> _LoggerType:
        """Temporarily set the logger class, get/create a logger, then restore.

        This function temporarily sets the logger class to the desired type,
        gets or creates the logger, then restores the original logger class.

        Args:
            logger_name: The name of the logger to get.
            logger_class: The desired logger class type.

        Returns:
            A logger instance of the specified type.
        """
        original_class = logging.getLoggerClass()
        logging.setLoggerClass(logger_class)
        logger = logging.getLogger(logger_name)
        logging.setLoggerClass(original_class)
        typed_logger = cast("_LoggerType", logger)
        return typed_logger
