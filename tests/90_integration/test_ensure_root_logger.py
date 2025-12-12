# tests/90_integration/test_ensure_root_logger.py
"""Tests for Logger.ensureRootLogger() class method."""

import logging
import sys

import apathetic_logging as mod_alogs


def test_ensure_root_logger_sets_flag() -> None:
    """ensureRootLogger() should set _root_logger_user_configured flag."""
    # --- execute ---
    mod_alogs.Logger.ensureRootLogger()

    # --- verify ---
    logger_module = sys.modules.get("apathetic_logging.logger")
    assert getattr(logger_module, "_root_logger_user_configured", False) is True


def test_ensure_root_logger_returns_none() -> None:
    """ensureRootLogger() should return None."""
    # --- execute ---
    result = mod_alogs.Logger.ensureRootLogger()

    # --- verify ---
    assert result is None


def test_ensure_root_logger_root_has_correct_name() -> None:
    """ensureRootLogger() should ensure root logger name is 'root'."""
    # --- execute ---
    mod_alogs.Logger.ensureRootLogger()

    # --- verify ---
    root_logger = logging.getLogger("")
    assert root_logger.name == "root"


def test_extend_logging_module_respects_user_configured_flag() -> None:
    """extendLoggingModule() should skip root handling if user configured it."""
    # First ensure root is configured
    mod_alogs.Logger.ensureRootLogger()
    original_root = logging.getLogger("")
    original_id = id(original_root)

    # --- execute ---
    # extendLoggingModule() is called again
    mod_alogs.Logger.extendLoggingModule(replace_root=True)

    # --- verify ---
    new_root = logging.getLogger("")
    # Should still be the same instance (not replaced because user configured it)
    assert id(new_root) == original_id
