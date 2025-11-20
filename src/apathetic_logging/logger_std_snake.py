# src/apathetic_logging/logger_std_snake.py
"""Snake case convenience methods for standard logging.Logger.

See https://docs.python.org/3/library/logging.html#logging.Logger for the
complete list of standard library Logger methods that are wrapped by this class.

Docstrings are adapted from the standard library logging.Logger documentation
licensed under the Python Software Foundation License Version 2.
"""

from __future__ import annotations

import logging
from types import FrameType
from typing import Any


class ApatheticLogging_Internal_StdLoggerSnakeCase:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides snake_case convenience methods for logging.Logger.

    This class contains snake_case wrapper methods for standard library
    `logging.Logger` methods that use camelCase naming. These wrappers provide
    a more Pythonic interface that follows PEP 8 naming conventions while
    maintaining full compatibility with the underlying logging.Logger methods.

    When mixed into Logger, it provides snake_case alternatives to standard
    Logger methods (e.g., `addHandler` -> `add_handler`, `removeHandler` ->
    `remove_handler`, `setLevel` -> `set_level`, `getEffectiveLevel` ->
    `get_effective_level`).
    """

    # --- Filter Management Methods ---

    def add_filter(
        self,
        filter: logging.Filter,  # noqa: A002
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Add the specified filter to this handler.

        Wrapper for logging.Logger.addFilter with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.addFilter
        """
        super().addFilter(filter, *args, **kwargs)  # type: ignore[misc]

    def remove_filter(
        self,
        filter: logging.Filter,  # noqa: A002
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Remove the specified filter from this handler.

        Wrapper for logging.Logger.removeFilter with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.removeFilter
        """
        super().removeFilter(filter, *args, **kwargs)  # type: ignore[misc]

    # --- Handler Management Methods ---

    def add_handler(self, hdlr: logging.Handler, *args: Any, **kwargs: Any) -> None:
        """Add the specified handler to this logger.

        Wrapper for logging.Logger.addHandler with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.addHandler
        """
        super().addHandler(hdlr, *args, **kwargs)  # type: ignore[misc]

    def remove_handler(self, hdlr: logging.Handler, *args: Any, **kwargs: Any) -> None:
        """Remove the specified handler from this logger.

        Wrapper for logging.Logger.removeHandler with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.removeHandler
        """
        super().removeHandler(hdlr, *args, **kwargs)  # type: ignore[misc]

    def call_handlers(
        self, record: logging.LogRecord, *args: Any, **kwargs: Any
    ) -> None:
        """Pass a record to all relevant handlers.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger with the "propagate" attribute set to zero is found - that
        will be the last logger whose handlers are called.

        Wrapper for logging.Logger.callHandlers with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.callHandlers
        """
        super().callHandlers(record, *args, **kwargs)  # type: ignore[misc]

    def has_handlers(self, *args: Any, **kwargs: Any) -> bool:
        """See if this logger has any handlers configured.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. Return True if a handler was found, else False.
        Stop searching up the hierarchy whenever a logger with the "propagate"
        attribute set to zero is found - that will be the last logger which
        is checked for the existence of handlers.

        Wrapper for logging.Logger.hasHandlers with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.hasHandlers
        """
        return super().hasHandlers(*args, **kwargs)  # type: ignore[misc,no-any-return]

    # --- Level Management Methods ---

    def set_level(self, level: int | str, *args: Any, **kwargs: Any) -> None:
        """Set the logging level of this logger.

        level must be an int or a str.

        Wrapper for logging.Logger.setLevel with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.setLevel
        """
        super().setLevel(level, *args, **kwargs)  # type: ignore[misc]

    def get_effective_level(self, *args: Any, **kwargs: Any) -> int:
        """Get the effective level for this logger.

        Loop through this logger and its parents in the logger hierarchy,
        looking for a non-zero logging level. Return the first one found.

        Wrapper for logging.Logger.getEffectiveLevel with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.getEffectiveLevel
        """
        return super().getEffectiveLevel(*args, **kwargs)  # type: ignore[misc,no-any-return]

    def is_enabled_for(self, level: int, *args: Any, **kwargs: Any) -> bool:
        """Is this logger enabled for level 'level'?

        Wrapper for logging.Logger.isEnabledFor with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.isEnabledFor
        """
        return super().isEnabledFor(level, *args, **kwargs)  # type: ignore[misc,no-any-return]

    # --- Logger Hierarchy Methods ---

    def get_child(self, suffix: str, *args: Any, **kwargs: Any) -> logging.Logger:
        """Get a logger which is a descendant to this one.

        This is a convenience method, such that

        logging.getLogger('abc').getChild('def.ghi')

        is the same as

        logging.getLogger('abc.def.ghi')

        It's useful, for example, when the parent logger is named using
        __name__ rather than a literal string.

        Wrapper for logging.Logger.getChild with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.getChild
        """
        return super().getChild(suffix, *args, **kwargs)  # type: ignore[misc,no-any-return]

    def get_children(self, *args: Any, **kwargs: Any) -> list[logging.Logger]:
        """Get all child loggers of this logger.

        Wrapper for logging.Logger.getChildren with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.getChildren
        """
        return super().getChildren(*args, **kwargs)  # type: ignore[misc,no-any-return]

    # --- Record Creation Methods ---

    def make_record(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: str,
        args: tuple[Any, ...],
        exc_info: Any,
        func: str | None = None,
        extra: dict[str, Any] | None = None,
        sinfo: str | None = None,
        *record_args: Any,
        **record_kwargs: Any,
    ) -> logging.LogRecord:
        """A factory method which can be overridden in subclasses to create
        specialized LogRecords.

        Wrapper for logging.Logger.makeRecord with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.makeRecord
        """
        return super().makeRecord(  # type: ignore[misc,no-any-return]
            name,
            level,
            fn,
            lno,
            msg,
            args,
            exc_info,
            func,
            extra,
            sinfo,
            *record_args,
            **record_kwargs,
        )

    # --- Utility Methods ---

    def find_caller(
        self,
        stack_info: bool = False,  # noqa: FBT001, FBT002
        stacklevel: int = 1,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[str, int, str, FrameType | None] | tuple[str, int, str]:
        """Find the stack frame of the caller.

        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.

        Wrapper for logging.Logger.findCaller with snake_case naming.

        https://docs.python.org/3.10/library/logging.html#logging.Logger.findCaller
        """
        return super().findCaller(stack_info, stacklevel, *args, **kwargs)  # type: ignore[misc,no-any-return]
