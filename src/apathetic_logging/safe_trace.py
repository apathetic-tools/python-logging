# src/apathetic_logging/safe_trace.py
"""Safe trace functionality for Apathetic Logging."""

from __future__ import annotations

import builtins
import importlib
import sys
from collections.abc import Callable
from typing import Any

from .constants import (
    ApatheticLogging_Internal_Constants,
)


# Lazy, safe import — avoids patched time modules
#   in environments like pytest or eventlet
_real_time = importlib.import_module("time")


class ApatheticLogging_Internal_SafeTrace:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the safe_trace and make_safe_trace static methods.

    This class contains the safe_trace implementation as static methods.
    When mixed into apathetic_logging, it provides apathetic_logging.safe_trace
    and apathetic_logging.make_safe_trace.
    """

    @staticmethod
    def make_safe_trace(icon: str = "🧪") -> Callable[..., Any]:
        _safe_trace = ApatheticLogging_Internal_SafeTrace

        def local_trace(label: str, *args: Any) -> Any:
            return _safe_trace.safe_trace(label, *args, icon=icon)

        return local_trace

    @staticmethod
    def safe_trace(label: str, *args: Any, icon: str = "🧪") -> None:
        """Emit a synchronized, flush-safe diagnostic line.

        Args:
            label: Short identifier or context string.
            *args: Optional values to append.
            icon: Emoji prefix/suffix for easier visual scanning.

        """
        _constants = ApatheticLogging_Internal_Constants
        if not _constants.SAFE_TRACE_ENABLED:
            return

        ts = _real_time.monotonic()
        # builtins.print more reliable than sys.stdout.write + sys.stdout.flush
        builtins.print(
            f"{icon} [SAFE TRACE {ts:.6f}] {label}",
            *args,
            file=sys.__stderr__,
            flush=True,
        )
