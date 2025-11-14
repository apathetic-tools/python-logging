"""TestTrace functionality for Apathetic Logging."""

from __future__ import annotations

import builtins
import importlib
import sys
from collections.abc import Callable
from typing import Any

from .constants import (
    ApatheticLogging_Priv_Constants,  # pyright: ignore[reportPrivateUsage]
)


# Lazy, safe import — avoids patched time modules
#   in environments like pytest or eventlet
_real_time = importlib.import_module("time")


class ApatheticLogging_Priv_TestTrace:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the TEST_TRACE and make_test_trace static methods.

    This class contains the TEST_TRACE implementation as static methods.
    When mixed into ApatheticLogging, it provides ApatheticLogging.TEST_TRACE
    and ApatheticLogging.make_test_trace.
    """

    @staticmethod
    def make_test_trace(icon: str = "🧪") -> Callable[..., Any]:
        def local_trace(label: str, *args: Any) -> Any:
            return ApatheticLogging_Priv_TestTrace.TEST_TRACE(label, *args, icon=icon)

        return local_trace

    @staticmethod
    def TEST_TRACE(label: str, *args: Any, icon: str = "🧪") -> None:  # noqa: N802
        """Emit a synchronized, flush-safe diagnostic line.

        Args:
            label: Short identifier or context string.
            *args: Optional values to append.
            icon: Emoji prefix/suffix for easier visual scanning.

        """
        if not ApatheticLogging_Priv_Constants.TEST_TRACE_ENABLED:
            return

        ts = _real_time.monotonic()
        # builtins.print more reliable than sys.stdout.write + sys.stdout.flush
        builtins.print(
            f"{icon} [TEST TRACE {ts:.6f}] {label}",
            *args,
            file=sys.__stderr__,
            flush=True,
        )
