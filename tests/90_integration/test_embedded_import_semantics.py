# tests/90_integration/test_embedded_import_semantics.py
"""Integration tests for import semantics in built distributions.

These tests verify that when the project is built using serger or zipbundler,
the import semantics work correctly:
- apathetic_logging.ANSIColors.RED is available and correct
- Can import and use the module from built files

Tests both serger (single-file .py) and zipbundler (zipapp .pyz) builds
using the actual project configuration and source code.

These are project-specific tests that verify our code works correctly
when built with the tools (not testing the tools themselves).
"""

import importlib.util
import subprocess
import sys
import types
import zipfile
from typing import Any

import apathetic_utils as mod_utils
import pytest

from tests.utils.constants import PROJ_ROOT


def test_serger_build_import_semantics() -> None:  # noqa: PLR0915
    """Test that serger build of the project maintains correct import semantics.

    This test verifies our project code works correctly when built with serger:
    1. Builds the project using the actual .serger.jsonc config
    2. Imports the built file and verifies import semantics work correctly:
       - apathetic_logging.ANSIColors.RED is available and correct
       - Can import and use the module from the stitched file

    This verifies our project configuration and code work correctly with serger.
    """
    # --- setup ---
    expected_red_code = "\033[91m"
    expected_reset_code = "\033[0m"
    test_text = "Hello, world!"

    # Build the project's single-file script
    config_file = PROJ_ROOT / ".serger.jsonc"
    output_file = PROJ_ROOT / "dist" / "apathetic_logging.py"

    # Ensure dist directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # --- execute: build the project ---
    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "serger",
            "--config",
            str(config_file),
        ],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(
            f"Serger failed with return code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    if not output_file.exists():
        pytest.fail(f"Stitched file not created at {output_file}")

    # Import the stitched file programmatically
    # Use a unique module name to avoid conflicts with other tests
    built_module_name = f"apathetic_logging_serger_build_{id(output_file)}"
    spec = importlib.util.spec_from_file_location(
        built_module_name,
        output_file,
    )
    if spec is None or spec.loader is None:
        pytest.fail(f"Could not create import spec for {output_file}")

    # Save all apathetic_logging-related modules to restore later
    original_modules = {
        name: mod
        for name, mod in sys.modules.items()
        if name == "apathetic_logging" or name.startswith("apathetic_logging.")
    }

    stitched_module = importlib.util.module_from_spec(spec)
    sys.modules[built_module_name] = stitched_module

    # Temporarily prevent the stitched module from registering "apathetic_logging"
    # in sys.modules during execution by temporarily removing it
    temp_removed = False
    temp_module: types.ModuleType | None = None
    if "apathetic_logging" in sys.modules:
        temp_module = sys.modules.pop("apathetic_logging")
        temp_removed = True

    try:
        spec.loader.exec_module(stitched_module)
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Failed to import stitched module: {e}")
    finally:
        # Restore apathetic_logging immediately after execution
        # to prevent any side effects
        if temp_removed and temp_module is not None:
            sys.modules["apathetic_logging"] = temp_module
        elif "apathetic_logging" in sys.modules:
            # If it was added during execution, remove it
            del sys.modules["apathetic_logging"]

    # --- verify: import semantics ---
    # Verify apathetic_logging.ANSIColors.RED is available and correct
    assert hasattr(stitched_module, "apathetic_logging"), (
        "apathetic_logging should be available in stitched module"
    )

    apathetic_logging_ns = stitched_module.apathetic_logging
    assert hasattr(apathetic_logging_ns, "ANSIColors"), (
        "apathetic_logging.ANSIColors should be available"
    )

    red_color = apathetic_logging_ns.ANSIColors.RED
    reset_color = apathetic_logging_ns.ANSIColors.RESET

    assert red_color == expected_red_code, (
        f"apathetic_logging.ANSIColors.RED should be {expected_red_code!r}, "
        f"got {red_color!r}"
    )

    assert reset_color == expected_reset_code, (
        f"apathetic_logging.ANSIColors.RESET should be {expected_reset_code!r}, "
        f"got {reset_color!r}"
    )

    # Verify the values work correctly when used
    colored_string = red_color + test_text + reset_color
    expected_colored = expected_red_code + test_text + expected_reset_code
    assert colored_string == expected_colored, (
        f"Colored string should be {expected_colored!r}, got {colored_string!r}"
    )

    # Verify Logger class is available
    assert hasattr(apathetic_logging_ns, "Logger"), (
        "apathetic_logging.Logger should be available"
    )

    # Clean up - remove our test module and any submodules it might have created
    # Remove all modules that start with our built module name
    modules_to_remove = [
        name for name in list(sys.modules.keys()) if name.startswith(built_module_name)
    ]
    for name in modules_to_remove:
        del sys.modules[name]

    # Restore all original apathetic_logging-related modules
    # First, remove any that were added
    current_apathetic_modules = {
        name
        for name in sys.modules
        if name == "apathetic_logging" or name.startswith("apathetic_logging.")
    }
    for name in current_apathetic_modules:
        if name not in original_modules:
            del sys.modules[name]
    # Then restore the original ones
    for name, mod in original_modules.items():
        sys.modules[name] = mod


def test_zipapp_import_semantics(tmp_path: Any) -> None:
    """Test that zipapp builds maintain correct import semantics.

    This test verifies our project code works correctly when built with zipbundler:
    1. Builds apathetic_logging as a zipapp using zipbundler (from project root)
    2. Imports from the zipapp and verifies import semantics work correctly:
       - apathetic_logging.ANSIColors.RED is available and correct
       - Can import and use the module from zipapp format

    This verifies our project configuration and code work correctly with zipbundler.
    """
    # --- setup ---
    expected_red_code = "\033[91m"
    expected_reset_code = "\033[0m"
    test_text = "Hello, world!"

    # Use pytest's tmp_path to avoid race conditions in parallel test execution
    zipapp_file = tmp_path / f"apathetic_logging_{id(test_zipapp_import_semantics)}.pyz"

    # --- execute: build zipapp ---
    zipbundler_cmd = mod_utils.find_python_command("zipbundler")
    result = subprocess.run(  # noqa: S603
        [
            *zipbundler_cmd,
            "-o",
            str(zipapp_file),
            "-q",
            "src",
        ],
        cwd=PROJ_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(
            f"Zipbundler failed with return code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    if not zipapp_file.exists():
        pytest.fail(f"Zipapp file not created at {zipapp_file}")

    # Verify it's a valid zip file
    assert zipfile.is_zipfile(zipapp_file), "Zipapp should be a valid zip file"

    # --- execute: import from zipapp ---
    # Add zipapp to sys.path and import
    sys.path.insert(0, str(zipapp_file))

    try:
        # Import apathetic_logging from the zipapp
        import apathetic_logging  # noqa: PLC0415

        # --- verify: import semantics ---
        # Verify apathetic_logging.ANSIColors.RED is available and correct
        assert hasattr(apathetic_logging, "ANSIColors"), (
            "apathetic_logging.ANSIColors should be available"
        )

        red_color = apathetic_logging.ANSIColors.RED
        reset_color = apathetic_logging.ANSIColors.RESET

        assert red_color == expected_red_code, (
            f"apathetic_logging.ANSIColors.RED should be {expected_red_code!r}, "
            f"got {red_color!r}"
        )

        assert reset_color == expected_reset_code, (
            f"apathetic_logging.ANSIColors.RESET should be {expected_reset_code!r}, "
            f"got {reset_color!r}"
        )

        # Verify the values work correctly when used
        colored_string = red_color + test_text + reset_color
        expected_colored = expected_red_code + test_text + expected_reset_code
        assert colored_string == expected_colored, (
            f"Colored string should be {expected_colored!r}, got {colored_string!r}"
        )

        # Verify Logger class is available
        assert hasattr(apathetic_logging, "Logger"), (
            "apathetic_logging.Logger should be available"
        )

    finally:
        # Clean up sys.path
        if str(zipapp_file) in sys.path:
            sys.path.remove(str(zipapp_file))
        # Clean up imported modules
        if "apathetic_logging" in sys.modules:
            del sys.modules["apathetic_logging"]
