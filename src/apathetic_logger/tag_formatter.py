"""TagFormatter class for Apathetic Logger."""

from __future__ import annotations

import logging

from .constants import (
    _ApatheticLogger_Constants,  # pyright: ignore[reportPrivateUsage]
)


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
            tag_color, tag_text = _ApatheticLogger_Constants.TAG_STYLES.get(
                record.levelname, ("", "")
            )
            msg = super().format(record)
            if tag_text:
                if getattr(record, "enable_color", False) and tag_color:
                    prefix = (
                        f"{tag_color}{tag_text}"
                        f"{_ApatheticLogger_Constants.ANSIColors.RESET}"
                    )
                else:
                    prefix = tag_text
                return f"{prefix} {msg}"
            return msg
