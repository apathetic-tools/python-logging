"""DualStreamHandler class for Apathetic Logger."""

from __future__ import annotations

import logging
import sys


class _ApatheticLogger_DualStreamHandler:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the DualStreamHandler nested class.

    This class contains the DualStreamHandler implementation as a nested class.
    When mixed into ApatheticLogger, it provides ApatheticLogger.DualStreamHandler.
    """

    class DualStreamHandler(logging.StreamHandler):  # type: ignore[type-arg]
        """Send info/debug/trace to stdout, everything else to stderr."""

        enable_color: bool = False

        def __init__(self) -> None:
            # default to stdout, overridden per record in emit()
            super().__init__()  # pyright: ignore[reportUnknownMemberType]

        def emit(self, record: logging.LogRecord) -> None:
            level = record.levelno
            if level >= logging.WARNING:
                self.stream = sys.stderr
            else:
                self.stream = sys.stdout

            # used by TagFormatter
            record.enable_color = getattr(self, "enable_color", False)

            super().emit(record)
