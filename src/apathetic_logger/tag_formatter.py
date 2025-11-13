"""TagFormatter class for Apathetic Logger."""

from __future__ import annotations

import logging
import sys
from typing import Any


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


def _get_namespace() -> Any:
    """Get the ApatheticLogger namespace at runtime."""
    return _get_namespace_module().ApatheticLogger


class _ApatheticLogger_TagFormatter:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the TagFormatter nested class.

    This class contains the TagFormatter implementation as a nested class.
    When mixed into ApatheticLogger, it provides ApatheticLogger.TagFormatter.
    """

    class TagFormatter(logging.Formatter):
        def format(
            self,
            record: logging.LogRecord,
        ) -> str:
            ns = _get_namespace()
            tag_color, tag_text = ns.TAG_STYLES.get(record.levelname, ("", ""))
            msg = super().format(record)
            if tag_text:
                if getattr(record, "enable_color", False) and tag_color:
                    prefix = f"{tag_color}{tag_text}{ns.ANSIColors.RESET}"
                else:
                    prefix = tag_text
                return f"{prefix} {msg}"
            return msg
