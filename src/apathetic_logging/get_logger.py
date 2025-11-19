# src/apathetic_logging/get_logger.py
"""GetLogger functionality for Apathetic Logging."""

from __future__ import annotations

import inspect
import logging
from typing import TypeVar, cast

from .logger import (
    ApatheticLogging_Priv_Logger,  # pyright: ignore[reportPrivateUsage]
)
from .register_logger_name import (
    ApatheticLogging_Priv_RegisterLoggerName,  # pyright: ignore[reportPrivateUsage]
)
from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)


_T = TypeVar("_T", bound=logging.Logger)


class ApatheticLogging_Priv_GetLogger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the get_logger static method.

    This class contains the get_logger implementation as a static method.
    When mixed into apathetic_logging, it provides apathetic_logging.get_logger.
    """

    @staticmethod
    def get_logger(
        logger_name: str | None = None,
    ) -> ApatheticLogging_Priv_Logger.Logger:
        """Get a logger of type ApatheticLogging_Priv_Logger.Logger.

        Args:
            logger_name: The name of the logger to get. If None, the logger name
                will be auto-inferred from the calling module's __package__.

        Returns:
            A logger of type ApatheticLogging_Priv_Logger.Logger.

        Raises:
        Note: you must carefully pass skip_frames based on the height of your callstack
        between this function and _resolve_logger_name. The test
        test_get_logger_auto_infers_from_caller_package must also carefully construct
        an identical callstack to mimic the frames here.
        """
        return ApatheticLogging_Priv_GetLogger.get_logger_of_type(
            logger_name, ApatheticLogging_Priv_Logger.Logger, skip_frames=2
        )

    @staticmethod
    def get_logger_of_type(
        logger_name: str | None, _logger_class: type[_T], *, skip_frames: int = 1
    ) -> _T:
        registered_logger_name = ApatheticLogging_Priv_GetLogger._resolve_logger_name(
            logger_name, skip_frames=skip_frames
        )
        logger = logging.getLogger(registered_logger_name)

        if not hasattr(logger, "level_name"):
            if registered_logger_name in logging.Logger.manager.loggerDict:
                logging.Logger.manager.loggerDict.pop(registered_logger_name, None)
            logger = logging.getLogger(registered_logger_name)

        typed_logger = cast("_T", logger)
        return typed_logger

    @staticmethod
    def _resolve_logger_name(logger_name: str | None, *, skip_frames: int = 2) -> str:
        if logger_name is not None:
            return logger_name

        registered_logger_name = (
            ApatheticLogging_Priv_Registry.registered_priv_logger_name
        )

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
                            _extract = (
                                ApatheticLogging_Priv_RegisterLoggerName._extract_top_level_package  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
                            )
                            inferred_name = _extract(caller_module)
                            if inferred_name:
                                registry = ApatheticLogging_Priv_Registry
                                registry.registered_priv_logger_name = inferred_name
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
