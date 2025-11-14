# src/apathetic_logging/get_logger.py
"""GetLogger functionality for Apathetic Logging."""

from __future__ import annotations

import inspect
import logging
from typing import Any, cast

from .register_logger_name import (
    ApatheticLogging_Priv_RegisterLoggerName,  # pyright: ignore[reportPrivateUsage]
)
from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)
from .test_trace import (
    ApatheticLogging_Priv_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


class ApatheticLogging_Priv_GetLogger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the get_logger static method.

    This class contains the get_logger implementation as a static method.
    When mixed into apathetic_logging, it provides apathetic_logging.get_logger.
    """

    @staticmethod
    def get_logger() -> Any:  # Returns apathetic_logging.Logger
        """Return the registered logger instance.

        Uses Python's built-in logging registry (logging.getLogger()) to retrieve
        the logger. If no logger name has been registered, attempts to auto-infer
        the logger name from the calling module's top-level package.

        Returns:
            The logger instance from logging.getLogger()
            (as apathetic_logging.Logger type)

        Raises:
            RuntimeError: If called before a logger name has been registered and
                auto-inference fails.

        Note:
            This function is used internally by utils_logs.py. Applications
            should use their app-specific getter (e.g., get_app_logger()) for
            better type hints.
        """
        registered_logger_name = (
            ApatheticLogging_Priv_Registry.registered_priv_logger_name
        )

        if registered_logger_name is None:
            # Try to auto-infer from the calling module's package
            frame = inspect.currentframe()
            if frame is not None:
                try:
                    # Get the calling frame (skip get_logger itself)
                    caller_frame = frame.f_back
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
                                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                                    "get_logger() auto-inferred logger name",
                                    f"name={inferred_name}",
                                    f"from_module={caller_module}",
                                )
                finally:
                    del frame

        if registered_logger_name is None:
            _msg = (
                "Logger name not registered and could not be auto-inferred. "
                "Call register_logger_name() or ensure your app's logs "
                "module is imported."
            )
            raise RuntimeError(_msg)

        logger = logging.getLogger(registered_logger_name)
        typed_logger = cast("Any", logger)  # apathetic_logging.Logger
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "get_logger() called",
            f"name={typed_logger.name}",
            f"id={id(typed_logger)}",
            f"level={typed_logger.level_name}",
            f"handlers={[type(h).__name__ for h in typed_logger.handlers]}",
        )
        return typed_logger
