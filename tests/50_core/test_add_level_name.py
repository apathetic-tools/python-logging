# tests/50_core/test_add_level_name.py
"""Tests for addLevelName() and level validation features."""

import logging
from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


# ---------------------------------------------------------------------------
# Tests for validateLevel()
# ---------------------------------------------------------------------------


def test_validate_level_valid_level() -> None:
    """validateLevel() should pass for valid levels (> 0)."""
    # Should not raise for valid levels
    mod_alogs.Logger.validateLevel(1, level_name="TEST")
    mod_alogs.Logger.validateLevel(5, level_name="TRACE")
    mod_alogs.Logger.validateLevel(10, level_name="DEBUG")
    mod_alogs.Logger.validateLevel(100, level_name="CUSTOM")


def test_validate_level_zero_raises() -> None:
    """validateLevel() should raise ValueError for level 0."""
    with pytest.raises(ValueError, match=r"setLevel\(0\).*NOTSET"):
        mod_alogs.Logger.validateLevel(0, level_name="TEST")


def test_validate_level_zero_with_allow_inherit_passes() -> None:
    """validateLevel() should pass for level 0 with allow_inherit=True."""
    # Should not raise when allow_inherit=True
    mod_alogs.Logger.validateLevel(0, level_name="TEST", allow_inherit=True)


def test_validate_level_negative_raises() -> None:
    """validateLevel() should raise ValueError for negative levels."""
    with pytest.raises(ValueError, match=r"<= 0"):
        mod_alogs.Logger.validateLevel(-5, level_name="NEGATIVE")


def test_validate_level_auto_detects_name() -> None:
    """validateLevel() should auto-detect level name if None."""
    with pytest.raises(ValueError, match=r"setLevel\(0\).*NOTSET"):
        mod_alogs.Logger.validateLevel(0, level_name=None)


# ---------------------------------------------------------------------------
# Tests for addLevelName()
# ---------------------------------------------------------------------------


def test_add_level_name_success() -> None:
    """addLevelName() should successfully register a custom level."""
    # Use a unique level value to avoid conflicts
    level_value = 25
    level_name = "CUSTOM_TEST"
    apathetic_level_name = f"{level_name}_LEVEL"

    # Clean up if it exists
    if hasattr(logging, level_name):
        delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)

    mod_alogs.Logger.addLevelName(level_value, level_name)

    # Verify level name is registered
    assert logging.getLevelName(level_value) == level_name

    # Verify convenience attributes are set in both namespaces
    assert getattr(logging, level_name) == level_value
    assert getattr(mod_alogs.apathetic_logging, apathetic_level_name) == level_value

    # Clean up
    delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)


def test_add_level_name_sets_convenience_attribute() -> None:
    """addLevelName() should set logging.<LEVEL_NAME> attribute."""
    level_value = 30
    level_name = "CONVENIENCE_TEST"

    # Save original level name mapping (30 is WARNING)
    original_level_name = logging.getLevelName(level_value)

    # Clean up if it exists
    if hasattr(logging, level_name):
        delattr(logging, level_name)

    mod_alogs.Logger.addLevelName(level_value, level_name)

    # Verify attribute exists and has correct value
    assert hasattr(logging, level_name)
    assert getattr(logging, level_name) == level_value

    # Can use it like built-in levels
    logger = logging.getLogger("test")
    logger.setLevel(getattr(logging, level_name))
    assert logger.level == level_value

    # Clean up: restore original level name mapping
    delattr(logging, level_name)
    # Restore original level name in _levelToName dict
    if original_level_name and original_level_name != f"Level {level_value}":
        logging.addLevelName(level_value, original_level_name)


def test_add_level_name_zero_raises() -> None:
    """addLevelName() should raise ValueError for level 0."""
    with pytest.raises(ValueError, match=r"setLevel\(0\).*NOTSET"):
        mod_alogs.Logger.addLevelName(0, "ZERO_LEVEL")


def test_add_level_name_negative_raises() -> None:
    """addLevelName() should raise ValueError for negative levels."""
    with pytest.raises(ValueError, match=r"<= 0.*PEP 282"):
        mod_alogs.Logger.addLevelName(-10, "NEGATIVE_LEVEL")


def test_add_level_name_idempotent() -> None:
    """addLevelName() should be idempotent (can call multiple times)."""
    level_value = 35
    level_name = "IDEMPOTENT_TEST"
    apathetic_level_name = f"{level_name}_LEVEL"

    # Clean up if it exists
    if hasattr(logging, level_name):
        delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)

    # First call
    mod_alogs.Logger.addLevelName(level_value, level_name)
    assert getattr(logging, level_name) == level_value
    assert getattr(mod_alogs.apathetic_logging, apathetic_level_name) == level_value

    # Second call with same value (should not raise)
    mod_alogs.Logger.addLevelName(level_value, level_name)
    assert getattr(logging, level_name) == level_value
    assert getattr(mod_alogs.apathetic_logging, apathetic_level_name) == level_value

    # Clean up
    delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)


def test_add_level_name_rejects_invalid_existing_attribute_type() -> None:
    """addLevelName() should reject if attribute exists with non-integer value."""
    level_name = "INVALID_TYPE_TEST"

    # Set invalid attribute
    setattr(logging, level_name, "not_an_int")

    try:
        with pytest.raises(
            ValueError,
            match=r"non-integer value.*Level attributes must be integers",
        ):
            mod_alogs.Logger.addLevelName(40, level_name)
    finally:
        # Clean up
        if hasattr(logging, level_name):
            delattr(logging, level_name)


def test_add_level_name_rejects_invalid_existing_attribute_value() -> None:
    """addLevelName() should reject if attribute exists with <= 0 value."""
    level_name = "INVALID_VALUE_TEST"

    # Set invalid attribute (zero)
    setattr(logging, level_name, 0)

    try:
        with pytest.raises(
            ValueError,
            match=r"setLevel\(0\).*NOTSET",
        ):
            mod_alogs.Logger.addLevelName(45, level_name)
    finally:
        # Clean up
        if hasattr(logging, level_name):
            delattr(logging, level_name)


def test_add_level_name_rejects_different_existing_value() -> None:
    """addLevelName() should reject if attribute exists with different value."""
    level_name = "DIFFERENT_VALUE_TEST"
    existing_value = 50
    new_value = 55

    # Set existing attribute with different value
    setattr(logging, level_name, existing_value)

    try:
        with pytest.raises(
            ValueError,
            match=r"different value.*must match the level value",
        ):
            mod_alogs.Logger.addLevelName(new_value, level_name)
    finally:
        # Clean up
        if hasattr(logging, level_name):
            delattr(logging, level_name)


def test_add_level_name_rejects_invalid_apathetic_logging_attribute_type() -> None:
    """addLevelName() should reject if apathetic_logging attribute exists
    with non-integer value."""
    level_name = "INVALID_APATHETIC_TYPE_TEST"
    apathetic_level_name = f"{level_name}_LEVEL"

    # Set invalid attribute on apathetic_logging namespace class
    setattr(mod_alogs.apathetic_logging, apathetic_level_name, "not_an_int")

    try:
        with pytest.raises(
            ValueError,
            match=r"non-integer value.*Level attributes must be integers",
        ):
            mod_alogs.Logger.addLevelName(70, level_name)
    finally:
        # Clean up
        if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
            delattr(mod_alogs.apathetic_logging, apathetic_level_name)


def test_add_level_name_rejects_invalid_apathetic_logging_attribute_value() -> None:
    """addLevelName() should reject if apathetic_logging attribute exists
    with <= 0 value."""
    level_name = "INVALID_APATHETIC_VALUE_TEST"
    apathetic_level_name = f"{level_name}_LEVEL"

    # Set invalid attribute (zero) on apathetic_logging namespace class
    setattr(mod_alogs.apathetic_logging, apathetic_level_name, 0)

    try:
        with pytest.raises(
            ValueError,
            match=r"setLevel\(0\).*NOTSET",
        ):
            mod_alogs.Logger.addLevelName(75, level_name)
    finally:
        # Clean up
        if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
            delattr(mod_alogs.apathetic_logging, apathetic_level_name)


def test_add_level_name_rejects_different_existing_apathetic_logging_value() -> None:
    """addLevelName() should reject if apathetic_logging attribute exists
    with different value."""
    level_name = "DIFFERENT_APATHETIC_VALUE_TEST"
    apathetic_level_name = f"{level_name}_LEVEL"
    existing_value = 80
    new_value = 85

    # Set existing attribute with different value on apathetic_logging namespace class
    setattr(mod_alogs.apathetic_logging, apathetic_level_name, existing_value)

    try:
        with pytest.raises(
            ValueError,
            match=r"different value.*must match the level value",
        ):
            mod_alogs.Logger.addLevelName(new_value, level_name)
    finally:
        # Clean up
        if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
            delattr(mod_alogs.apathetic_logging, apathetic_level_name)


def test_add_level_name_works_with_extend_logging_module() -> None:
    """addLevelName() should work correctly when used by extendLoggingModule()."""
    # Reset extension flag
    mod_alogs.Logger._logging_module_extended = False  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001

    # Call extendLoggingModule (uses addLevelName internally)
    result = mod_alogs.Logger.extendLoggingModule()

    assert result is True

    # Verify levels are registered
    assert logging.getLevelName(mod_alogs.TEST_LEVEL) == "TEST"
    assert logging.getLevelName(mod_alogs.TRACE_LEVEL) == "TRACE"
    assert logging.getLevelName(mod_alogs.SILENT_LEVEL) == "SILENT"

    # Verify convenience attributes are set in logging namespace
    assert logging.TEST == mod_alogs.TEST_LEVEL  # type: ignore[attr-defined]
    assert logging.TRACE == mod_alogs.TRACE_LEVEL  # type: ignore[attr-defined]
    assert logging.SILENT == mod_alogs.SILENT_LEVEL  # type: ignore[attr-defined]

    # Verify convenience attributes are also set in apathetic_logging namespace
    # with _LEVEL suffix (these are the same as the constants, so they should match)
    assert mod_alogs.apathetic_logging.TEST_LEVEL == mod_alogs.TEST_LEVEL
    assert mod_alogs.apathetic_logging.TRACE_LEVEL == mod_alogs.TRACE_LEVEL
    assert mod_alogs.apathetic_logging.SILENT_LEVEL == mod_alogs.SILENT_LEVEL


def test_add_level_name_matches_builtin_level_pattern() -> None:
    """addLevelName() should create attributes matching built-in level pattern."""
    level_value = 60
    level_name = "PATTERN_TEST"

    # Clean up if it exists
    if hasattr(logging, level_name):
        delattr(logging, level_name)

    mod_alogs.Logger.addLevelName(level_value, level_name)

    # Verify it matches built-in pattern
    assert hasattr(logging, "DEBUG")  # built-in
    assert hasattr(logging, level_name)  # custom (same pattern)

    # Both should be integers
    assert isinstance(logging.DEBUG, int)
    assert isinstance(getattr(logging, level_name), int)

    # Both should be usable in setLevel
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    assert logger.level == logging.DEBUG

    logger.setLevel(getattr(logging, level_name))
    assert logger.level == level_value

    # Clean up
    delattr(logging, level_name)


def test_add_level_name_sets_apathetic_logging_attribute() -> None:
    """addLevelName() should set apathetic_logging.<LEVEL_NAME>_LEVEL attribute."""
    level_value = 65
    level_name = "APATHETIC_NAMESPACE_TEST"
    apathetic_level_name = f"{level_name}_LEVEL"

    # Clean up if it exists
    if hasattr(logging, level_name):
        delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)

    mod_alogs.Logger.addLevelName(level_value, level_name)

    # Verify attribute exists in both namespaces
    assert hasattr(logging, level_name)
    assert getattr(logging, level_name) == level_value
    assert hasattr(mod_alogs.apathetic_logging, apathetic_level_name)
    assert getattr(mod_alogs.apathetic_logging, apathetic_level_name) == level_value

    # Both should be usable in setLevel
    logger = mod_alogs.getLogger("test")
    logger.setLevel(getattr(logging, level_name))
    assert logger.level == level_value

    logger.setLevel(getattr(mod_alogs.apathetic_logging, apathetic_level_name))
    assert logger.level == level_value

    # Clean up
    delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)


def test_add_level_name_idempotent_with_existing_constant() -> None:
    """addLevelName() should be idempotent when constant already exists."""
    # TRACE_LEVEL already exists as a constant, calling addLevelName should work
    # and set it to the same value (idempotent)
    mod_alogs.Logger.extendLoggingModule()

    # Verify TRACE_LEVEL constant exists
    assert hasattr(mod_alogs.apathetic_logging, "TRACE_LEVEL")
    original_value = mod_alogs.apathetic_logging.TRACE_LEVEL

    # Call addLevelName again (should be idempotent)
    mod_alogs.Logger.addLevelName(mod_alogs.TRACE_LEVEL, "TRACE")

    # Value should remain the same
    assert original_value == mod_alogs.apathetic_logging.TRACE_LEVEL
    assert original_value == logging.TRACE  # type: ignore[attr-defined]


def test_add_level_name_both_namespaces_independent() -> None:
    """addLevelName() should set attributes in both namespaces independently."""
    level_value = 90
    level_name = "INDEPENDENT_TEST"
    apathetic_level_name = f"{level_name}_LEVEL"

    # Clean up if it exists
    if hasattr(logging, level_name):
        delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)

    mod_alogs.Logger.addLevelName(level_value, level_name)

    # Verify both namespaces have the correct values
    assert logging.getLevelName(level_value) == level_name
    assert getattr(logging, level_name) == level_value
    assert getattr(mod_alogs.apathetic_logging, apathetic_level_name) == level_value

    # Verify they can be used independently
    logger1 = logging.getLogger("test1")
    logger1.setLevel(getattr(logging, level_name))
    assert logger1.level == level_value

    logger2 = mod_alogs.getLogger("test2")
    logger2.setLevel(getattr(mod_alogs.apathetic_logging, apathetic_level_name))
    assert logger2.level == level_value

    # Clean up
    delattr(logging, level_name)
    if hasattr(mod_alogs.apathetic_logging, apathetic_level_name):
        delattr(mod_alogs.apathetic_logging, apathetic_level_name)


# ---------------------------------------------------------------------------
# Tests for setLevel() validation
# ---------------------------------------------------------------------------


def test_set_level_validates_custom_levels(direct_logger: Logger) -> None:
    """setLevel() should validate custom levels are not <= 0."""
    # Valid custom levels should work
    direct_logger.setLevel(mod_alogs.TEST_LEVEL)
    assert direct_logger.level == mod_alogs.TEST_LEVEL

    direct_logger.setLevel(mod_alogs.TRACE_LEVEL)
    assert direct_logger.level == mod_alogs.TRACE_LEVEL

    direct_logger.setLevel(mod_alogs.SILENT_LEVEL)
    assert direct_logger.level == mod_alogs.SILENT_LEVEL


def test_set_level_allows_builtin_levels(direct_logger: Logger) -> None:
    """setLevel() should allow built-in levels (all are > 0)."""
    # Built-in levels should work (they're all > 0, so pass validation)
    direct_logger.setLevel(logging.DEBUG)
    assert direct_logger.level == logging.DEBUG

    direct_logger.setLevel(logging.INFO)
    assert direct_logger.level == logging.INFO

    direct_logger.setLevel(logging.WARNING)
    assert direct_logger.level == logging.WARNING


def test_set_level_rejects_any_level_zero_or_negative(
    direct_logger: Logger,
) -> None:
    """setLevel() should reject ANY level <= 0, not just our custom levels."""
    # Should reject level 0 (NOTSET) - new error message format
    with pytest.raises(ValueError, match=r"setLevel\(0\).*allow_inherit=True"):
        direct_logger.setLevel(0)

    # Should reject negative levels
    with pytest.raises(ValueError, match=r"<= 0.*PEP 282"):
        direct_logger.setLevel(-10)

    # Should reject user's custom level if <= 0
    logging.addLevelName(-10, "USER_BAD")
    with pytest.raises(ValueError, match=r"<= 0.*PEP 282"):
        direct_logger.setLevel(-10)


def test_set_level_validates_custom_level_string(
    direct_logger: Logger,
) -> None:
    """setLevel() should validate custom levels when passed as string."""
    # Valid custom level strings should work
    direct_logger.setLevel("TEST")
    assert direct_logger.level == mod_alogs.TEST_LEVEL

    direct_logger.setLevel("TRACE")
    assert direct_logger.level == mod_alogs.TRACE_LEVEL

    direct_logger.setLevel("SILENT")
    assert direct_logger.level == mod_alogs.SILENT_LEVEL
