"""Mechanism tests for .plan/062 sequential useRootLevel bug fix.

This file verifies the FIX MECHANISM, not just symptoms.

Bug Report: .plan/062_logging_bug_reproduction.md
Root Cause: Stale _last_stream_ids cache → false stream change → rebuild loop
Fix Location: src/apathetic_logging/logging_root.py:410
Fix: root_any._last_stream_ids = None  # Line 410 - Reset cache on context exit

What This File Tests:
- _last_stream_ids cache management (THE FIX)
- Handler rebuild detection and prevention
- Re-entry loop detection
- State transition verification

Related Files:
- Symptom tests: test_useRootLevel_sequential_bug.py (checks output count)
- This file: Mechanism tests (checks FIX MECHANISM)

Expected Behavior:
- All 8 tests PASS when fix is present (line 410 exists)
- Tests FAIL immediately if fix is removed or broken

Critical Failure Points (if fix is removed):
- Test 1: Cache not cleared after context exit
- Test 2: Rebuild loop detected (>2 rebuilds per context)
- Test 3: Handler called >1 time per message
- Test 5: Cache state machine broken

Time to Run: < 2 seconds (all 8 tests combined)

Bug Severity: CRITICAL
- Affects: Stitched mode logging (module-level state persistence)
- Impact: Sequential tests cause 14-17x message duplication
- First Report Date: 2025-12-28
- Investigation: .plan/062_logging_bug_reproduction.md
"""

import logging
import sys
from io import StringIO

import apathetic_logging as amod_logging
import apathetic_logging.pytest_helpers as mod_pytest_helpers


# Allow up to 3 lines: 1 for the message + potential formatting/blank lines
# (In stitched mode, logging may produce extra lines due to different formatting)
# The critical thing is we should NOT see 14-17 lines (the original bug)
MAX_EXPECTED_LINES = 3


# ============================================================================
# PRIORITY 1: CRITICAL MECHANISM VERIFICATION TESTS
# These tests MUST pass with fix present, MUST fail if fix is removed
# ============================================================================


def test_useRootLevel_exit_clears_stream_cache_explicit(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """CRITICAL: Verify useRootLevel.__exit__() clears _last_stream_ids.

    This test directly verifies the fix from commit bc5fd7e line 410:
        root_any._last_stream_ids = None

    If this test fails, the fix has been removed or is broken.

    Related Bug: .plan/062_logging_bug_reproduction.md
    Impact: Without this fix, sequential context managers cause 14-17x duplication
    """
    root = isolatedLogging.getRootLogger()

    # Verify root logger has the _last_stream_ids attribute
    assert hasattr(root, "_last_stream_ids"), (
        "Root logger missing _last_stream_ids attribute. "
        "Either the logger class changed or the fix was removed."
    )

    # Set a value to simulate previous state (before context manager is entered)
    root._last_stream_ids = (sys.stdout, sys.stderr)  # noqa: SLF001
    assert (
        root._last_stream_ids is not None  # noqa: SLF001
    ), "Precondition failed: cache not set"

    # Use context manager
    with amod_logging.useRootLevel("DEBUG"):
        # Inside context, cache state is implementation-dependent
        # We don't check it here - we check after exit
        pass

    # CRITICAL CHECK: After exit, _last_stream_ids MUST be None
    # This is THE FIX from commit bc5fd7e line 410
    assert root._last_stream_ids is None, (  # noqa: SLF001
        f"CRITICAL BUG: useRootLevel.__exit__() must clear _last_stream_ids to None. "
        f"The fix from commit bc5fd7e line 410 may have been removed. "
        f"Expected: None, Got: {root._last_stream_ids}. "
        f"Fix line: root_any._last_stream_ids = None"
    )


def test_no_rebuild_loop_with_stream_replacement(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Detect rebuild loop from .plan/062 (14-17 message duplicates).

    Bug Mechanism:
    1. First context: useRootLevel() enters → sets _last_stream_ids
    2. Pytest between tests: Replaces sys.stdout/stderr with capture objects
    3. Second context: useRootLevel() enters
       - Old cache value still present (before fix)
       - Detects "stream change" (old vs. current streams)
       - Triggers handler rebuild
       - Rebuild calls logging code internally
       - Calls _log() again → calls manageHandlers() again
       - LOOP: rebuild → log → rebuild → log → ... (14-17 times)

    This test tracks rebuild calls and fails if excessive rebuilding occurs.

    Related Bug: .plan/062 describes the 14-17 duplicates mechanism
    Fix: Clearing _last_stream_ids prevents false stream change detection
    """
    logger = isolatedLogging.getLogger("test")
    root = isolatedLogging.getRootLogger()

    # Track rebuild calls by monkey-patching _rebuildAppatheticHandlers
    rebuild_counts: list[int] = []
    current_count = 0
    original_rebuild = root._rebuildAppatheticHandlers  # noqa: SLF001

    max_rebuilds_allowed = 5

    def tracked_rebuild() -> None:
        nonlocal current_count
        current_count += 1
        if current_count > max_rebuilds_allowed:
            msg = (
                f"REBUILD LOOP DETECTED: _rebuildAppatheticHandlers called "
                f"{current_count} times in single context. "
                f"This is the bug from .plan/062 (expected 14-17 calls before fix). "
                f"The fix (clearing _last_stream_ids) may be broken or removed. "
                f"Failing at {max_rebuilds_allowed}+ rebuilds to detect the loop early."
            )
            raise AssertionError(msg)
        return original_rebuild()

    root._rebuildAppatheticHandlers = tracked_rebuild  # noqa: SLF001

    try:
        # First context with stream replacement
        capture1 = StringIO()
        sys.stdout = capture1
        sys.stderr = capture1

        current_count = 0
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("First message")
        rebuild_counts.append(current_count)

        # Replace streams with different objects (like pytest does between tests)
        capture2 = StringIO()
        sys.stdout = capture2
        sys.stderr = capture2

        # Second context - this is where the rebuild loop would trigger without the fix
        current_count = 0
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Second message")
        rebuild_counts.append(current_count)

        # Replace streams again
        capture3 = StringIO()
        sys.stdout = capture3
        sys.stderr = capture3

        # Third context to ensure pattern is consistent
        current_count = 0
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Third message")
        rebuild_counts.append(current_count)

        # Verify no excessive rebuilds in any context
        max_expected_rebuilds = 2
        for i, count in enumerate(rebuild_counts):
            assert (
                count <= max_expected_rebuilds
            ), (
                f"Context {i}: Rebuild loop detected ({count} rebuilds). "
                f"Expected ≤{max_expected_rebuilds} rebuilds per context. "
                f"All counts: {rebuild_counts}. The fix may be broken."
            )

    finally:
        root._rebuildAppatheticHandlers = original_rebuild  # noqa: SLF001


def test_exact_emission_count_via_handler(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Count exact handler emissions to detect message duplication.

    Output line counting can be fooled by:
    - Formatting differences
    - Blank lines
    - Multiline messages
    - Captured stream variations

    Handler call counting is precise:
    - 1 logger.log() call = exactly 1 handler.emit() call (when working correctly)
    - Bug: 1 logger.log() call = 14-17 handler.emit() calls (re-entry loop)

    This test creates a custom CountingHandler that tracks emissions directly.

    Related Bug: .plan/062 states "message emitted 14-17 times through single handler"
    """

    class CountingHandler(logging.Handler):
        """Custom handler that counts emit() calls."""

        def __init__(self) -> None:
            super().__init__()
            self.count = 0
            self.records: list[logging.LogRecord] = []

        def emit(self, record: logging.LogRecord) -> None:
            """Track each emission."""
            self.count += 1
            self.records.append(record)

    logger = isolatedLogging.getLogger("test")
    root = isolatedLogging.getRootLogger()

    # Create and attach counter
    counter = CountingHandler()
    counter.setLevel(logging.DEBUG)
    root.addHandler(counter)

    try:
        # Sequential uses with stream replacement (reproduces bug scenario)
        for i in range(3):
            # Replace streams each iteration (like pytest does between tests)
            capture = StringIO()
            sys.stdout = capture
            sys.stderr = capture

            # Reset counter for this iteration
            counter.count = 0
            counter.records.clear()

            # Log single message
            with amod_logging.useRootLevel("TRACE"):
                logger.debug("Iteration %d: test message", i)

            # Verify EXACTLY ONE emission to handler
            assert (
                counter.count == 1
            ), f"Iteration {i}: Message emitted {counter.count} times to handler (expected exactly 1). This is the bug from .plan/062 (14-17 emissions). Messages: {[r.getMessage() for r in counter.records]}"

    finally:
        root.removeHandler(counter)


# ============================================================================
# PRIORITY 2: REGRESSION DETECTION TESTS
# These tests prevent the bug from returning in different forms
# ============================================================================


def test_handler_count_remains_one_during_sequential_use(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify handler count stays at 1 throughout sequential usage.

    Bug Report (.plan/062) states:
    "NOT handler duplication: there is exactly 1 handler present.
    The message is being logged 14-17 times through the same handler."

    This test confirms that assertion and detects if the bug changes form
    (e.g., if it becomes actual handler duplication instead of re-entry loop).
    """
    root = isolatedLogging.getRootLogger()
    logger = isolatedLogging.getLogger("test")

    for i in range(5):
        # Replace streams each iteration (like pytest does between tests)
        capture = StringIO()
        sys.stdout = capture
        sys.stderr = capture

        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Iteration %d", i)

            # Count DualStreamHandlers (the apathetic logging handlers)
            apathetic_handlers = [
                h for h in root.handlers if isinstance(h, amod_logging.DualStreamHandler)
            ]

            assert (
                len(apathetic_handlers) == 1
            ), f"Iteration {i}: Expected exactly 1 DualStreamHandler, got {len(apathetic_handlers)}. All handlers: {root.handlers}. Bug may have changed form (handler duplication vs re-entry)."


def test_stream_cache_state_machine(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify _last_stream_ids follows expected state transitions.

    Expected state lifecycle:
    1. None or unset (after fixture setup or useRootLevel exit)
    2. (stdout, stderr) tuple (after handler setup during logging)
    3. None (after useRootLevel exit) ← THE FIX MUST HAPPEN HERE

    Critical transition: State 2 → State 3
    - The exit handler MUST clear _last_stream_ids to None
    - This prevents false stream change detection on next use
    """
    root = isolatedLogging.getRootLogger()
    logger = isolatedLogging.getLogger("test")

    # Iteration 1: First context manager use
    with amod_logging.useRootLevel("DEBUG"):
        logger.debug("First message")
        # Cache may or may not be set during logging - implementation dependent
        cache_inside = root._last_stream_ids  # noqa: SLF001

    # CRITICAL: After first exit, MUST be None
    assert (
        root._last_stream_ids is None  # noqa: SLF001
    ), f"State 1: After first useRootLevel exit, cache must be None. Got: {root._last_stream_ids}. Fix may be broken."

    # Iteration 2: With different streams (like pytest between tests)
    capture = StringIO()
    sys.stdout = capture
    sys.stderr = capture

    with amod_logging.useRootLevel("DEBUG"):
        logger.debug("Second message")
        # Cache may or may not be set during logging

    # CRITICAL: After second exit, MUST be None again
    assert (
        root._last_stream_ids is None  # noqa: SLF001
    ), f"State 2: After second useRootLevel exit, cache must be None. Got: {root._last_stream_ids}. Fix may be broken."


def test_sequential_contexts_produce_consistent_output(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Each context should produce similar output (no escalating duplication).

    Bug: First context outputs 1-2 lines, second outputs 14-17 lines
    Fixed: All contexts output 1-2 lines consistently

    This test detects if the bug returns in a milder form or
    if duplication escalates as contexts are nested.
    """
    logger = isolatedLogging.getLogger("test")
    line_counts: list[int] = []

    for i in range(5):
        capture = StringIO()
        sys.stdout = capture
        sys.stderr = capture

        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Iteration %d", i)

        output = capture.getvalue()
        lines = [line for line in output.splitlines() if line.strip()]
        line_counts.append(len(lines))

    # All iterations should have similar output
    max_lines = max(line_counts)
    min_lines = min(line_counts)

    # Allow small variation (1-3 lines per message) but not 14-17x
    # Stitched mode may produce 3 lines due to formatting, package mode produces 1-2
    max_expected_lines = 3
    assert (
        max_lines <= max_expected_lines
    ), (
        f"Excessive output detected: {max_lines} lines. All counts: {line_counts}. "
        f"Bug may have returned. Expected ≤{max_expected_lines} lines per message."
    )

    # Variation should be minimal (all iterations similar)
    # All counts should be identical or very close
    variation = max_lines - min_lines
    assert (
        variation == 0
    ), (
        f"Inconsistent output across iterations: {line_counts}. "
        f"Expected consistent counts, but variation is {variation}. "
        f"Bug may cause variable duplication."
    )


# ============================================================================
# PRIORITY 3: EDGE CASE TESTS
# These tests ensure fix works in all scenarios
# ============================================================================


def test_nested_useRootLevel_contexts_clear_cache(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Nested contexts should each clear cache on exit.

    Each __exit__ should clear _last_stream_ids independently.
    Nested contexts can occur when:
    - Test uses context manager, then calls another function that uses context manager
    - Utility functions wrap logging setup
    - Framework setup/teardown has multiple levels
    """
    root = isolatedLogging.getRootLogger()
    logger = isolatedLogging.getLogger("test")

    capture = StringIO()
    sys.stdout = capture
    sys.stderr = capture

    with amod_logging.useRootLevel("TRACE"):
        logger.debug("Outer start")

        # Inner context should work correctly
        with amod_logging.useRootLevel("DEBUG"):
            logger.debug("Inner")

        # After inner exit, cache should be None
        assert root._last_stream_ids is None, (  # noqa: SLF001
            "Inner context exit must clear cache. "
            "The finally block in __exit__ may be broken."
        )

        logger.debug("Outer continue")

    # After outer exit, cache should be None
    assert root._last_stream_ids is None, (  # noqa: SLF001
        "Outer context exit must clear cache. "
        "The finally block in __exit__ may be broken."
    )

    # Verify reasonable output (no runaway duplication)
    output = capture.getvalue()
    lines = [line for line in output.splitlines() if line.strip()]
    max_nested_lines = 9
    assert (
        len(lines) <= max_nested_lines
    ), (
        f"Expected ≤{max_nested_lines} output lines from 3 messages, got {len(lines)}. "
        f"Possible duplication in nested contexts."
    )


def test_exception_during_context_still_clears_cache(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Cache must be cleared even if exception occurs in context.

    The fix is in a finally block in __exit__, so it should always execute:

        finally:
            root_any._last_stream_ids = None

    This test verifies that cleanup happens even when exceptions are raised.
    """
    root = isolatedLogging.getRootLogger()

    # Set cache to non-None initial state
    root._last_stream_ids = (sys.stdout, sys.stderr)  # noqa: SLF001
    assert (
        root._last_stream_ids is not None  # noqa: SLF001
    ), "Precondition: cache should be set"

    # Context with exception
    exc_msg = "Test exception - should not prevent cleanup"
    try:
        with amod_logging.useRootLevel("DEBUG"):
            msg = exc_msg  # noqa: F841
            raise ValueError(exc_msg)
    except ValueError:
        pass  # Expected

    # Despite exception, cache must be cleared
    assert root._last_stream_ids is None, (  # noqa: SLF001
        "Exception during context should not prevent cache cleanup. "
        "The finally block in __exit__ may be missing or broken. "
        "Check: useRootLevel.__exit__() has try/finally that clears cache."
    )
