# tests/10_lint/test_lint__camelcase_functions.py
"""Custom lint rule: Enforce camelCase naming for functions and methods.

This test acts as a "lazy person's linter" since ruff doesn't support enforcing
camelCase for function and method names. It enforces that all public functions
and methods in the source code use camelCase naming convention.

Rule: All public function and method names must be camelCase:
  - First letter must be lowercase
  - Subsequent words must be capitalized
  - No underscores between words

Examples:
  ✅ getLogger
  ✅ getLoggerOfType
  ✅ ensureHandlers
  ✅ setLevel
  ✅ determineColorEnabled
  ❌ get_logger (snake_case)
  ❌ GetLogger (PascalCase)
  ❌ get_logger_of_type (snake_case)

Exceptions:
  - Private functions/methods (starting with `_`) are excluded
  - Special methods (starting and ending with `__`) are excluded
  - Test functions (in test files) are excluded
"""

import ast
import re
from pathlib import Path

from tests.utils.constants import PROJ_ROOT


def _is_camelcase(name: str) -> bool:
    """Check if a name follows camelCase convention.

    camelCase means:
    - First character is lowercase
    - Subsequent words start with uppercase
    - No underscores
    - No consecutive uppercase letters (except at start of words)

    Args:
        name: The name to check

    Returns:
        True if the name is camelCase, False otherwise
    """
    # Empty string is not valid
    if not name:
        return False

    # Must start with lowercase letter
    if not name[0].islower():
        return False

    # No underscores allowed
    if "_" in name:
        return False

    # Check for valid camelCase pattern:
    # - Starts with lowercase letter
    # - Then any lowercase letters/numbers
    # - Then zero or more groups of (uppercase letter + lowercase letters/numbers)
    # This allows: getLogger, getLoggerOfType, ensureHandlers, format, emit, etc.
    pattern = r"^[a-z][a-z0-9]*([A-Z][a-z0-9]*)*$"
    return bool(re.match(pattern, name))


def _is_private(name: str) -> bool:
    """Check if a name is private (starts with underscore)."""
    return name.startswith("_")


def _is_special_method(name: str) -> bool:
    """Check if a name is a special method (starts and ends with double underscore)."""
    return name.startswith("__") and name.endswith("__")


def _should_check_name(name: str) -> bool:
    """Determine if a function/method name should be checked.

    We skip:
    - Private names (starting with `_`)
    - Special methods (starting and ending with `__`)

    Args:
        name: The function or method name

    Returns:
        True if the name should be checked for camelCase, False otherwise
    """
    if _is_private(name):
        return False
    return not _is_special_method(name)


class CamelCaseChecker(ast.NodeVisitor):
    """AST visitor to check function and method names are camelCase."""

    def __init__(self, file_path: Path) -> None:
        """Initialize the checker.

        Args:
            file_path: Path to the file being checked (for error reporting)
        """
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []  # (line, name, type)
        self.function_depth = 0  # Track nesting depth to skip nested functions
        self._class_depth = 0  # Track class nesting depth

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition."""
        # Only check top-level functions and class methods, not nested functions
        is_top_level_or_method = self.function_depth == 0
        if (
            is_top_level_or_method
            and _should_check_name(node.name)
            and not _is_camelcase(node.name)
        ):
            # Determine if it's a method (inside a class) or top-level function
            func_type = "method" if self._is_inside_class() else "function"
            self.violations.append((node.lineno, node.name, func_type))
        # Track nesting and visit children
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition."""
        # Only check top-level functions and class methods, not nested functions
        is_top_level_or_method = self.function_depth == 0
        if (
            is_top_level_or_method
            and _should_check_name(node.name)
            and not _is_camelcase(node.name)
        ):
            # Determine if it's a method (inside a class) or top-level function
            is_inside_class = self._is_inside_class()
            func_type = "async method" if is_inside_class else "async function"
            self.violations.append((node.lineno, node.name, func_type))
        # Track nesting and visit children
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition."""
        # Track that we're inside a class for method detection
        self._class_depth += 1
        self.generic_visit(node)
        self._class_depth -= 1

    def _is_inside_class(self) -> bool:
        """Check if we're currently inside a class definition."""
        return getattr(self, "_class_depth", 0) > 0


def _check_file(file_path: Path) -> list[tuple[int, str, str]]:
    """Check a single Python file for camelCase violations.

    Args:
        file_path: Path to the Python file to check

    Returns:
        List of violations as (line_number, name, type) tuples
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        # Skip files with syntax errors (they'll be caught by other tools)
        return []

    checker = CamelCaseChecker(file_path)
    checker.visit(tree)
    return checker.violations


def test_camelcase_functions_and_methods() -> None:
    """Enforce camelCase naming for all public functions and methods.

    This is a custom lint rule implemented as a pytest test because ruff doesn't
    support enforcing camelCase for function and method names. It ensures all
    public functions and methods in the source code follow camelCase convention.

    Rule: All public function and method names must be camelCase:
      - First letter must be lowercase
      - Subsequent words must be capitalized
      - No underscores between words

    Examples:
      ✅ getLogger
      ✅ getLoggerOfType
      ✅ ensureHandlers
      ✅ setLevel
      ✅ determineColorEnabled
      ❌ get_logger (snake_case)
      ❌ GetLogger (PascalCase)
      ❌ get_logger_of_type (snake_case)

    Exceptions:
      - Private functions/methods (starting with `_`) are excluded
      - Special methods (starting and ending with `__`) are excluded
      - Only checks `src/` directory (not tests, dist, etc.)
    """
    src_dir = PROJ_ROOT / "src"
    if not src_dir.exists():
        msg = f"Source directory not found: {src_dir}"
        raise AssertionError(msg)

    all_violations: list[tuple[Path, int, str, str]] = []

    # Check all Python files in src/
    for py_file in src_dir.rglob("*.py"):
        violations = _check_file(py_file)
        for line_num, name, func_type in violations:
            all_violations.append((py_file, line_num, name, func_type))

    if all_violations:
        print("\n❌ Function and method names must use camelCase convention:")
        print(
            "\nRule: All public function and method names must be camelCase"
            "\n  - First letter must be lowercase"
            "\n  - Subsequent words must be capitalized"
            "\n  - No underscores between words"
        )
        print(
            "\nExamples:"
            "\n  ✅ getLogger"
            "\n  ✅ getLoggerOfType"
            "\n  ✅ ensureHandlers"
            "\n  ✅ setLevel"
            "\n  ✅ determineColorEnabled"
            "\n  ❌ get_logger (snake_case)"
            "\n  ❌ GetLogger (PascalCase)"
            "\n  ❌ get_logger_of_type (snake_case)"
        )
        print(
            "\nExceptions (not checked):"
            "\n  - Private functions/methods (starting with `_`)"
            "\n  - Special methods (starting and ending with `__`)"
        )
        print("\nViolations found:")
        for file_path, line_num, name, func_type in all_violations:
            relative_path = file_path.relative_to(PROJ_ROOT)
            print(f"\n  - {relative_path}:{line_num}")
            print(f"    {func_type}: `{name}`")
            print(f"    Fix: Rename to camelCase (e.g., `{_suggest_camelcase(name)}`)")
        xmsg = (
            f"{len(all_violations)} function/method name(s) violate camelCase"
            " convention. All public functions and methods must use camelCase"
            " naming (first letter lowercase, subsequent words capitalized,"
            " no underscores)."
        )
        raise AssertionError(xmsg)


def _suggest_camelcase(name: str) -> str:
    """Suggest a camelCase version of a name.

    This is a simple heuristic that converts snake_case to camelCase.
    For more complex cases, manual fixing may be needed.

    Args:
        name: The original name

    Returns:
        A suggested camelCase version
    """
    # Split on underscores and capitalize appropriately
    parts = name.split("_")
    if not parts:
        return name

    # First part lowercase, rest capitalized
    result = parts[0].lower()
    for part in parts[1:]:
        if part:
            result += part.capitalize()

    return result
