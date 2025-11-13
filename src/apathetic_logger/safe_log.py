"""SafeLog functionality for Apathetic Logger."""

from __future__ import annotations

import sys
from contextlib import suppress
from typing import TextIO, cast


class _ApatheticLogger_SafeLog:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the safe_log static method.

    This class contains the safe_log implementation as a static method.
    When mixed into ApatheticLogger, it provides ApatheticLogger.safe_log.
    """

    @staticmethod
    def safe_log(msg: str) -> None:
        """Emergency logger that never fails."""
        stream = cast("TextIO", sys.__stderr__)
        try:
            print(msg, file=stream)
        except Exception:  # noqa: BLE001
            # As final guardrail — never crash during crash reporting
            with suppress(Exception):
                stream.write(f"[INTERNAL] {msg}\n")
