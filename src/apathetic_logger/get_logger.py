"""GetLogger functionality for Apathetic Logger."""

from __future__ import annotations

import inspect
import logging
import sys
from typing import Any, cast

from .register_logger_name import (
    _ApatheticLogger_RegisterLoggerName,  # pyright: ignore[reportPrivateUsage]
)
from .test_trace import (
    _ApatheticLogger_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


def _get_namespace_module() -> Any:
    """Get the namespace module at runtime.

    This avoids circular import issues by accessing the namespace
    through the module system after it's been created.
    """
    # Access through sys.modules to avoid circular import
    namespace_module = sys.modules.get("apathetic_logger.namespace")
    if namespace_module is None:
        # Fallback: import if not yet loaded
        namespace_module = sys.modules["apathetic_logger.namespace"]
    return namespace_module


class _ApatheticLogger_GetLogger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the get_logger static method.

    This class contains the get_logger implementation as a static method.
    When mixed into ApatheticLogger, it provides ApatheticLogger.get_logger.
    """

    @staticmethod
    def get_logger() -> Any:  # Returns ApatheticLogger.Logger
        """Return the registered logger instance.

        Uses Python's built-in logging registry (logging.getLogger()) to retrieve
        the logger. If no logger name has been registered, attempts to auto-infer
        the logger name from the calling module's top-level package.

        Returns:
            The logger instance from logging.getLogger()
            (as ApatheticLogger.Logger type)

        Raises:
            RuntimeError: If called before a logger name has been registered and
                auto-inference fails.

        Note:
            This function is used internally by utils_logs.py. Applications
            should use their app-specific getter (e.g., get_app_logger()) for
            better type hints.
        """
        namespace_module = _get_namespace_module()
        registered_logger_name = getattr(
            namespace_module, "_registered_logger_name", None
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
                                _ApatheticLogger_RegisterLoggerName._extract_top_level_package  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
                            )
                            inferred_name = _extract(caller_module)
                            if inferred_name:
                                namespace_module._registered_logger_name = inferred_name  # noqa: SLF001
                                registered_logger_name = inferred_name
                                _ApatheticLogger_TestTrace.TEST_TRACE(
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
        typed_logger = cast("Any", logger)  # ApatheticLogger.Logger
        _ApatheticLogger_TestTrace.TEST_TRACE(
            "get_logger() called",
            f"name={typed_logger.name}",
            f"id={id(typed_logger)}",
            f"level={typed_logger.level_name}",
            f"handlers={[type(h).__name__ for h in typed_logger.handlers]}",
        )
        return typed_logger
