# src/apathetic_logging/get_logger.py
"""GetLogger functionality for Apathetic Logging."""

from __future__ import annotations

import inspect
import logging
from typing import Protocol, TypeVar, cast

from .logger import (
    ApatheticLogging_Internal_Logger,
)
from .logging_utils import (
    ApatheticLogging_Internal_LoggingUtils,
)
from .registry import (
    ApatheticLogging_Internal_Registry,
)
from .registry_data import (
    ApatheticLogging_Internal_RegistryData,
)


_T = TypeVar("_T", bound=logging.Logger)


class _LoggerClassWithExtend(Protocol):
    """Protocol for logger classes that have extend_logging_module()."""

    @classmethod
    def extend_logging_module(cls) -> bool:
        """Extend the logging module with custom levels."""
        ...


class ApatheticLogging_Internal_GetLogger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the get_logger static method.

    This class contains the get_logger implementation as a static method.
    When mixed into apathetic_logging, it provides apathetic_logging.get_logger.
    """

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
        between this function and resolve_logger_name. The test
        test_get_logger_auto_infers_from_caller_package must also carefully construct
        an identical callstack to mimic the frames here.
        """
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logger = ApatheticLogging_Internal_Logger
        return _get_logger.get_logger_of_type(
            logger_name, _logger.Logger, skip_frames=2
        )

    @staticmethod
    def get_logger_of_type(
        logger_name: str | None, logger_class: type[_T], *, skip_frames: int = 1
    ) -> _T:
        _get_logger = ApatheticLogging_Internal_GetLogger
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        register_name = _get_logger.resolve_logger_name(
            logger_name, skip_frames=skip_frames
        )
        registered = _logging_utils.has_logger(register_name)

        logger = None
        if registered:
            logger = logging.getLogger(register_name)
            if not isinstance(logger, logger_class):
                _logging_utils.remove_logger(register_name)

        logger = logging.getLogger(register_name)

        if not hasattr(logger, "level_name"):
            if _logging_utils.has_logger(register_name):
                _logging_utils.remove_logger(register_name)
            logger = logging.getLogger(register_name)

        typed_logger = cast("_T", logger)
        return typed_logger

    @staticmethod
    def resolve_logger_name(logger_name: str | None, *, skip_frames: int = 2) -> str:
        _registry = ApatheticLogging_Internal_Registry
        _registry_data = ApatheticLogging_Internal_RegistryData
        if logger_name is not None:
            return logger_name

        registered_logger_name = _registry_data.registered_internal_logger_name

        if registered_logger_name is None:
            # Try to auto-infer from the calling module's package
            frame = inspect.currentframe()
            if frame is not None:
                try:
                    # Skip the specified number of frames to get to the actual caller
                    caller_frame = frame.f_back
                    for _ in range(skip_frames):
                        if caller_frame is None:
                            break
                        caller_frame = caller_frame.f_back
                    if caller_frame is not None:
                        caller_module = caller_frame.f_globals.get("__package__")
                        if caller_module:
                            _extract = _registry.extract_top_level_package
                            inferred_name = _extract(caller_module)
                            if inferred_name:
                                _registry_data.registered_internal_logger_name = (
                                    inferred_name
                                )
                                registered_logger_name = inferred_name
                finally:
                    del frame

        if registered_logger_name is None:
            _msg = (
                "Logger name not registered and could not be auto-inferred. "
                "Call register_logger_name() or ensure your app's logs "
                "module is imported."
            )
            raise RuntimeError(_msg)

        return registered_logger_name

    @staticmethod
    def _ensure_logger_has_level_name(
        logger_name: str,
        logger_class: type[_LoggerClassWithExtend] | None = None,
    ) -> logging.Logger:
        _logger = ApatheticLogging_Internal_Logger
        _logging_utils = ApatheticLogging_Internal_LoggingUtils
        extend_class = logger_class if logger_class is not None else _logger.Logger

        logger_exists = _logging_utils.has_logger(logger_name)

        if not logger_exists:
            extend_class.extend_logging_module()
            logging.setLoggerClass(cast("type[logging.Logger]", extend_class))
            if _logging_utils.has_logger(logger_name):
                _logging_utils.remove_logger(logger_name)
            logger = logging.getLogger(logger_name)
        else:
            logger = logging.getLogger(logger_name)
            if not hasattr(logger, "level_name"):
                extend_class.extend_logging_module()
                logging.setLoggerClass(cast("type[logging.Logger]", extend_class))
                _logging_utils.remove_logger(logger_name)
                logger = logging.getLogger(logger_name)

        return logger
