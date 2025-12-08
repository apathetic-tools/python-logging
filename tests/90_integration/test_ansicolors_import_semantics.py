# tests/90_integration/test_ansicolors_import_semantics.py
"""Integration tests for import semantics in different runtime modes.

This test explicitly verifies that import semantics work correctly in both
package mode (from src/) and stitched mode (from dist/apathetic_logging.py).

The test uses ANSIColors.RED as an example to verify that:
- Imports from apathetic_logging work correctly
- Exported constants are accessible
- Values are correct regardless of runtime mode

This replicates the verification done in mode_verify/package_example/package_run.py
and mode_verify/stitched_example/stitched_run.py, but as a pytest integration test
that runs in both runtime modes.
"""

import apathetic_logging as mod_alogs


def test_import_semantics_work_in_all_runtime_modes() -> None:
    """Test that import semantics work correctly in package and stitched modes.

    This test verifies import semantics by importing and using ANSIColors.RED
    as an example. The test runs in the current runtime mode (package by default,
    stitched when RUNTIME_MODE=stitched).

    The key verification is that imports work correctly regardless of whether
    the module is loaded from src/ (package) or dist/apathetic_logging.py
    (stitched).
    """
    # --- setup ---
    # Expected ANSI escape code for RED (used as example to verify import semantics)
    expected_red_code = "\033[91m"
    expected_reset_code = "\033[0m"
    test_text = "Hello, world!"

    # --- execute ---
    # Verify import semantics: ANSIColors should be accessible via the module
    # This tests that the import mechanism works correctly in the current runtime mode
    red_color = mod_alogs.ANSIColors.RED
    reset_color = mod_alogs.ANSIColors.RESET

    # Build colored string (replicating mode_verify test pattern)
    # This verifies the imported value is correct and usable
    colored_string = red_color + test_text + reset_color
    expected_colored = expected_red_code + test_text + expected_reset_code

    # --- verify ---
    # Verify the imported value is correct (validates import semantics worked)
    assert red_color == expected_red_code, (
        f"ANSIColors.RED should be {expected_red_code!r}, got {red_color!r}"
    )

    assert reset_color == expected_reset_code, (
        f"ANSIColors.RESET should be {expected_reset_code!r}, got {reset_color!r}"
    )

    # Verify the imported values work correctly when used
    assert colored_string == expected_colored, (
        f"Colored string should be {expected_colored!r}, got {colored_string!r}"
    )
