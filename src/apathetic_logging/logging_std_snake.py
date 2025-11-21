# src/apathetic_logging/logging_std_snake.py
"""Snake case convenience functions for standard logging module.

Docstrings are adapted from the standard library logging module documentation
licensed under the Python Software Foundation License Version 2.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from types import FrameType
from typing import TYPE_CHECKING, Any

from .get_logger import (
    ApatheticLogging_Internal_GetLogger,
)


if TYPE_CHECKING:
    from .logger_namespace import (
        ApatheticLogging_Internal_Logger,
    )


class ApatheticLogging_Internal_StdSnakeCase:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides snake_case convenience functions for logging.*.

    **Purpose**: Stdlib-compatible wrappers that match the standard library API exactly.

    This class contains snake_case wrapper functions for standard library
    `logging.*` functions that use camelCase naming. These wrappers provide
    a more Pythonic interface that follows PEP 8 naming conventions while
    maintaining **full API compatibility** with the underlying logging module
    functions. The function signatures match the stdlib exactly - extended
    parameters are not part of the signature (though they may be passed via
    `**kwargs` and forwarded to the underlying implementation).

    When mixed into apathetic_logging, it provides snake_case alternatives
    to standard logging module functions (e.g., `basicConfig` -> `basic_config`,
    `addLevelName` -> `add_level_name`, `setLoggerClass` -> `set_logger_class`).

    **Note**: For extended functionality with additional parameters, see
    `ApatheticLogging_Internal_LibSnakeCase`, which wraps apathetic logging's
    library functions with their extended APIs.
    """

    # --- Configuration Functions ---

    @staticmethod
    def basic_config(*args: Any, **kwargs: Any) -> None:
        """Do basic configuration for the logging system.

        This function does nothing if the root logger already has handlers
        configured, unless the keyword argument *force* is set to ``True``.
        It is a convenience method intended for use by simple scripts
        to do one-shot configuration of the logging package.

        The default behaviour is to create a StreamHandler which writes to
        sys.stderr, set a formatter using the BASIC_FORMAT format string, and
        add the handler to the root logger.

        A number of optional keyword arguments may be specified, which can alter
        the default behaviour.

        Wrapper for logging.basicConfig with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.basicConfig
        """
        logging.basicConfig(*args, **kwargs)

    @staticmethod
    def capture_warnings(
        capture: bool,  # noqa: FBT001
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Redirect warnings to the logging package.

        If capture is true, redirect all warnings to the logging package.
        If capture is False, ensure that warnings are not redirected to logging
        but to their original destinations.

        Wrapper for logging.captureWarnings with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.captureWarnings
        """
        logging.captureWarnings(capture, *args, **kwargs)

    @staticmethod
    def shutdown(*args: Any, **kwargs: Any) -> None:
        """Perform any cleanup actions in the logging system.

        Perform any cleanup actions in the logging system (e.g. flushing
        buffers). Should be called at application exit.

        Wrapper for logging.shutdown with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.shutdown
        """
        logging.shutdown(*args, **kwargs)

    # --- Level Management Functions ---

    @staticmethod
    def add_level_name(level: int, level_name: str, *args: Any, **kwargs: Any) -> None:
        """Associate a level name with a numeric level.

        Associate 'level_name' with 'level'. This is used when converting
        levels to text during message formatting.

        Wrapper for logging.addLevelName with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.addLevelName
        """
        logging.addLevelName(level, level_name, *args, **kwargs)

    @staticmethod
    def get_level_name(level: int, *args: Any, **kwargs: Any) -> str:
        """Return the textual or numeric representation of a logging level.

        If the level is one of the predefined levels (CRITICAL, ERROR, WARNING,
        INFO, DEBUG) then you get the corresponding string. If you have
        associated levels with names using addLevelName then the name you have
        associated with 'level' is returned.

        If a numeric value corresponding to one of the defined levels is passed
        in, the corresponding string representation is returned.

        If a string representation of the level is passed in, the corresponding
        numeric value is returned.

        If no matching numeric or string value is passed in, the string
        'Level %s' % level is returned.

        Wrapper for logging.getLevelName with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLevelName
        """
        return logging.getLevelName(level, *args, **kwargs)

    @staticmethod
    def get_level_names_mapping(*args: Any, **kwargs: Any) -> dict[int, str]:
        """Return a mapping of all level names to their numeric values.

        Wrapper for logging.getLevelNamesMapping with snake_case naming.

        https://docs.python.org/3.11/library/logging.html#logging.getLevelNamesMapping
        """
        if sys.version_info < (3, 11):
            msg = (
                "get_level_names_mapping is not available in "
                "Python versions earlier than 3.11"
            )
            raise NotImplementedError(msg)
        return logging.getLevelNamesMapping(*args, **kwargs)

    @staticmethod
    def disable(level: int = 50, *args: Any, **kwargs: Any) -> None:
        """Disable all logging calls of severity 'level' and below.

        Wrapper for logging.disable with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.disable
        """
        logging.disable(level, *args, **kwargs)

    # --- Logger Management Functions ---

    @staticmethod
    def get_logger(
        name: str | None = None, *args: Any, **kwargs: Any
    ) -> ApatheticLogging_Internal_Logger.Logger:
        """Return a logger with the specified name, creating it if necessary.

        **Stdlib-compatible wrapper**: This function matches the standard library
        `logging.getLogger()` API exactly. It only accepts `name` and passes through
        `*args` and `**kwargs` for future-proofing.

        **Note**: Due to Python's method resolution order (MRO), this function is
        shadowed by `ApatheticLogging_Internal_LibSnakeCase.get_logger()` which
        comes earlier in the inheritance chain and provides extended parameters
        (`level`, `minimum_level`). This stdlib-compatible signature is maintained
        for documentation purposes and to show the stdlib API, but the extended
        version from `LibSnakeCase` is the one actually called at runtime.

        If no name is specified, return the root logger.

        Args:
            name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.
                If an empty string (""), returns the root logger.
            *args: Additional positional arguments (for future-proofing)
            **kwargs: Additional keyword arguments (for future-proofing)

        Returns:
            An ApatheticLogging_Internal_Logger.Logger instance.

        Wrapper for logging.getLogger with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLogger
        """
        # Use the custom getLogger from get_logger.py which returns our Logger type
        # Note: This function is shadowed by LibSnakeCase.get_logger() in the MRO
        return ApatheticLogging_Internal_GetLogger.getLogger(name, *args, **kwargs)

    @staticmethod
    def get_logger_class(*args: Any, **kwargs: Any) -> type[logging.Logger]:
        """Return the class to be used when instantiating a logger.

        Wrapper for logging.getLoggerClass with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLoggerClass
        """
        return logging.getLoggerClass(*args, **kwargs)

    @staticmethod
    def set_logger_class(
        klass: type[logging.Logger], *args: Any, **kwargs: Any
    ) -> None:
        """Set the class to be used when instantiating a logger.

        The class should define __init__() such that only a name argument is
        required, and the __init__() should call Logger.__init__().

        Args:
            klass (logger class): The logger class to use.
            *args: Additional positional arguments (for future-proofing).
            **kwargs: Additional keyword arguments (for future-proofing).

        Wrapper for logging.setLoggerClass with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.setLoggerClass
        """
        logging.setLoggerClass(klass, *args, **kwargs)

    # --- Handler Management Functions ---

    @staticmethod
    def get_handler_by_name(
        name: str, *args: Any, **kwargs: Any
    ) -> logging.Handler | None:
        """Get a handler with the specified name, or None if there isn't one.

        Wrapper for logging.getHandlerByName with snake_case naming.

        https://docs.python.org/3.12/library/logging.html#logging.getHandlerByName
        """
        if sys.version_info < (3, 12):
            msg = (
                "get_handler_by_name is not available in "
                "Python versions earlier than 3.12"
            )
            raise NotImplementedError(msg)
        return logging.getHandlerByName(name, *args, **kwargs)

    @staticmethod
    def get_handler_names(*args: Any, **kwargs: Any) -> list[str]:
        """Return all known handler names as an immutable set.

        Wrapper for logging.getHandlerNames with snake_case naming.

        https://docs.python.org/3.12/library/logging.html#logging.getHandlerNames
        """
        if sys.version_info < (3, 12):
            msg = (
                "get_handler_names is not available in "
                "Python versions earlier than 3.12"
            )
            raise NotImplementedError(msg)
        return logging.getHandlerNames(*args, **kwargs)

    # --- Factory Functions ---

    @staticmethod
    def get_log_record_factory(
        *args: Any, **kwargs: Any
    ) -> Callable[..., logging.LogRecord]:
        """Return the factory to be used when instantiating a log record.

        Wrapper for logging.getLogRecordFactory with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.getLogRecordFactory
        """
        return logging.getLogRecordFactory(*args, **kwargs)

    @staticmethod
    def set_log_record_factory(
        factory: Callable[..., logging.LogRecord], *args: Any, **kwargs: Any
    ) -> None:
        """Set the factory to be used when instantiating a log record.

        :param factory: A callable which will be called to instantiate
        a log record.

        Wrapper for logging.setLogRecordFactory with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.setLogRecordFactory
        """
        logging.setLogRecordFactory(factory, *args, **kwargs)

    @staticmethod
    def make_log_record(
        dict: dict[str, Any],  # noqa: A002
        *args: Any,
        **kwargs: Any,
    ) -> logging.LogRecord:
        """Make a LogRecord whose attributes are defined by a dictionary.

        This function is useful for converting a logging event received over
        a socket connection (which is sent as a dictionary) into a LogRecord
        instance.

        Wrapper for logging.makeLogRecord with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.makeLogRecord
        """
        return logging.makeLogRecord(dict, *args, **kwargs)

    # --- Logging Functions ---

    @staticmethod
    def critical(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'CRITICAL' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.critical with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.critical
        """
        logging.critical(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def debug(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'DEBUG' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.debug with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.debug
        """
        logging.debug(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def error(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'ERROR' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.error with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.error
        """
        logging.error(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def exception(msg: str, *args: Any, exc_info: bool = True, **kwargs: Any) -> None:
        """Log a message with severity 'ERROR' on the root logger, with exception info.

        If the logger has no handlers, basicConfig() is called to add a console
        handler with a pre-defined format.

        Wrapper for logging.exception with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.exception
        """
        logging.exception(msg, *args, exc_info=exc_info, **kwargs)  # noqa: LOG015

    @staticmethod
    def fatal(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'CRITICAL' on the root logger.

        Don't use this function, use critical() instead.

        Wrapper for logging.fatal with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.fatal
        """
        logging.fatal(msg, *args, **kwargs)

    @staticmethod
    def info(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'INFO' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.info with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.info
        """
        logging.info(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def log(level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log 'msg % args' with the integer severity 'level' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.log with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.log
        """
        logging.log(level, msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def warn(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'WARNING' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.warn with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.warn
        """
        logging.warning(msg, *args, **kwargs)  # noqa: LOG015

    @staticmethod
    def warning(msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with severity 'WARNING' on the root logger.

        If the logger has no handlers, call basicConfig() to add a console
        handler with a pre-defined format.

        Wrapper for logging.warning with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.warning
        """
        logging.warning(msg, *args, **kwargs)  # noqa: LOG015

    # --- Utility Functions ---

    @staticmethod
    def currentframe(*args: Any, **kwargs: Any) -> FrameType | None:
        """Return the frame object for the caller's stack frame.

        Wrapper for logging.currentframe with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.currentframe
        """
        return logging.currentframe(*args, **kwargs)
