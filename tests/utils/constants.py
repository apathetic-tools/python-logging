# tests/utils/constants.py
"""Package metadata constants for test utilities."""

from pathlib import Path


# Project root directory (tests/utils/constants.py -> project root)
PROJ_ROOT = Path(__file__).resolve().parent.parent.parent.resolve()

# Package name used for imports and module paths
PROGRAM_PACKAGE = "apathetic_logging"

# Script name for the single-file distribution
PROGRAM_SCRIPT = "apathetic_logging"

# Config file name (used by patch_everywhere for stitch detection)
PROGRAM_CONFIG = "apathetic_logging"

# Path to the bundler script (relative to project root)
BUNDLER_SCRIPT = "dev/serger.py"

# Stitch hints for patch_everywhere (used to identify stitched modules)
PATCH_STITCH_HINTS = {"/dist/", "standalone", f"{PROGRAM_SCRIPT}.py"}
