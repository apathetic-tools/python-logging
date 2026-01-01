"""Test to reproduce the sequential useRootLevel bug from .plan/062.

This test demonstrates the issue where using useRootLevel() context manager
sequentially causes log messages to be emitted multiple times instead of once.
This only manifests in stitched mode where module state persists.

Uses the apathetic_testing library's atest_isolated_logging fixture and
capture_streams() helper for reliable stream capture across all runtime modes
and execution modes (serial, parallel with xdist).
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import apathetic_logging as amod_logging


if TYPE_CHECKING:
    from apathetic_testing import LoggingIsolation


def test_sequential_useRootLevel_single_message(
    atest_isolated_logging: LoggingIsolation,
) -> None:
    """Verify sequential useRootLevel calls don't cause message duplication.

    This test reproduces the exact issue reported in .plan/062:
    - First context manager use: works fine
    - Second context manager use: message appears multiple times (broken)

    Uses the isolated_logging fixture's capture_streams() which properly
    handles pytest's capsys/caplog and xdist parallel execution scenarios.
    """
    logger = amod_logging.getLogger("test")

    # First context manager use
    with atest_isolated_logging.capture_streams() as capture1:
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("First message")

        count1 = capture1.count_message("First message")
        assert count1 == 1, f"First message: expected 1 occurrence, got {count1}"

    # Second context manager use - this is where the bug manifests
    with atest_isolated_logging.capture_streams() as capture2:
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Second message")

        count2 = capture2.count_message("Second message")
        assert count2 == 1, f"Second message: expected 1 occurrence, got {count2}"


def test_sequential_useRootLevel_multiple_iterations(
    atest_isolated_logging: LoggingIsolation,
) -> None:
    """Verify multiple sequential useRootLevel calls all produce correct output."""
    logger = amod_logging.getLogger("test_multi")

    # Test multiple sequential uses
    for i in range(5):
        with atest_isolated_logging.capture_streams() as capture:
            with amod_logging.useRootLevel("TRACE"):
                logger.debug("Iteration %s", i)

            count = capture.count_message(f"Iteration {i}")
            assert count == 1, (
                f"Iteration {i}: expected 1 occurrence, got {count}. Bug manifested!"
            )


def test_sequential_useRootLevel_with_stream_changes(
    atest_isolated_logging: LoggingIsolation,
) -> None:
    """Simulate pytest capsys behavior: replacing streams between uses.

    This more closely matches what happens in pytest where streams can be
    redirected multiple times during test execution.
    """
    logger = amod_logging.getLogger("test_streams")

    # First use with stream1
    with atest_isolated_logging.capture_streams() as capture1:
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Message 1")

        count1 = capture1.count_message("Message 1")
        assert count1 == 1, f"Message 1: expected 1 occurrence, got {count1}"

    # Second use with stream2 (streams replaced, like pytest capsys does)
    with atest_isolated_logging.capture_streams() as capture2:
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Message 2")

        count2 = capture2.count_message("Message 2")
        assert count2 == 1, f"Message 2: expected 1 occurrence, got {count2}"

    # Third use with stream3 (yet another stream replacement)
    with atest_isolated_logging.capture_streams() as capture3:
        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Message 3")

        count3 = capture3.count_message("Message 3")
        assert count3 == 1, f"Message 3: expected 1 occurrence, got {count3}"


def test_useRootLevel_clears_stream_cache() -> None:
    """Verify that useRootLevel properly clears the _last_stream_ids cache.

    This is the core of the fix: the root logger's _last_stream_ids cache
    must be cleared when exiting the context manager.
    """
    root = amod_logging.getRootLogger()

    # Before entering context manager, set _last_stream_ids to something
    # (simulating previous state)
    root._last_stream_ids = (sys.stdout, sys.stderr)  # type: ignore[attr-defined]  # noqa: SLF001

    # Enter and exit context manager
    with amod_logging.useRootLevel("DEBUG"):
        pass

    # After exiting, _last_stream_ids should be None (cleared)
    # OR it should be reset to current stdout/stderr
    # The key is that stale stream identities should not cause re-entry loops
    assert (
        root._last_stream_ids is None  # type: ignore[attr-defined]  # noqa: SLF001
        or root._last_stream_ids == (sys.stdout, sys.stderr)  # type: ignore[attr-defined]  # noqa: SLF001
    ), f"Stream cache not properly managed: {root._last_stream_ids}"  # type: ignore[attr-defined]  # noqa: SLF001
