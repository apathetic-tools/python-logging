# tests/50_core/test_logger_level_api.py
"""Tests for Logger level-related properties and methods.

Tests the new level API:
- Properties: level, levelName, effectiveLevel, effectiveLevelName
- Methods: getLevel(), getLevelName(), getEffectiveLevel(), getEffectiveLevelName()
- Snake_case wrappers: level_name, effective_level, effective_level_name,
  get_level(), get_level_name(), get_effective_level_name()
"""

import logging
from typing import TYPE_CHECKING

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


# ---------------------------------------------------------------------------
# Tests for Properties (CamelCase)
# ---------------------------------------------------------------------------


def test_level_property_explicit(direct_logger: Logger) -> None:
    """Level property should return explicit level set on logger."""
    direct_logger.setLevel("INFO")
    assert direct_logger.level == logging.INFO


def test_level_name_property_explicit(direct_logger: Logger) -> None:
    """LevelName property should return explicit level name."""
    direct_logger.setLevel("DEBUG")
    assert direct_logger.levelName == "DEBUG"
    assert direct_logger.level == logging.DEBUG


def test_effective_level_property(direct_logger: Logger) -> None:
    """EffectiveLevel property should return effective level."""
    direct_logger.setLevel("WARNING")
    assert direct_logger.effectiveLevel == logging.WARNING
    assert direct_logger.effectiveLevel == direct_logger.getEffectiveLevel()


def test_effective_level_name_property(direct_logger: Logger) -> None:
    """EffectiveLevelName property should return effective level name."""
    direct_logger.setLevel("ERROR")
    assert direct_logger.effectiveLevelName == "ERROR"
    assert direct_logger.effectiveLevelName == direct_logger.getEffectiveLevelName()


def test_explicit_vs_effective_with_inheritance() -> None:
    """Test difference between explicit and effective with inheritance."""
    parent = mod_alogs.getLogger("test_parent_inherit")
    parent.setLevel("WARNING")

    child = mod_alogs.getLogger("test_parent_inherit.child")

    # Explicit level (NOTSET for child, unless default is set)
    # Note: child.level might be NOTSET or a default level depending on config
    explicit_level = child.level
    explicit_level_name = child.levelName

    # Effective level (inherited from parent if child has NOTSET)
    # If child has a default level set, effective will be that
    effective_level = child.effectiveLevel
    effective_level_name = child.effectiveLevelName

    # Key assertion: effective should be WARNING (from parent) if child is NOTSET
    # OR effective should match explicit if child has a level set
    if explicit_level == logging.NOTSET:
        # Child inherits from parent
        assert effective_level == logging.WARNING
        assert effective_level_name == "WARNING"
    else:
        # Child has explicit level set, effective matches explicit
        assert effective_level == explicit_level
        assert effective_level_name == explicit_level_name


def test_explicit_vs_effective_when_set() -> None:
    """Test explicit and effective are same when level is explicitly set."""
    logger = mod_alogs.getLogger("test_explicit")
    logger.setLevel("INFO")

    # When explicitly set, explicit and effective should match
    assert logger.level == logging.INFO
    assert logger.levelName == "INFO"
    assert logger.effectiveLevel == logging.INFO
    assert logger.effectiveLevelName == "INFO"


# ---------------------------------------------------------------------------
# Tests for Methods (CamelCase)
# ---------------------------------------------------------------------------


def test_get_level_method(direct_logger: Logger) -> None:
    """getLevel() should return explicit level."""
    direct_logger.setLevel("DEBUG")
    assert direct_logger.getLevel() == logging.DEBUG
    assert direct_logger.getLevel() == direct_logger.level


def test_get_level_name_method(direct_logger: Logger) -> None:
    """getLevelName() should return explicit level name."""
    direct_logger.setLevel("TRACE")
    assert direct_logger.getLevelName() == "TRACE"
    assert direct_logger.getLevelName() == direct_logger.levelName


def test_get_effective_level_method(direct_logger: Logger) -> None:
    """getEffectiveLevel() should return effective level."""
    direct_logger.setLevel("ERROR")
    assert direct_logger.getEffectiveLevel() == logging.ERROR
    assert direct_logger.getEffectiveLevel() == direct_logger.effectiveLevel


def test_get_effective_level_name_method(direct_logger: Logger) -> None:
    """getEffectiveLevelName() should return effective level name."""
    direct_logger.setLevel("CRITICAL")
    assert direct_logger.getEffectiveLevelName() == "CRITICAL"
    assert direct_logger.getEffectiveLevelName() == direct_logger.effectiveLevelName


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------


def test_all_apis_consistent(direct_logger: Logger) -> None:
    """All APIs should return consistent values."""
    direct_logger.setLevel("SILENT")

    # Properties
    level_prop = direct_logger.level
    level_name_prop = direct_logger.levelName
    effective_level_prop = direct_logger.effectiveLevel
    effective_level_name_prop = direct_logger.effectiveLevelName

    # Methods
    level_method = direct_logger.getLevel()
    level_name_method = direct_logger.getLevelName()
    effective_level_method = direct_logger.getEffectiveLevel()
    effective_level_name_method = direct_logger.getEffectiveLevelName()

    # Verify consistency
    assert level_prop == level_method
    assert level_name_prop == level_name_method
    assert effective_level_prop == effective_level_method
    assert effective_level_name_prop == effective_level_name_method
