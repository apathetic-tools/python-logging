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
    """Mixin class that provides the get_logger static method.

    This class contains the get_logger implementation as a static method.
    When mixed into apathetic_logging, it provides apathetic_logging.get_logger.
    """

    _LoggerType = TypeVar("_LoggerType", bound=logging.Logger)

    @staticmethod
    def get_logger(
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
        result = _get_logger.get_logger_of_type(
            logger_name, _logger.Logger, skip_frames=2
        )
        return cast("ApatheticLogging_Internal_Logger.Logger", result)  # type: ignore[redundant-cast]

    @staticmethod
    def get_logger_of_type(
        logger_name: str | None,
        logger_class: type[ApatheticLogging_Internal_GetLogger._LoggerType],
        *,
        skip_frames: int = 1,
    ) -> ApatheticLogging_Internal_GetLogger._LoggerType:
        _logging_utils = ApatheticLogging_Internal_LoggingUtils

        # Resolve logger name (with inference if needed)
        # skip_frames+1 because: get_logger_of_type -> resolve_logger_name -> caller
        # check_registry=True because get_logger() should use a previously registered
        # name if available, which is the expected behavior for "get" operations.
        register_name = _logging_utils.resolve_logger_name(
            logger_name,
            check_registry=True,
            skip_frames=skip_frames + 1,
        )

        # extend logging module
        if hasattr(logger_class, "extend_logging_module"):
            logger_class.extend_logging_module()  # type: ignore[attr-defined]

        # recreate if wrong type
        logger = None
        registered = _logging_utils.has_logger(register_name)
        if registered:
            logger = logging.getLogger(register_name)
            if not isinstance(logger, logger_class):
                _logging_utils.remove_logger(register_name)
                registered = False
        if not registered:
            logger = _logging_utils.set_logger_class_temporarily(
                register_name, logger_class
            )

        typed_logger = cast("ApatheticLogging_Internal_GetLogger._LoggerType", logger)
        return typed_logger
