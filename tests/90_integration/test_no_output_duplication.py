"""Integration tests for output duplication detection.

Tests that logging output is NOT duplicated in various scenarios:
- Child logger with propagate=True (message goes to root, not duplicated)
- Root logger + child logger together (each logs once)
- Multiple child loggers (no cross-contamination)
- Sequential logging (no message from previous logs appears)

These tests focus on the SYMPTOM (actual duplicated output) rather than
the cause (multiple handlers, re-entry loops, etc). If messages are
duplicated in output, tests fail immediately.

Related: .plan/062_logging_bug_reproduction.md (14-17x duplication bug)
"""

from __future__ import annotations

import io
import logging
import sys
from typing import TYPE_CHECKING

import apathetic_logging as amod_logging
import apathetic_logging.pytest_helpers as mod_pytest_helpers


if TYPE_CHECKING:
    import pytest


def test_child_propagates_without_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify child logger message appears exactly once when propagating to root."""
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("child_propagate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = True
    child.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    child.debug("test_message")

    output = out_buf.getvalue() + err_buf.getvalue()
    lines = [line for line in output.splitlines() if "test_message" in line]

    assert (
        len(lines) == 1
    ), f"Expected exactly 1 'test_message', got {len(lines)}. Output:\n{output}"


def test_root_and_child_logging_no_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify separate messages from root and child don't duplicate."""
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("child_separate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = True
    child.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    root.debug("root_message")
    child.debug("child_message")

    output = out_buf.getvalue() + err_buf.getvalue()
    root_lines = [line for line in output.splitlines() if "root_message" in line]
    child_lines = [line for line in output.splitlines() if "child_message" in line]

    assert (
        len(root_lines) == 1
    ), f"Expected exactly 1 'root_message', got {len(root_lines)}. Output:\n{output}"

    assert (
        len(child_lines) == 1
    ), f"Expected exactly 1 'child_message', got {len(child_lines)}. Output:\n{output}"


def test_multiple_children_no_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify multiple child loggers propagate without duplication."""
    root = isolatedLogging.getRootLogger()
    child1 = isolatedLogging.getLogger("child_multi_1")
    child2 = isolatedLogging.getLogger("child_multi_2")
    child3 = isolatedLogging.getLogger("child_multi_3")

    root.setLevel(logging.DEBUG)
    for child in [child1, child2, child3]:
        child.setLevel(logging.DEBUG)
        child.propagate = True
        child.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    child1.debug("message_1")
    child2.debug("message_2")
    child3.debug("message_3")

    output = out_buf.getvalue() + err_buf.getvalue()
    msg1_lines = [line for line in output.splitlines() if "message_1" in line]
    msg2_lines = [line for line in output.splitlines() if "message_2" in line]
    msg3_lines = [line for line in output.splitlines() if "message_3" in line]

    assert (
        len(msg1_lines) == 1
    ), f"Expected exactly 1 'message_1', got {len(msg1_lines)}. Output:\n{output}"

    assert (
        len(msg2_lines) == 1
    ), f"Expected exactly 1 'message_2', got {len(msg2_lines)}. Output:\n{output}"

    assert (
        len(msg3_lines) == 1
    ), f"Expected exactly 1 'message_3', got {len(msg3_lines)}. Output:\n{output}"


def test_sequential_messages_no_bleed(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify sequential logging doesn't cause messages to bleed."""
    root = isolatedLogging.getRootLogger()
    logger = isolatedLogging.getLogger("sequential_test")

    root.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.propagate = True
    logger.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    logger.debug("seq_1")
    logger.debug("seq_2")
    logger.debug("seq_3")
    logger.debug("seq_4")
    logger.debug("seq_5")

    output = out_buf.getvalue() + err_buf.getvalue()

    for i in range(1, 6):
        msg = f"seq_{i}"
        lines = [line for line in output.splitlines() if msg in line]
        assert (
            len(lines) == 1
        ), f"Expected exactly 1 '{msg}', got {len(lines)}. Output:\n{output}"


def test_non_propagating_child_no_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify non-propagating child logger doesn't duplicate."""
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("child_no_propagate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = False
    child.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    child.debug("no_propagate_message")

    output = out_buf.getvalue() + err_buf.getvalue()
    lines = [line for line in output.splitlines() if "no_propagate_message" in line]

    assert (
        len(lines) == 1
    ), f"Expected exactly 1 'no_propagate_message', got {len(lines)}. Output:\n{output}"


def test_mixed_propagating_and_non_propagating_no_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify mix of propagating and non-propagating children works correctly."""
    root = isolatedLogging.getRootLogger()
    child_prop = isolatedLogging.getLogger("mixed_propagate")
    child_no_prop = isolatedLogging.getLogger("mixed_no_propagate")

    root.setLevel(logging.DEBUG)
    child_prop.setLevel(logging.DEBUG)
    child_prop.propagate = True
    child_prop.handlers.clear()

    child_no_prop.setLevel(logging.DEBUG)
    child_no_prop.propagate = False
    child_no_prop.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    child_prop.debug("UNIQUE_PROP_MSG_XYZ")
    child_no_prop.debug("UNIQUE_NOPROP_MSG_ABC")

    output = out_buf.getvalue() + err_buf.getvalue()
    prop_count = output.count("UNIQUE_PROP_MSG_XYZ")
    no_prop_count = output.count("UNIQUE_NOPROP_MSG_ABC")

    assert (
        prop_count == 1
    ), f"Expected exactly 1 'UNIQUE_PROP_MSG_XYZ', got {prop_count}. Output:\n{output}"

    assert (
        no_prop_count == 1
    ), (
        f"Expected exactly 1 'UNIQUE_NOPROP_MSG_ABC', got {no_prop_count}. "
        f"Output:\n{output}"
    )


def test_root_level_context_no_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify useRootLevel context doesn't cause output duplication."""
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("context_test")

    child.propagate = True
    child.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    with amod_logging.useRootLevel("DEBUG"):
        root.debug("context_root_msg")
        child.debug("context_child_msg")

    output = out_buf.getvalue() + err_buf.getvalue()
    root_lines = [line for line in output.splitlines() if "context_root_msg" in line]
    child_lines = [line for line in output.splitlines() if "context_child_msg" in line]

    assert (
        len(root_lines) == 1
    ), (
        f"Expected exactly 1 'context_root_msg', got {len(root_lines)}. "
        f"Output:\n{output}"
    )

    assert (
        len(child_lines) == 1
    ), (
        f"Expected exactly 1 'context_child_msg', got {len(child_lines)}. "
        f"Output:\n{output}"
    )


def test_sequential_root_level_contexts_no_duplication(
    isolatedLogging: mod_pytest_helpers.LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify sequential useRootLevel contexts don't cause duplication."""
    logger = isolatedLogging.getLogger("sequential_context_test")

    logger.propagate = True
    logger.handlers.clear()

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_buf)
    monkeypatch.setattr(sys, "stderr", err_buf)

    with amod_logging.useRootLevel("DEBUG"):
        logger.debug("context_1_message")

    with amod_logging.useRootLevel("DEBUG"):
        logger.debug("context_2_message")

    with amod_logging.useRootLevel("DEBUG"):
        logger.debug("context_3_message")

    output = out_buf.getvalue() + err_buf.getvalue()
    msg1_lines = [line for line in output.splitlines() if "context_1_message" in line]
    msg2_lines = [line for line in output.splitlines() if "context_2_message" in line]
    msg3_lines = [line for line in output.splitlines() if "context_3_message" in line]

    assert (
        len(msg1_lines) == 1
    ), (
        f"Expected exactly 1 'context_1_message', got {len(msg1_lines)}. "
        f"Output:\n{output}. Sequential contexts may cause duplication."
    )

    assert (
        len(msg2_lines) == 1
    ), (
        f"Expected exactly 1 'context_2_message', got {len(msg2_lines)}. "
        f"Output:\n{output}. Sequential contexts may cause duplication."
    )

    assert (
        len(msg3_lines) == 1
    ), (
        f"Expected exactly 1 'context_3_message', got {len(msg3_lines)}. "
        f"Output:\n{output}. Sequential contexts may cause duplication."
    )
