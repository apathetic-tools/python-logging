# tests/utils/level_validation.py
"""Utilities for validating test logging level values."""

from __future__ import annotations

import logging


def _get_safe_ranges() -> list[str]:
    """Calculate safe level ranges dynamically from constants.

    Returns a list of safe range descriptions for error messages.
    """
    # Import here to avoid circular dependencies and ensure runtime_swap has run
    import apathetic_logging as mod_alogs  # noqa: PLC0415

    _constants = mod_alogs.apathetic_logging

    # Collect all reserved level values in sorted order
    reserved_levels: list[tuple[int, str]] = [
        (logging.DEBUG, "DEBUG"),
        (logging.INFO, "INFO"),
        (logging.WARNING, "WARNING"),
        (logging.ERROR, "ERROR"),
        (logging.CRITICAL, "CRITICAL"),
        (_constants.TEST_LEVEL, "TEST"),
        (_constants.TRACE_LEVEL, "TRACE"),
        (_constants.DETAIL_LEVEL, "DETAIL"),
        (_constants.BRIEF_LEVEL, "BRIEF"),
        (_constants.MINIMAL_LEVEL, "MINIMAL"),  # deprecated: same value as BRIEF
        (_constants.SILENT_LEVEL, "SILENT"),
    ]
    reserved_levels.sort()

    # Calculate safe ranges between reserved levels
    safe_ranges: list[str] = []
    prev_level = 0
    min_safe_level = 1

    for level, _name in reserved_levels:
        # Range before first level (if > 1)
        if prev_level == 0 and level > min_safe_level:
            if level == min_safe_level + 1:
                safe_ranges.append(str(min_safe_level))
            else:
                safe_ranges.append(f"{min_safe_level}-{level - 1}")

        # Range between levels
        elif level - prev_level > 1:
            start = prev_level + 1
            end = level - 1
            if start == end:
                safe_ranges.append(str(start))
            else:
                safe_ranges.append(f"{start}-{end}")

        prev_level = level

    # Range after last level
    safe_ranges.append(f"{prev_level + 1}+")

    return safe_ranges


def validate_test_level(level: int) -> None:
    """Validate that a test level value doesn't conflict with existing levels.

    Raises ValueError if the level conflicts with:
    - Built-in logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Apathetic logging custom levels (TEST, TRACE, DETAIL, BRIEF, MINIMAL, SILENT)

    This forces test designers to explicitly choose safe level values,
    preventing accidental conflicts that could cause test failures.

    The function dynamically reads level values from the apathetic_logging
    constants module, so it automatically stays in sync with any changes.

    Args:
        level: The level value to validate

    Raises:
        ValueError: If the level conflicts with an existing level

    Example:
        >>> validate_test_level(26)  # Safe value between BRIEF and WARNING
        >>> validate_test_level(25)  # Raises ValueError (conflicts with BRIEF)
    """
    # Import here to avoid circular dependencies and ensure runtime_swap has run
    import apathetic_logging as mod_alogs  # noqa: PLC0415

    # Collect all reserved level values
    reserved_levels: dict[int, str] = {}

    # Built-in logging levels
    reserved_levels[logging.DEBUG] = "DEBUG"
    reserved_levels[logging.INFO] = "INFO"
    reserved_levels[logging.WARNING] = "WARNING"
    reserved_levels[logging.ERROR] = "ERROR"
    reserved_levels[logging.CRITICAL] = "CRITICAL"

    # Apathetic logging custom levels (read dynamically from constants)
    _constants = mod_alogs.apathetic_logging
    reserved_levels[_constants.TEST_LEVEL] = "TEST"
    reserved_levels[_constants.TRACE_LEVEL] = "TRACE"
    reserved_levels[_constants.DETAIL_LEVEL] = "DETAIL"
    reserved_levels[_constants.BRIEF_LEVEL] = "BRIEF"
    reserved_levels[_constants.MINIMAL_LEVEL] = "MINIMAL"  # deprecated
    reserved_levels[_constants.SILENT_LEVEL] = "SILENT"

    # Check for conflict
    if level in reserved_levels:
        conflicting_name = reserved_levels[level]
        safe_ranges = _get_safe_ranges()
        ranges_str = ", ".join(safe_ranges)
        msg = (
            f"Test level value {level} conflicts with existing level "
            f"{conflicting_name}. Choose a different value. "
            f"Safe ranges: {ranges_str}"
        )
        raise ValueError(msg)
