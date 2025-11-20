# src/apathetic_logging/get_logger.py
"""GetLogger functionality for Apathetic Logging."""

from __future__ import annotations

import logging
from typing import TypeVar, cast

from .logger import (
    ApatheticLogging_Internal_Logger,
)
from .logging_utils import (
    ApatheticLogging_Internal_LoggingUtils,
)


class ApatheticLogging_Internal_GetLogger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the getLogger static method.

    This class contains the getLogger implementation as a static method.
    When mixed into apathetic_logging, it provides apathetic_logging.getLogger.
    """

    _LoggerType = TypeVar("_LoggerType", bound=logging.Logger)

    @staticmethod
    def getLogger(
        logger_name: str | None = None,
    ) -> ApatheticLogging_Internal_Logger.Logger:
        """Get a logger of type ApatheticLogging_Internal_Logger.Logger.

        Args:
            logger_name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.

        Returns:
            A logger of type ApatheticLogging_Internal_Logger.Logger.

        Raises:
        Note: you must carefully pass skip_frames based on the height of your callstack
        between this function and the logger name resolution. The test
        test_get_logger_auto_infers_from_caller_package must also carefully construct
        an identical callstack to mimic the frames here.
        """
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logger = ApatheticLogging_Internal_Logger
        result = _get_logger.getLoggerOfType(logger_name, _logger.Logger, skip_frames=2)
        return cast("ApatheticLogging_Internal_Logger.Logger", result)  # type: ignore[redundant-cast]

    @staticmethod
    def getLoggerOfType(
        logger_name: str | None,
        logger_class: type[ApatheticLogging_Internal_GetLogger._LoggerType],
        *,
        skip_frames: int = 1,
    ) -> ApatheticLogging_Internal_GetLogger._LoggerType:
        _logging_utils = ApatheticLogging_Internal_LoggingUtils

        # Resolve logger name (with inference if needed)
        # skip_frames+1 because: getLoggerOfType -> resolveLoggerName -> caller
        # check_registry=True because getLogger() should use a previously registered
        # name if available, which is the expected behavior for "get" operations.
        register_name = _logging_utils.resolveLoggerName(
            logger_name,
            check_registry=True,
            skip_frames=skip_frames + 1,
        )

        # extend logging module
        if hasattr(logger_class, "extend_logging_module"):
            logger_class.extend_logging_module()  # type: ignore[attr-defined]

        # recreate if wrong type
        logger = None
        registered = _logging_utils.hasLogger(register_name)
        if registered:
            logger = logging.getLogger(register_name)
            if not isinstance(logger, logger_class):
                _logging_utils.removeLogger(register_name)
                registered = False
        if not registered:
            logger = _logging_utils.setLoggerClassTemporarily(
                register_name, logger_class
            )

        typed_logger = cast("ApatheticLogging_Internal_GetLogger._LoggerType", logger)
        return typed_logger
