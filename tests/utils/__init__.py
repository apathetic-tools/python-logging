# tests/utils/__init__.py

import apathetic_utils as mod_utils

from .constants import (
    BUNDLER_SCRIPT,
    PATCH_STITCH_HINTS,
    PROGRAM_CONFIG,
    PROGRAM_PACKAGE,
    PROGRAM_SCRIPT,
    PROJ_ROOT,
)
from .debug_logger import debug_logger_summary
from .level_validation import validate_test_level

# create_mock_superclass_test imported from apathetic_utils.testing
# patch_everywhere imported from apathetic_utils.testing
# detect_runtime_mode imported from apathetic_utils.runtime
# runtime_swap imported from apathetic_utils.runtime
from .safe_trace import make_safe_trace, safe_trace


# Re-export functions from apathetic_utils for convenience
create_mock_superclass_test = mod_utils.create_mock_superclass_test
detect_runtime_mode = mod_utils.detect_runtime_mode
find_all_packages_under_path = mod_utils.find_all_packages_under_path
find_shiv = mod_utils.find_shiv
if_ci = mod_utils.if_ci
is_ci = mod_utils.is_ci
patch_everywhere = mod_utils.patch_everywhere
runtime_swap = mod_utils.runtime_swap
strip_common_prefix = mod_utils.strip_common_prefix


__all__ = [  # noqa: RUF022
    # build_tools (from apathetic_utils.runtime)
    "find_shiv",
    # ci (from apathetic_utils.ci)
    "if_ci",
    "is_ci",
    # constants
    "BUNDLER_SCRIPT",
    "PATCH_STITCH_HINTS",
    "PROJ_ROOT",
    "PROGRAM_CONFIG",
    "PROGRAM_PACKAGE",
    "PROGRAM_SCRIPT",
    # debug_logger
    "debug_logger_summary",
    # level_validation
    "validate_test_level",
    # mock_superclass (from apathetic_utils.testing)
    "create_mock_superclass_test",
    # modules (from apathetic_utils.modules)
    "find_all_packages_under_path",
    # patch_everywhere (from apathetic_utils.testing)
    "patch_everywhere",
    # runtime_detection (from apathetic_utils.runtime)
    "detect_runtime_mode",
    # runtime_swap (from apathetic_utils.runtime)
    "runtime_swap",
    # strip_common_prefix (from apathetic_utils.paths)
    "strip_common_prefix",
    # safe_trace
    "safe_trace",
    "make_safe_trace",
]
