# tests/90_integration/test_embedded_import_semantics.py
"""Integration test for embedded mode import semantics.

This test verifies that when apathetic_logging is embedded into a stitched script
using serger, the import semantics work correctly:
- ANSIColors is NOT in the global namespace
- apathetic_logging.ANSIColors.RED is available and correct

This test only runs in singlefile mode since that's where serger stitching works.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from tests.utils.constants import PROJ_ROOT


# Mark this test to only run in singlefile mode
__runtime_mode__ = "singlefile"


def test_embedded_import_semantics() -> None:
    """Test that embedded mode import semantics work correctly.

    Does not actually run against our produced singlefile build,
    but a custom one it writes itself.

    This test:
    1. Creates temporary source files to stitch
    2. Creates a serger config file
    (that excludes __init__.py as one would when stitching with your own code)
    3. Runs serger to stitch the files together
    4. Imports the resulting stitched file programmatically
    5. Verifies ANSIColors is NOT in global namespace
    6. Verifies apathetic_logging.ANSIColors.RED is available and correct
    """
    # --- setup ---
    expected_red_code = "\033[91m"
    expected_reset_code = "\033[0m"
    test_text = "Hello, world!"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_dir = tmp_path / "source_to_join"
        source_dir.mkdir()

        # Create a dummy source file that will be stitched
        source_file = source_dir / "test_app.py"
        source_file.write_text(
            """# Test application file to be stitched with apathetic_logging
import apathetic_logging

def main(_argv: list[str] | None = None) -> int:
    # Verify ANSIColors is NOT in global namespace
    assert "ANSIColors" not in globals(), "ANSIColors should not be in global namespace"
    try:
        _ = ANSIColors  # noqa: F841
        raise AssertionError("ANSIColors should not be accessible directly")
    except NameError:
        pass  # Expected - ANSIColors is not in global namespace

    # Verify we can access it via the namespace class
    from_logging = (
        apathetic_logging.ANSIColors.RED
        + "Hello, world!"
        + apathetic_logging.ANSIColors.RESET
    )
    expected = "\\033[91mHello, world!\\033[0m"
    assert expected == from_logging
    return 0
"""
        )

        # Create serger config file
        # Include paths can be relative to config_dir or absolute
        config_file = tmp_path / ".serger-test.jsonc"
        # Use absolute path for project src (serger handles absolute paths)
        src_pattern = str(PROJ_ROOT / "src" / "apathetic_*" / "**" / "*.py")
        config = {
            "package": "test_embedded",
            "include": [
                "source_to_join/*.py",
                src_pattern,
            ],
            "exclude": [
                "__pycache__/**",
                "*.pyc",
                "**/__init__.py",
                "**/__main__.py",
            ],
            "out": "stitched_output.py",
            "module_bases": [str(PROJ_ROOT / "src")],
            "internal_imports": "keep",
            "module_mode": "multi",
        }
        config_file.write_text(json.dumps(config, indent=2))

        # --- execute ---
        # Run serger to stitch the files
        serger_script = PROJ_ROOT / "dev" / "serger.py"
        result = subprocess.run(  # noqa: S603
            [
                sys.executable,
                str(serger_script),
                "--config",
                str(config_file),
            ],
            cwd=str(tmp_path),
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

        stitched_file = tmp_path / "stitched_output.py"
        if not stitched_file.exists():
            pytest.fail(f"Stitched file not created at {stitched_file}")

        # Import the stitched file programmatically
        spec = importlib.util.spec_from_file_location("test_embedded", stitched_file)
        if spec is None or spec.loader is None:
            pytest.fail(f"Could not create import spec for {stitched_file}")

        stitched_module = importlib.util.module_from_spec(spec)
        sys.modules["test_embedded"] = stitched_module

        try:
            spec.loader.exec_module(stitched_module)
        except Exception as e:  # noqa: BLE001
            pytest.fail(f"Failed to import stitched module: {e}")

        # --- verify ---
        # Verify ANSIColors is NOT in global namespace of the stitched module
        assert "ANSIColors" not in stitched_module.__dict__, (
            "ANSIColors should not be in global namespace"
        )

        # Verify direct access to ANSIColors fails
        with pytest.raises(AttributeError):
            _ = stitched_module.ANSIColors

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

        # Verify the main function works (runs the embedded verification)
        if hasattr(stitched_module, "main"):
            main_result = stitched_module.main()
            assert main_result == 0, "main() should return 0 on success"
