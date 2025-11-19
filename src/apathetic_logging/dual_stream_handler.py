# src/apathetic_logging/dual_stream_handler.py
"""DualStreamHandler class for Apathetic Logging."""

from __future__ import annotations

import logging
import sys


class ApatheticLogging_Internal_DualStreamHandler:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the DualStreamHandler nested class.

    This class contains the DualStreamHandler implementation as a nested class.
    When mixed into apathetic_logging, it provides apathetic_logging.DualStreamHandler.
    """

    class DualStreamHandler(logging.StreamHandler):  # type: ignore[type-arg]
        """Send info to stdout, everything else to stderr.

        INFO, MINIMAL, and DETAIL go to stdout (normal program output).
        TRACE, DEBUG, WARNING, ERROR, and CRITICAL go to stderr
        (diagnostic/error output).
        When logger level is TEST, TEST/TRACE/DEBUG messages bypass capture
        by writing to sys.__stderr__ instead of sys.stderr. This allows
        debugging tests without breaking output assertions while still being
        capturable by subprocess.run(capture_output=True).
        WARNING, ERROR, and CRITICAL always use normal stderr, even in TEST mode.
        """

        enable_color: bool = False

        def __init__(self) -> None:
            # default to stdout, overridden per record in emit()
            super().__init__()  # pyright: ignore[reportUnknownMemberType]

        def emit(self, record: logging.LogRecord) -> None:
            # Import here to avoid circular dependency
            from .constants import (  # noqa: PLC0415
                ApatheticLogging_Internal_Constants,
            )

            _constants = ApatheticLogging_Internal_Constants
            level = record.levelno

            # Check if logger is in TEST mode (bypass capture for verbose levels)
            logger_name = record.name
            logger_instance = logging.getLogger(logger_name)

            # Use duck typing to check if this is our Logger class
            # (has test() method) to avoid circular dependency
            has_test_method = hasattr(logger_instance, "test") and callable(
                getattr(logger_instance, "test", None)
            )
            is_test_mode = has_test_method and logger_instance.level == (
                _constants.TEST_LEVEL
            )

            # Determine target stream
            if level >= logging.WARNING:
                # WARNING, ERROR, CRITICAL → stderr (always, even in TEST mode)
                # This ensures they still break tests as expected
                self.stream = sys.stderr
            elif level <= logging.DEBUG:
                # TEST, TRACE, DEBUG → stderr (normal) or __stderr__ (TEST mode bypass)
                # Use __stderr__ so they bypass pytest capsys but are still
                # capturable by subprocess.run(capture_output=True)
                if is_test_mode:
                    self.stream = sys.__stderr__
                else:
                    self.stream = sys.stderr
            elif level == _constants.DETAIL_LEVEL:
                # DETAIL → stdout (normal program output, like INFO)
                self.stream = sys.stdout
            elif level == _constants.MINIMAL_LEVEL:
                # MINIMAL → stdout (normal program output)
                self.stream = sys.stdout
            else:
                # INFO → stdout (normal program output)
                self.stream = sys.stdout

            # used by TagFormatter
            record.enable_color = getattr(self, "enable_color", False)

            super().emit(record)
