# src/apathetic_logging/get_logger.py
"""GetLogger functionality for Apathetic Logging.

Docstrings are adapted from the standard library logging module documentation
licensed under the Python Software Foundation License Version 2.
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar, cast

from .logger_namespace import (
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
    def _setLoggerClassTemporarily(
        klass: type[ApatheticLogging_Internal_GetLogger._LoggerType],
        name: str,
    ) -> ApatheticLogging_Internal_GetLogger._LoggerType:
        """Temporarily set the logger class, get/create a logger, then restore.

        This is an internal helper function used by getLoggerOfType to create
        a logger of a specific type when one doesn't already exist. It temporarily
        sets the logger class to the desired type, gets or creates the logger,
        then restores the original logger class.

        This function is mostly for internal use by the library. If you need
        a logger of a specific type, use getLoggerOfType instead, which provides
        all the conveniences (name inference, registry checking, etc.).

        Args:
            klass (logger class): The desired logger class type.
            name: The name of the logger to get.

        Returns:
            A logger instance of the specified type.
        """
        original_class = logging.getLoggerClass()
        logging.setLoggerClass(klass)
        logger = logging.getLogger(name)
        logging.setLoggerClass(original_class)
        typed_logger = cast("ApatheticLogging_Internal_GetLogger._LoggerType", logger)
        return typed_logger

    @staticmethod
    def getLogger(
        name: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> ApatheticLogging_Internal_Logger.Logger:
        """Return a logger with the specified name, creating it if necessary.

        Changes:
        - When name is None, infers the name automatically from
          the calling module's __package__ attribute by examining the call stack
          (using skip_frames=2 to correctly identify the caller)
          instead of returning the root logger.
        - When name is an empty string (""), returns the root logger
          as usual, matching standard library behavior.
        - Returns an apathetic_logging.Logger instance instead of
          the standard logging.Logger.

        Args:
            name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.
                If an empty string (""), returns the root logger.
            *args: Additional positional arguments (for future-proofing)
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            A logger of type ApatheticLogging_Internal_Logger.Logger.

        Wrapper for logging.getLogger.

        https://docs.python.org/3.10/library/logging.html#logging.getLogger
        """
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logger = ApatheticLogging_Internal_Logger
        skip_frames = 2
        result = _get_logger.getLoggerOfType(
            name, _logger.Logger, skip_frames, *args, **kwargs
        )
        return cast("ApatheticLogging_Internal_Logger.Logger", result)  # type: ignore[redundant-cast]

    @staticmethod
    def getLoggerOfType(
        name: str | None,
        class_type: type[ApatheticLogging_Internal_GetLogger._LoggerType],
        skip_frames: int = 1,
        *args: Any,
        **kwargs: Any,
    ) -> ApatheticLogging_Internal_GetLogger._LoggerType:
        """Get a logger of the specified type, creating it if necessary.

        Changes:
        - When name is None, infers the name automatically from
          the calling module's __package__ attribute by examining the call stack
          (using skip_frames to correctly identify the caller)
          instead of returning the root logger.
        - When name is an empty string (""), returns the root logger
          as usual, matching standard library behavior.
        - Returns a class_type instance instead of
          the standard logging.Logger.

        Args:
            name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.
                If an empty string (""), returns the root logger.
            class_type: The logger class type to use.
            skip_frames: Number of frames to skip when inferring logger name.
                Prefer using as a keyword argument (e.g., skip_frames=2) for clarity.
            *args: Additional positional arguments (for future-proofing)
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            A logger instance of the specified type.

        Wrapper for logging.getLogger.

        https://docs.python.org/3.10/library/logging.html#logging.getLogger
        """
        _logging_utils = ApatheticLogging_Internal_LoggingUtils

        # Resolve logger name (with inference if needed)
        # Note: Empty string ("") is a special case - resolveLoggerName returns it
        # as-is (root logger, matching stdlib behavior). This is handled by the
        # early return in resolveLoggerName when logger_name is not None.
        # skip_frames+1 because: getLoggerOfType -> resolveLoggerName -> caller
        # check_registry=True because getLogger() should use a previously registered
        # name if available, which is the expected behavior for "get" operations.
        register_name = _logging_utils.resolveLoggerName(
            name,
            check_registry=True,
            skip_frames=skip_frames + 1,
        )

        # extend logging module
        if hasattr(class_type, "extend_logging_module"):
            class_type.extend_logging_module()  # type: ignore[attr-defined]

        # recreate if wrong type
        logger = None
        registered = _logging_utils.hasLogger(register_name)
        if registered:
            logger = logging.getLogger(register_name, *args, **kwargs)
            if not isinstance(logger, class_type):
                _logging_utils.removeLogger(register_name)
                registered = False
        if not registered:  # may have changed above
            logger = ApatheticLogging_Internal_GetLogger._setLoggerClassTemporarily(
                class_type, register_name
            )

        typed_logger = cast("ApatheticLogging_Internal_GetLogger._LoggerType", logger)
        return typed_logger
