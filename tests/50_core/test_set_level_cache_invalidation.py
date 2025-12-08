# tests/50_core/test_set_level_cache_invalidation.py
"""Tests for cache invalidation when setLevel() is called.

This test verifies that the isEnabledFor() cache is properly cleared when
setLevel() is called, preventing stale cache entries from persisting after
level changes.
"""

import logging
from typing import TYPE_CHECKING

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


def test_set_level_clears_is_enabled_for_cache(
    direct_logger: Logger,
) -> None:
    """setLevel() should clear the isEnabledFor() cache when level changes.

    This test verifies the fix for a bug where the isEnabledFor() cache
    wasn't being cleared when setLevel() was called. This caused stale cache
    entries (e.g., isEnabledFor(TRACE=5)=True) to persist after changing the
    logger level from TRACE to DEBUG, making trace messages appear even when
    they shouldn't.

    Steps:
    1. Set level to TRACE
    2. Call trace() to trigger handlers and cache isEnabledFor(TRACE_LEVEL)=True
    3. Set level to DEBUG
    4. Verify isEnabledFor(TRACE_LEVEL) returns False (cache should be cleared)
    """
    _constants = mod_alogs.apathetic_logging
    trace_level = _constants.TRACE_LEVEL

    # Step 1: Set level to TRACE
    direct_logger.setLevel("trace")
    assert direct_logger.level == trace_level
    assert direct_logger.getEffectiveLevel() == trace_level

    # Step 2: Call trace() to trigger handlers and cache isEnabledFor(5)=True
    # This will call isEnabledFor(TRACE_LEVEL) internally, which caches the result
    direct_logger.trace("trigger")

    # Verify the cache was populated (if it exists)
    cache_before = getattr(direct_logger, "_cache", None)
    if cache_before is not None:
        # The cache should now contain an entry for TRACE_LEVEL
        assert trace_level in cache_before
        assert cache_before[trace_level] is True

    # Step 3: Set level to DEBUG
    direct_logger.setLevel("debug")
    assert direct_logger.level == logging.DEBUG
    assert direct_logger.getEffectiveLevel() == logging.DEBUG

    # Step 4: Verify isEnabledFor(TRACE_LEVEL) returns False
    # The cache should have been cleared, so this should recalculate correctly
    is_enabled = direct_logger.isEnabledFor(trace_level)
    assert is_enabled is False, (
        f"isEnabledFor({trace_level}) should return False "
        f"after setting level to DEBUG. "
        f"Current level: {direct_logger.level}, "
        f"Effective level: {direct_logger.getEffectiveLevel()}"
    )

    # Verify the cache was cleared (if it exists)
    cache_after = getattr(direct_logger, "_cache", None)
    if cache_after is not None and trace_level in cache_after:
        # If it's in the cache, it should be False (correctly recalculated)
        assert cache_after[trace_level] is False
    # If it's not in the cache, that's also fine - it will be
    # recalculated when needed


def test_set_level_cache_invalidation_detailed_debug(
    direct_logger: Logger,
) -> None:
    """Detailed test with debug output to verify cache invalidation behavior.

    This is similar to test_set_level_clears_is_enabled_for_cache but includes
    more detailed assertions about the cache state for debugging purposes.
    """
    _constants = mod_alogs.apathetic_logging
    trace_level = _constants.TRACE_LEVEL

    # Initial state
    direct_logger.setLevel("trace")
    assert direct_logger.level == trace_level
    assert direct_logger.getEffectiveLevel() == trace_level

    # Check initial cache state
    cache_initial = getattr(direct_logger, "_cache", None)
    initial_cache_size = len(cache_initial) if cache_initial else 0

    # Trigger cache by calling trace()
    direct_logger.trace("trigger")

    # Verify cache was populated
    cache_after_trace = getattr(direct_logger, "_cache", None)
    if cache_after_trace is not None:
        assert trace_level in cache_after_trace
        assert cache_after_trace[trace_level] is True
        cache_size_after_trace = len(cache_after_trace)
        assert cache_size_after_trace > initial_cache_size

    # Change level to DEBUG
    direct_logger.setLevel("debug")

    # Verify level changed
    assert direct_logger.level == logging.DEBUG
    assert direct_logger.getEffectiveLevel() == logging.DEBUG

    # Check cache state after setLevel
    cache_after_setlevel = getattr(direct_logger, "_cache", None)

    # The key assertion: isEnabledFor should return False
    is_enabled = direct_logger.isEnabledFor(trace_level)
    assert is_enabled is False, (
        f"After setLevel('debug'), isEnabledFor({trace_level}) should be False. "
        f"logger.level={direct_logger.level}, "
        f"logger.getEffectiveLevel()={direct_logger.getEffectiveLevel()}, "
        f"cache={cache_after_setlevel}"
    )

    # Verify cache behavior
    if cache_after_setlevel is not None and trace_level in cache_after_setlevel:
        # The cache should either:
        # 1. Be empty (cleared), or
        # 2. Contain the correct value (False) if it was repopulated
        assert cache_after_setlevel[trace_level] is False, (
            f"Cache entry for {trace_level} should be False, "
            f"but got {cache_after_setlevel[trace_level]}"
        )
