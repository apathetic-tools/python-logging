"""Integration tests for output duplication detection (symptom-based).

STRATEGY
--------
These tests detect MESSAGE DUPLICATION SYMPTOMS, not specific implementation
bugs. They validate the user-visible outcome: log messages should appear
exactly once, regardless of the underlying cause (duplicate handlers,
propagation loops, cache corruption, or other mechanisms).

WHY SYMPTOM-BASED TESTS?
------------------------
Message duplication can be introduced by many different root causes:
- Handler duplication (same handler registered multiple times)
- Propagation loops (messages propagating through multiple paths)
- Cache state corruption (stream IDs causing re-entry)
- Registry inconsistencies
- And potentially other unknown causes discovered during refactoring

A symptom-based approach catches ANY duplication bug, not just ones we
anticipate. This provides defense-in-depth against regressions.

RELATIONSHIP TO MECHANISM TESTS
--------------------------------
Mechanism-specific tests (test_useRootLevel_sequential_bug.py) verify HOW
specific fixes work (cache clearing, rebuild loop prevention, etc.).

Symptom tests verify THAT user-visible bugs don't happen.

Together they provide:
- Confidence that specific issues are fixed (mechanism tests)
- Broad protection against future duplication bugs (symptom tests)

PARALLEL EXECUTION NOTE
------------------------
These tests use manual stream capture (io.StringIO) instead of pytest's
caplog fixture. This approach works reliably in:
- Serial mode (pytest without xdist)
- Parallel mode (pytest-xdist with multiple workers)
- Package mode (src/ imports)
- Stitched mode (dist/ single-file)
- Zipapp mode (dist/ .pyz bundle)

Manual stream capture avoids caplog's worker process inconsistencies and
handler identity issues in stitched mode.

Related: test_useRootLevel_sequential_bug.py (mechanism-specific tests)
"""

from __future__ import annotations

import logging

import apathetic_logging as amod_logging
import apathetic_logging.pytest_helpers as mod_pytest_helpers


# Maximum handlers allowed before we suspect duplication
MAX_HANDLERS_REASONABLE = 3


def test_child_propagates_without_excessive_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify child logger message appears without excessive duplication.

    Uses manual stream capture to count log records. Checks that when a child logger
    propagates to root, messages aren't duplicated excessively (e.g.,
    14-17 times like the .plan/062 bug).
    """
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("child_propagate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = True

    # Capture output with manual stream redirection
    with isolatedLogging.captureStreams() as capture:
        child.debug("UNIQUE_CHILD_PROPAGATE_001")

    # Count message appearances in output
    count = capture.countMessage("UNIQUE_CHILD_PROPAGATE_001")

    # Should appear exactly 1 time, not 14-17 (the bug)
    assert count == 1, (
        f"Expected message once, got {count} times. "
        f"This indicates duplication like .plan/062 bug."
    )


def test_root_and_child_logging_no_excessive_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify separate messages from root and child don't duplicate excessively."""
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("child_separate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = True

    # Capture output with manual stream redirection
    with isolatedLogging.captureStreams() as capture:
        root.debug("UNIQUE_ROOT_MESSAGE_002")
        child.debug("UNIQUE_CHILD_MESSAGE_002")

    # Each should appear exactly once
    root_count = capture.countMessage("UNIQUE_ROOT_MESSAGE_002")
    child_count = capture.countMessage("UNIQUE_CHILD_MESSAGE_002")

    assert root_count == 1, (
        f"Root message appeared {root_count} times (expected 1). Duplication detected."
    )
    assert child_count == 1, (
        f"Child message appeared {child_count} times (expected 1). "
        f"Duplication detected."
    )


def test_multiple_children_no_excessive_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify multiple child loggers propagate without excessive duplication."""
    root = isolatedLogging.getRootLogger()
    child1 = isolatedLogging.getLogger("child_multi_1")
    child2 = isolatedLogging.getLogger("child_multi_2")
    child3 = isolatedLogging.getLogger("child_multi_3")

    root.setLevel(logging.DEBUG)
    for child in [child1, child2, child3]:
        child.setLevel(logging.DEBUG)
        child.propagate = True

    # Capture output with manual stream redirection
    with isolatedLogging.captureStreams() as capture:
        child1.debug("UNIQUE_MULTI_MSG_1_003")
        child2.debug("UNIQUE_MULTI_MSG_2_003")
        child3.debug("UNIQUE_MULTI_MSG_3_003")

    # Each should appear exactly once
    for i, msg in enumerate(
        [
            "UNIQUE_MULTI_MSG_1_003",
            "UNIQUE_MULTI_MSG_2_003",
            "UNIQUE_MULTI_MSG_3_003",
        ],
        1,
    ):
        count = capture.countMessage(msg)
        assert count == 1, (
            f"Message {i} appeared {count} times (expected 1). Duplication detected."
        )


def test_sequential_messages_no_excessive_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify sequential logging doesn't cause excessive duplication."""
    root = isolatedLogging.getRootLogger()
    logger = isolatedLogging.getLogger("sequential_test")

    root.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

    # Capture output with manual stream redirection
    with isolatedLogging.captureStreams() as capture:
        for i in range(1, 6):
            logger.debug("UNIQUE_SEQ_MSG_%d_004", i)

    # Each should appear exactly once
    for i in range(1, 6):
        msg = f"UNIQUE_SEQ_MSG_{i}_004"
        count = capture.countMessage(msg)
        assert count == 1, (
            f"Sequential message {i} appeared {count} times (expected 1). "
            f"Duplication or bleed detected."
        )


def test_non_propagating_child_no_excessive_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify non-propagating child logger doesn't have duplicate handlers.

    Non-propagating loggers get their own handler. This test verifies that
    when a non-propagating logger logs, it doesn't accumulate duplicate
    handlers (e.g., 14+ handlers like the .plan/062 bug could cause).
    """
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("child_no_propagate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = False

    # Log from non-propagating child to trigger handler creation
    child.debug("UNIQUE_NOPROP_MSG_005")

    # Non-propagating logger should have its own handler(s), but not excessively
    handler_count = len(child.handlers)
    assert handler_count > 0, (
        f"Non-propagating child should have handler, got {handler_count}."
    )
    assert handler_count <= MAX_HANDLERS_REASONABLE, (
        f"Non-propagating child has {handler_count} handlers "
        f"(expected ≤{MAX_HANDLERS_REASONABLE}). "
        f"Handler duplication detected."
    )


def test_mixed_propagating_and_non_propagating_no_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify mix of propagating and non-propagating children works correctly."""
    root = isolatedLogging.getRootLogger()
    child_prop = isolatedLogging.getLogger("mixed_propagate")
    child_no_prop = isolatedLogging.getLogger("mixed_no_propagate")

    root.setLevel(logging.DEBUG)
    child_prop.setLevel(logging.DEBUG)
    child_prop.propagate = True

    child_no_prop.setLevel(logging.DEBUG)
    child_no_prop.propagate = False

    # Capture output with manual stream redirection
    with isolatedLogging.captureStreams() as capture:
        child_prop.debug("UNIQUE_PROP_MSG_XYZ_006")
        child_no_prop.debug("UNIQUE_NOPROP_MSG_ABC_006")

    # Check propagating message in output
    prop_count = capture.countMessage("UNIQUE_PROP_MSG_XYZ_006")
    assert prop_count == 1, (
        f"Propagating message appeared {prop_count} times (expected 1)."
    )

    # Non-propagating logger should have reasonable handler count
    no_prop_handler_count = len(child_no_prop.handlers)
    assert no_prop_handler_count > 0, (
        f"Non-propagating child should have handler, got {no_prop_handler_count}."
    )
    assert no_prop_handler_count <= MAX_HANDLERS_REASONABLE, (
        f"Non-propagating child has {no_prop_handler_count} handlers "
        f"(expected ≤{MAX_HANDLERS_REASONABLE}). "
        f"Handler duplication detected."
    )


def test_root_level_context_no_excessive_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify useRootLevel context doesn't cause excessive output duplication."""
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("context_test")

    child.propagate = True

    # Capture output with manual stream redirection
    with (
        isolatedLogging.captureStreams() as capture,
        amod_logging.useRootLevel("DEBUG"),
    ):
        root.debug("UNIQUE_CONTEXT_ROOT_MSG_007")
        child.debug("UNIQUE_CONTEXT_CHILD_MSG_007")

    # Each should appear exactly once
    root_count = capture.countMessage("UNIQUE_CONTEXT_ROOT_MSG_007")
    child_count = capture.countMessage("UNIQUE_CONTEXT_CHILD_MSG_007")

    assert root_count == 1, (
        f"Context root message appeared {root_count} times (expected 1). "
        f"useRootLevel caused duplication."
    )
    assert child_count == 1, (
        f"Context child message appeared {child_count} times (expected 1). "
        f"useRootLevel caused duplication."
    )


def test_sequential_root_level_contexts_no_excessive_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
) -> None:
    """Verify sequential useRootLevel contexts don't cause excessive duplication.

    This is the critical test for .plan/062 bug (14-17x duplication).
    Ensures that sequential useRootLevel() calls don't cause messages to
    appear multiple times.
    """
    logger = isolatedLogging.getLogger("sequential_context_test")
    logger.propagate = True

    # Use useRootLevel sequentially (reproduces the bug scenario)
    with (
        isolatedLogging.captureStreams() as capture1,
        amod_logging.useRootLevel("DEBUG"),
    ):
        logger.debug("UNIQUE_SEQUENTIAL_CONTEXT_MSG_1_008")
    msg1_count = capture1.countMessage("UNIQUE_SEQUENTIAL_CONTEXT_MSG_1_008")

    with (
        isolatedLogging.captureStreams() as capture2,
        amod_logging.useRootLevel("DEBUG"),
    ):
        logger.debug("UNIQUE_SEQUENTIAL_CONTEXT_MSG_2_008")
    msg2_count = capture2.countMessage("UNIQUE_SEQUENTIAL_CONTEXT_MSG_2_008")

    with (
        isolatedLogging.captureStreams() as capture3,
        amod_logging.useRootLevel("DEBUG"),
    ):
        logger.debug("UNIQUE_SEQUENTIAL_CONTEXT_MSG_3_008")
    msg3_count = capture3.countMessage("UNIQUE_SEQUENTIAL_CONTEXT_MSG_3_008")

    # Each should appear exactly once (not 14-17 times like the bug)
    for i, count in enumerate([msg1_count, msg2_count, msg3_count], 1):
        assert count == 1, (
            f"Sequential context message {i} appeared {count} times "
            f"(expected 1). "
            f"This is the .plan/062 bug - sequential useRootLevel causing "
            f"duplication."
        )
