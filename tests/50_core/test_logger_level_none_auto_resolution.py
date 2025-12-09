# tests/50_core/test_logger_level_none_auto_resolution.py
"""Tests for level=None auto-resolution vs level=NOTSET behavior."""

from __future__ import annotations

import logging
import os

import apathetic_logging as mod_alogs


def test_level_none_auto_resolves() -> None:
    """Test that level=None auto-resolves via determineLogLevel()."""
    # --- setup ---
    # Set environment variable to control resolution
    original_env = os.environ.get("LOG_LEVEL")
    os.environ["LOG_LEVEL"] = "WARNING"

    # --- execute ---
    logger = mod_alogs.Logger("test_level_none", level=None)

    # --- verify ---
    # Should have auto-resolved to WARNING from env var
    assert logger.level == logging.WARNING
    assert logger.levelName == "WARNING"

    # --- cleanup ---
    if original_env is None:
        os.environ.pop("LOG_LEVEL", None)
    else:
        os.environ["LOG_LEVEL"] = original_env


def test_level_notset_default_does_not_auto_resolve() -> None:
    """Test that level=NOTSET (default) does NOT auto-resolve."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("INFO")

    # Set environment variable (should be ignored for NOTSET)
    original_env = os.environ.get("LOG_LEVEL")
    os.environ["LOG_LEVEL"] = "DEBUG"

    # --- execute ---
    # Use getLogger() to get a logger properly connected to the hierarchy
    logger = mod_alogs.getLogger("test_level_notset")

    # --- verify ---
    # Should be NOTSET, not auto-resolved from env
    assert logger.level == logging.NOTSET
    assert logger.levelName == "NOTSET"
    # Effective level inherits from root
    assert logger.effectiveLevel == logging.INFO

    # --- cleanup ---
    root.setLevel(original_root_level)
    if original_env is None:
        os.environ.pop("LOG_LEVEL", None)
    else:
        os.environ["LOG_LEVEL"] = original_env


def test_level_explicit_sets_explicit_level() -> None:
    """Test that level=<explicit> sets explicit level."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("INFO")

    # --- execute ---
    logger = mod_alogs.Logger("test_level_explicit", level=logging.ERROR)

    # --- verify ---
    # Should have explicit level, not inherit
    assert logger.level == logging.ERROR
    assert logger.effectiveLevel == logging.ERROR
    assert logger.effectiveLevelName == "ERROR"

    # --- cleanup ---
    root.setLevel(original_root_level)


def test_level_none_uses_determine_log_level_priority() -> None:
    """Test that level=None uses determineLogLevel() priority order."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    root.setLevel("WARNING")

    # Set env var
    original_env = os.environ.get("LOG_LEVEL")
    os.environ["LOG_LEVEL"] = "DEBUG"

    # --- execute ---
    logger = mod_alogs.Logger("test_level_none_priority", level=None)

    # --- verify ---
    # Should resolve from env var (LOG_LEVEL), not root
    assert logger.level == logging.DEBUG
    assert logger.levelName == "DEBUG"

    # --- cleanup ---
    root.setLevel(original_root_level)
    if original_env is None:
        os.environ.pop("LOG_LEVEL", None)
    else:
        os.environ["LOG_LEVEL"] = original_env


def test_level_none_falls_back_to_default() -> None:
    """Test that level=None falls back to default when no env/root set."""
    # --- setup ---
    root = logging.getLogger("")
    original_root_level = root.level
    _constants = mod_alogs.apathetic_logging
    # Root also INHERIT_LEVEL (i.e. NOTSET) (stdlib accepts 0)
    root.setLevel(_constants.INHERIT_LEVEL)

    original_env = os.environ.get("LOG_LEVEL")
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]

    # --- execute ---
    logger = mod_alogs.Logger("test_level_none_default", level=None)

    # --- verify ---
    # Should resolve to default (DETAIL)
    _constants = mod_alogs.apathetic_logging
    assert logger.level == _constants.DETAIL_LEVEL
    assert logger.levelName == "DETAIL"

    # --- cleanup ---
    root.setLevel(original_root_level)
    if original_env is not None:
        os.environ["LOG_LEVEL"] = original_env
