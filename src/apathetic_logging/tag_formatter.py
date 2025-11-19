# src/apathetic_logging/tag_formatter.py
"""TagFormatter class for Apathetic Logging."""

from __future__ import annotations

import logging

from .constants import (
    ApatheticLogging_Internal_Constants,
)


class ApatheticLogging_Internal_TagFormatter:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the TagFormatter nested class.

    This class contains the TagFormatter implementation as a nested class.
    When mixed into apathetic_logging, it provides apathetic_logging.TagFormatter.
    """

    class TagFormatter(logging.Formatter):
        def format(
            self,
            record: logging.LogRecord,
        ) -> str:
            _constants = ApatheticLogging_Internal_Constants
            tag_color, tag_text = _constants.TAG_STYLES.get(record.levelname, ("", ""))
            msg = super().format(record)
            if tag_text:
                if getattr(record, "enable_color", False) and tag_color:
                    prefix = f"{tag_color}{tag_text}{_constants.ANSIColors.RESET}"
                else:
                    prefix = tag_text
                return f"{prefix} {msg}"
            return msg
