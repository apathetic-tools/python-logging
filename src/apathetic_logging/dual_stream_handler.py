# src/apathetic_logging/dual_stream_handler.py
"""DualStreamHandler class for Apathetic Logging."""

from __future__ import annotations

import logging
import sys


class ApatheticLogging_Priv_DualStreamHandler:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the DualStreamHandler nested class.

    This class contains the DualStreamHandler implementation as a nested class.
    When mixed into apathetic_logging, it provides apathetic_logging.DualStreamHandler.
    """

    class DualStreamHandler(logging.StreamHandler):  # type: ignore[type-arg]
        """Send info/debug/trace to stdout, everything else to stderr.

        When logger level is TEST, TRACE/DEBUG/TEST messages bypass capture
        by writing to sys.__stderr__ instead of sys.stderr.
        This allows debugging tests without breaking output assertions while
        still being capturable by subprocess.run(capture_output=True).
        """

        enable_color: bool = False

        def __init__(self) -> None:
            # default to stdout, overridden per record in emit()
            super().__init__()  # pyright: ignore[reportUnknownMemberType]

        def emit(self, record: logging.LogRecord) -> None:
            level = record.levelno

            # Check if logger is in TEST mode (bypass capture for verbose levels)
            logger_name = record.name
            logger_instance = logging.getLogger(logger_name)
            # Import here to avoid circular dependency
            from .constants import (  # noqa: PLC0415
                ApatheticLogging_Priv_Constants,  # pyright: ignore[reportPrivateUsage]
            )

            # Use duck typing to check if this is our Logger class
            # (has test() method) to avoid circular dependency
            has_test_method = hasattr(logger_instance, "test") and callable(
                getattr(logger_instance, "test", None)
            )
            is_test_mode = (
                has_test_method
                and logger_instance.level == ApatheticLogging_Priv_Constants.TEST_LEVEL
            )

            # Determine target stream
            if level >= logging.WARNING:
                # Warnings and errors always go to stderr (normal behavior)
                # This ensures they still break tests as expected
                # Even in TEST mode, warnings/errors use normal stderr
                self.stream = sys.stderr
            # TRACE, DEBUG, TEST, INFO go to stdout
            # If in TEST mode, bypass capture for verbose levels (TEST/TRACE/DEBUG)
            elif is_test_mode and level < logging.INFO:
                # Use bypass stream for TEST/TRACE/DEBUG in test mode
                # Use __stderr__ so they bypass pytest capsys but are still
                # capturable by subprocess.run(capture_output=True)
                self.stream = sys.__stderr__
            else:
                # Normal behavior: use regular stdout
                self.stream = sys.stdout

            # used by TagFormatter
            record.enable_color = getattr(self, "enable_color", False)

            super().emit(record)
