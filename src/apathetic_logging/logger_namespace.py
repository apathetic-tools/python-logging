# src/apathetic_logging/logger_namespace.py
"""Logger namespace mixin that composes core Logger with snake_case mixins.

See https://docs.python.org/3/library/logging.html#logging.Logger for the
complete list of standard library Logger methods that are extended by this class.

Docstrings are adapted from the standard library logging.Logger documentation
licensed under the Python Software Foundation License Version 2.
"""

from __future__ import annotations

from .logger import (
    ApatheticLogging_Internal_LoggerCore,
)
from .logger_lib_snake import (
    ApatheticLogging_Internal_LibLoggerSnakeCase,
)
from .logger_std_snake import (
    ApatheticLogging_Internal_StdLoggerSnakeCase,
)


class ApatheticLogging_Internal_Logger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the Logger nested class.

    This class contains the Logger implementation as a nested class, composed from
    the core Logger implementation and snake_case convenience mixins.

    When mixed into apathetic_logging, it provides apathetic_logging.Logger.
    """

    class Logger(
        ApatheticLogging_Internal_LoggerCore,
        ApatheticLogging_Internal_LibLoggerSnakeCase,  # keep second last
        ApatheticLogging_Internal_StdLoggerSnakeCase,  # keep last
    ):
        """Logger for all Apathetic tools.

        This Logger class is composed from:
        - Core Logger implementation
          (ApatheticLogging_Internal_LoggerCore, which inherits from logging.Logger)
        - Library snake_case mixins
          (ApatheticLogging_Internal_LibLoggerSnakeCase)
        - Standard library snake_case mixins
          (ApatheticLogging_Internal_StdLoggerSnakeCase)
        """
