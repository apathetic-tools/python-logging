# tests/50_core/test_colorize.py
"""Tests for color utility helpers in module.utils."""

from typing import TYPE_CHECKING

import pytest

import apathetic_logging as mod_alogs


if TYPE_CHECKING:
    from apathetic_logging import Logger  # noqa: ICN003
else:
    Logger = mod_alogs.Logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset environment variables and cached state before each test."""
    # fixture itself deals with context teardown, don't need to explicitly set
    for var in ("NO_COLOR", "FORCE_COLOR"):
        monkeypatch.delenv(var, raising=False)


# ---------------------------------------------------------------------------
# colorize() behavior
# ---------------------------------------------------------------------------


def test_colorize_explicit_true_false(
    direct_logger: Logger,
) -> None:
    """Explicit enable_color argument forces color on or off."""
    # --- setup ---
    text = "test"

    # --- execute and verify ---
    assert (
        direct_logger.colorize(
            text,
            mod_alogs.apathetic_logging.ANSIColors.GREEN,
            enable_color=True,
        )
    ) == (
        f"{mod_alogs.apathetic_logging.ANSIColors.GREEN}"
        f"{text}"
        f"{mod_alogs.apathetic_logging.ANSIColors.RESET}"
    )
    assert (
        direct_logger.colorize(
            text,
            mod_alogs.apathetic_logging.ANSIColors.GREEN,
            enable_color=False,
        )
    ) == text


def test_colorize_respects_instance_flag(
    direct_logger: Logger,
) -> None:
    """colorize() should honor logger.enable_color."""
    # --- setup ---
    text = "abc"

    # --- execute and verify ---
    direct_logger.enable_color = True
    assert direct_logger.colorize(
        text, mod_alogs.apathetic_logging.ANSIColors.GREEN
    ) == (
        f"{mod_alogs.apathetic_logging.ANSIColors.GREEN}"
        f"{text}"
        f"{mod_alogs.apathetic_logging.ANSIColors.RESET}"
    )

    direct_logger.enable_color = False
    assert (
        direct_logger.colorize(text, mod_alogs.apathetic_logging.ANSIColors.GREEN)
        == text
    )


def test_colorize_does_not_mutate_text(
    direct_logger: Logger,
) -> None:
    """colorize() should not alter text content aside from color codes."""
    text = "safe!"
    direct_logger.enable_color = True
    result = direct_logger.colorize(text, mod_alogs.apathetic_logging.ANSIColors.GREEN)
    assert text in result
    assert result.startswith(mod_alogs.apathetic_logging.ANSIColors.GREEN)
    assert result.endswith(mod_alogs.apathetic_logging.ANSIColors.RESET)
    # ensure text object itself wasn't modified
    assert text == "safe!"


def test_colorize_empty_text(
    direct_logger: Logger,
) -> None:
    """Empty strings should still produce proper output."""
    direct_logger.enable_color = True
    assert direct_logger.colorize("", mod_alogs.apathetic_logging.ANSIColors.GREEN) == (
        f"{mod_alogs.apathetic_logging.ANSIColors.GREEN}"
        f"{mod_alogs.apathetic_logging.ANSIColors.RESET}"
    )
    direct_logger.enable_color = False
    assert (
        direct_logger.colorize("", mod_alogs.apathetic_logging.ANSIColors.GREEN) == ""
    )
