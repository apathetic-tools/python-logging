---
layout: base
title: API Reference
permalink: /api/
---

# API Reference

Complete API documentation for Apathetic Python Logger.

> **Note:** This library provides both **snake_case** (recommended, PEP 8 compliant) and **CamelCase** APIs. The snake_case API is documented first and recommended for new code. The CamelCase API is available for compatibility and is documented at the end of this page.
>
> For information about breaking changes, see the [Breaking Changes](#breaking-changes) section.

## New and Modified Functions (snake_case)

These functions are new to Apathetic Python Logger or have modified behavior compared to stdlib logging.

### `get_logger(logger_name: str | None = None, *, level: str | int | None = None, minimum: bool | None = None) -> Logger`

Return the registered logger instance.

Uses Python's built-in logging registry (`logging.getLogger()`) to retrieve the logger. If no logger name is provided, uses the registered logger name or attempts to auto-infer the logger name from the calling module's top-level package.

> **Breaking Change:** When `logger_name` is `None`, the logger name is now **auto-inferred** from the calling module instead of returning the root logger. To get the root logger, use `get_logger("")` instead. See [Breaking Changes](#breaking-changes) for details.

**Parameters:**
- `logger_name` (str | None): Optional logger name. If not provided, uses the registered logger name or auto-infers from the calling module. Use `""` to get the root logger.
- `level` (str | int | None): Exact log level to set on the logger. Accepts both string names (case-insensitive) and numeric values. If provided, sets the logger's level to this value. Defaults to None (no change).
- `minimum` (bool | None): If True, only set the level if it's more verbose (lower numeric value) than the current level. This prevents downgrading from a more verbose level (e.g., TRACE) to a less verbose one (e.g., DEBUG). If None, defaults to False. Only used when `level` is provided.

**Returns:**
- The logger instance from `logging.getLogger()` (as `apathetic_logging.Logger` type)

**Raises:**
- `RuntimeError`: If no logger name is provided and no logger name has been registered and auto-inference fails.
- `ValueError`: If an invalid log level is provided.

**Example:**
```python
from apathetic_logging import get_logger, register_logger

# Using registered logger name
register_logger("my_app")
logger = get_logger()  # Gets "my_app" logger

# Or specify logger name directly
logger = get_logger("my_app")  # Gets "my_app" logger

# Set exact log level
logger = get_logger("my_app", level="debug")  # Sets level to DEBUG

# Set minimum log level (only if current is less verbose)
logger = get_logger("my_app", level="info", minimum=True)  # At least INFO

# To get root logger (use "" instead of None)
logger = get_logger("")  # Returns root logger
```

### `get_logger_of_type(name: str | None, class_type: type[Logger], skip_frames: int = 1, *args: Any, level: str | int | None = None, minimum: bool | None = None, **kwargs: Any) -> Logger`

Get a logger of the specified type, creating it if necessary.

**Parameters:**
- `name` (str | None): The name of the logger to get. If None, auto-infers from the calling module. Use `""` for root logger.
- `class_type`: The logger class type to use.
- `skip_frames` (int): Number of frames to skip when inferring logger name (default: 1).
- `*args`: Additional positional arguments (for future-proofing)
- `level` (str | int | None): Exact log level to set on the logger. Accepts both string names (case-insensitive) and numeric values. If provided, sets the logger's level to this value. Defaults to None (no change).
- `minimum` (bool | None): If True, only set the level if it's more verbose (lower numeric value) than the current level. This prevents downgrading from a more verbose level (e.g., TRACE) to a less verbose one (e.g., DEBUG). If None, defaults to False. Only used when `level` is provided.
- `**kwargs`: Additional keyword arguments (for future-proofing)

**Returns:**
- A logger instance of the specified type

**Raises:**
- `ValueError`: If an invalid log level is provided.

**Example:**
```python
from apathetic_logging import Logger, get_logger_of_type

class AppLogger(Logger):
    pass

logger = get_logger_of_type("my_app", AppLogger)

# Set exact log level
logger = get_logger_of_type("my_app", AppLogger, level="debug")

# Set minimum log level
logger = get_logger_of_type("my_app", AppLogger, level="info", minimum=True)
```

### `register_logger(logger_name: str | None = None, logger_class: type[Logger] | None = None, *, target_python_version: tuple[int, int] | None = None, log_level_env_vars: list[str] | None = None, default_log_level: str | None = None, propagate: bool | None = None, compatibility_mode: bool | None = None) -> None`

Register a logger for use by `get_logger()`. This registers the logger name and extends the logging module with custom levels if needed.

If `logger_name` is not provided, the top-level package is automatically extracted from the calling module's `__package__` attribute.

If `logger_class` is provided and has an `extend_logging_module()` method, it will be called to extend the logging module with custom levels and set the logger class. If `logger_class` is not provided, the default `Logger` class will be used.

**Parameters:**
- `logger_name` (str | None): The logger name to register. If None, auto-infers from the calling module.
- `logger_class` (type[Logger] | None): Optional logger class to use. If provided and the class has an `extend_logging_module()` method, it will be called. If None, defaults to the standard `Logger` class.
- `target_python_version` (tuple[int, int] | None): Optional target Python version (major, minor) tuple. If provided, sets the target Python version in the registry permanently. Defaults to None (no change).
- `log_level_env_vars` (list[str] | None): Optional list of environment variable names to check for log level. If provided, sets the log level environment variables in the registry permanently. Defaults to None (no change).
- `default_log_level` (str | None): Optional default log level name. If provided, sets the default log level in the registry permanently. Defaults to None (no change).
- `propagate` (bool | None): Optional propagate setting. If provided, sets the propagate value in the registry permanently. If None, uses registered propagate setting or falls back to DEFAULT_PROPAGATE from constants.py. Defaults to None (no change).
- `compatibility_mode` (bool | None): Optional compatibility mode setting. If provided, sets the compatibility mode in the registry permanently. When True, restores stdlib-compatible behavior where possible (e.g., `getLogger(None)` returns root logger). If None, uses registered compatibility mode setting or defaults to False (improved behavior). Defaults to None (no change).

**Example:**
```python
from apathetic_logging import register_logger

register_logger("my_app")
# Or let it auto-infer:
register_logger()  # Uses top-level package name

# Or with a custom logger class:
from apathetic_logging import Logger

class AppLogger(Logger):
    pass

register_logger("my_app", AppLogger)

# Or with convenience parameters to configure registry settings:
register_logger(
    "my_app",
    target_python_version=(3, 10),
    log_level_env_vars=["MYAPP_LOG_LEVEL", "LOG_LEVEL"],
    default_log_level="info",
    propagate=False,
    compatibility_mode=True,  # Enable stdlib compatibility
)
```

### `register_compatibility_mode(compatibility_mode: bool) -> None`

Register the compatibility mode setting for stdlib drop-in replacement.

This sets the compatibility mode that will be used when creating loggers. If not set, the library defaults to False (improved behavior).

When `compatibility_mode` is True, restores stdlib-compatible behavior where possible (e.g., `getLogger(None)` returns root logger instead of auto-inferring).

**Parameters:**
- `compatibility_mode` (bool): Compatibility mode setting (True or False). When True, enables stdlib-compatible behavior.

**Example:**
```python
from apathetic_logging import register_compatibility_mode

register_compatibility_mode(compatibility_mode=True)
# Now getLogger(None) returns root logger (stdlib behavior)
```

### `get_compatibility_mode() -> bool`

Get the compatibility mode setting.

Returns the registered compatibility mode setting, or False (improved behavior) if not registered.

**Returns:**
- `bool`: Compatibility mode setting (True or False). Defaults to `False` if not registered.

**Example:**
```python
from apathetic_logging import get_compatibility_mode

compat_mode = get_compatibility_mode()
print(compat_mode)  # False (default)
```

### `register_log_level_env_vars(env_vars: list[str]) -> None`

Register environment variable names to check for log level.

The environment variables will be checked in order, and the first non-empty value found will be used.

**Parameters:**
- `env_vars` (list[str]): List of environment variable names to check (e.g., `["MYAPP_LOG_LEVEL", "LOG_LEVEL"]`)

**Example:**
```python
from apathetic_logging import register_log_level_env_vars

register_log_level_env_vars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])
```

### `register_default_log_level(default_level: str) -> None`

Register the default log level to use when no other source is found.

**Parameters:**
- `default_level` (str): Default log level name (e.g., `"info"`, `"warning"`)

**Example:**
```python
from apathetic_logging import register_default_log_level

register_default_log_level("warning")
```

### `register_target_python_version(version: tuple[int, int] | None) -> None`

Register the target Python version for compatibility checking.

This sets the global target Python version that the library will use when checking for feature availability. Functions requiring a newer Python version than the registered target will raise a `NotImplementedError`, even if the runtime Python version is sufficient.

If not set, the library defaults to `MIN_PYTHON_VERSION` (3.10) from constants.py.

**Parameters:**
- `version` (tuple[int, int] | None): A tuple (major, minor) representing the target Python version (e.g., `(3, 10)` for Python 3.10). If None, the registration is skipped.

**Example:**
```python
from apathetic_logging import register_target_python_version

# Target Python 3.10
register_target_python_version((3, 10))

# Target Python 3.11
register_target_python_version((3, 11))
```

**Note:** This is useful when developing on a newer Python version (e.g., 3.12) but targeting an older version (e.g., 3.10). The library will validate function calls against your target version, preventing accidental use of features that don't exist in your target environment.

### `register_propagate(*, propagate: bool | None) -> None`

Register the propagate setting for loggers.

This sets the default propagate value that will be used when creating loggers. If not set, the library defaults to `DEFAULT_PROPAGATE` (False) from constants.py.

When `propagate` is `False`, loggers do not propagate messages to parent loggers, avoiding duplicate root logs.

**Parameters:**
- `propagate` (bool | None): Propagate setting (True or False). If None, the registration is skipped.

**Example:**
```python
from apathetic_logging import register_propagate

# Enable propagation (messages propagate to parent loggers)
register_propagate(propagate=True)

# Disable propagation (default, avoids duplicate logs)
register_propagate(propagate=False)
```

### `safe_log(msg: str) -> None`

Emergency logger that never fails.

This function bypasses the normal logging system and writes directly to `sys.__stderr__`. It's designed for use in error handlers where the logging system itself might be broken.

**Parameters:**
- `msg` (str): Message to log

**Example:**
```python
from apathetic_logging import safe_log

try:
    # Some operation
    pass
except Exception:
    safe_log("Critical error: logging system may be broken")
```

### `safe_trace(label: str, *args: Any, icon: str = "🧪") -> None`

Debug tracing function for test development. Only active when `TEST_TRACE` environment variable is set.

**Parameters:**
- `label` (str): Trace label
- `*args`: Additional arguments to trace
- `icon` (str): Icon to use (default: `"🧪"`)

### `make_safe_trace(icon: str = "🧪") -> Callable`

Create a test trace function with a custom icon.

**Parameters:**
- `icon` (str): Icon to use

**Returns:**
- `Callable`: Test trace function

### `has_logger(logger_name: str) -> bool`

Check if a logger exists in the logging manager's registry.

**Parameters:**
- `logger_name` (str): The name of the logger to check

**Returns:**
- `bool`: True if the logger exists, False otherwise

### `remove_logger(logger_name: str) -> None`

Remove a logger from the logging manager's registry.

**Parameters:**
- `logger_name` (str): The name of the logger to remove

### `get_default_logger_name(logger_name: str | None = None, *, check_registry: bool = True, skip_frames: int = 1, raise_on_error: bool = False, infer: bool = True, register: bool = False) -> str | None`

Get default logger name with optional inference from caller's frame.

**Parameters:**
- `logger_name` (str | None): Explicit logger name, or None to infer (default: None)
- `check_registry` (bool): If True, check registry before inferring (default: True)
- `skip_frames` (int): Number of frames to skip (default: 1)
- `raise_on_error` (bool): If True, raise RuntimeError if logger name cannot be resolved. If False (default), return None instead
- `infer` (bool): If True (default), attempt to infer logger name from caller's frame when not found in registry. If False, skip inference
- `register` (bool): If True, store inferred name in registry. If False (default), do not modify registry. Note: Explicit names are never stored regardless of this parameter

**Returns:**
- `str | None`: Resolved logger name, or None if cannot be resolved and raise_on_error=False

**Raises:**
- `RuntimeError`: If logger name cannot be resolved and raise_on_error=True

### `get_log_level_env_vars() -> list[str]`

Get the environment variable names to check for log level.

Returns the registered environment variable names, or the default environment variables if none are registered.

**Returns:**
- `list[str]`: List of environment variable names to check for log level. Defaults to `["LOG_LEVEL"]` if not registered

### `get_default_log_level() -> str`

Get the default log level.

Returns the registered default log level, or the module default if none is registered.

**Returns:**
- `str`: Default log level name (e.g., "detail", "info"). Defaults to `"detail"` if not registered

### `get_registered_logger_name() -> str | None`

Get the registered logger name.

Returns the registered logger name, or None if no logger name has been registered. Unlike `get_default_logger_name()`, this does not perform inference - it only returns the explicitly registered value.

**Returns:**
- `str | None`: Registered logger name, or None if not registered

### `get_target_python_version() -> tuple[int, int]`

Get the target Python version.

Returns the registered target Python version, or the minimum supported version if none is registered.

**Returns:**
- `tuple[int, int]`: Target Python version as (major, minor) tuple. Defaults to `(3, 10)` if not registered

### `get_default_propagate() -> bool`

Get the default propagate setting.

Returns the registered propagate setting, or the module default if none is registered.

**Returns:**
- `bool`: Default propagate setting (True or False). Defaults to `False` if not registered

## Wrapped stdlib Functions (snake_case)

These functions are direct wrappers of Python's standard library `logging` module functions, provided with snake_case naming for PEP 8 compliance. They behave identically to their stdlib counterparts.

### Configuration Functions

- `basic_config(*args: Any, **kwargs: Any) -> None` — Wrapper for `logging.basicConfig()`
- `add_level_name(level: int, level_name: str) -> None` — Wrapper for `logging.addLevelName()`
- `get_level_name(level: int) -> str` — Wrapper for `logging.getLevelName()`
- `get_level_names_mapping() -> dict[int, str]` — Wrapper for `logging.getLevelNamesMapping()`
- `get_logger_class() -> type[logging.Logger]` — Wrapper for `logging.getLoggerClass()`
- `set_logger_class(klass: type[logging.Logger]) -> None` — Wrapper for `logging.setLoggerClass()`
- `get_log_record_factory() -> Callable` — Wrapper for `logging.getLogRecordFactory()`
- `set_log_record_factory(factory: Callable) -> None` — Wrapper for `logging.setLogRecordFactory()`
- `shutdown() -> None` — Wrapper for `logging.shutdown()`
- `disable(level: int) -> None` — Wrapper for `logging.disable()`
- `capture_warnings(capture: bool) -> None` — Wrapper for `logging.captureWarnings()`

### Module-Level Logging Functions

- `critical(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.critical()`
- `debug(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.debug()`
- `error(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.error()`
- `exception(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.exception()`
- `fatal(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.fatal()`
- `info(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.info()`
- `log(level: int, msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.log()`
- `warn(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.warn()`
- `warning(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.warning()`

### Utility Functions

- `get_handler_by_name(name: str) -> logging.Handler | None` — Wrapper for `logging.getHandlerByName()`
- `get_handler_names() -> list[str]` — Wrapper for `logging.getHandlerNames()`
- `make_log_record(name: str, level: int, fn: str, lno: int, msg: str, args: tuple, exc_info: Any) -> logging.LogRecord` — Wrapper for `logging.makeLogRecord()`
- `currentframe(*args: Any, **kwargs: Any) -> FrameType | None` — Wrapper for `logging.currentframe()`

For detailed documentation on these functions, see the [Python logging module documentation](https://docs.python.org/3/library/logging.html).

## Classes

### `Logger`

Logger class for all Apathetic tools. Extends Python's standard `logging.Logger`.

#### Constructor

```python
Logger(
    name: str,
    level: int = logging.NOTSET,
    *,
    enable_color: bool | None = None
)
```

**Parameters:**
- `name` (str): Logger name
- `level` (int): Initial log level (defaults to `logging.NOTSET`)
- `enable_color` (bool | None): Whether to enable colorized output. If None, auto-detects based on TTY and environment variables.

#### Methods

##### `set_level(level: int | str) -> None`

Set the logging level. Accepts both string names (case-insensitive) and numeric values.

**Parameters:**
- `level` (int | str): Log level name or numeric value

**Example:**
```python
logger.set_level("debug")
logger.set_level(logging.DEBUG)
```

##### `determine_log_level(*, args: argparse.Namespace | None = None, root_log_level: str | None = None) -> str`

Resolve log level from CLI → env → root config → default.

**Parameters:**
- `args` (argparse.Namespace | None): Parsed command-line arguments (checks for `args.log_level`)
- `root_log_level` (str | None): Root logger level to use as fallback

**Returns:**
- `str`: Resolved log level name (uppercase)

**Example:**
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--log-level", default="info")
args = parser.parse_args()

level = logger.determine_log_level(args=args)
logger.set_level(level)
```

##### `determine_color_enabled() -> bool` (classmethod)

Return True if colored output should be enabled.

Checks:
- `NO_COLOR` environment variable (disables colors)
- `FORCE_COLOR` environment variable (enables colors)
- TTY detection (enables colors if stdout is a TTY)

**Returns:**
- `bool`: True if colors should be enabled

##### `extend_logging_module() -> bool` (classmethod)

Extend Python's logging module with TRACE and SILENT levels.

This method:
- Sets `apathetic_logging.Logger` as the default logger class
- Adds `TRACE` and `SILENT` level names
- Adds `logging.TRACE` and `logging.SILENT` constants

**Returns:**
- `bool`: True if the extension ran, False if it was already extended

##### `trace(msg: str, *args: Any, **kwargs: Any) -> None`

Log a message at TRACE level.

**Parameters:**
- `msg` (str): Message to log
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments (e.g., `exc_info`, `stacklevel`)

##### `error_if_not_debug(msg: str, *args: Any, **kwargs: Any) -> None`

Log an error with full traceback only if debug/trace is enabled.

If debug mode is enabled, shows full exception traceback. Otherwise, shows only the error message.

**Parameters:**
- `msg` (str): Error message
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

**Example:**
```python
try:
    risky_operation()
except Exception:
    logger.error_if_not_debug("Operation failed")
```

##### `critical_if_not_debug(msg: str, *args: Any, **kwargs: Any) -> None`

Log a critical error with full traceback only if debug/trace is enabled.

Similar to `error_if_not_debug()` but logs at CRITICAL level.

##### `colorize(text: str, color: str, *, enable_color: bool | None = None) -> str`

Apply ANSI color codes to text.

**Parameters:**
- `text` (str): Text to colorize
- `color` (str): ANSI color code (e.g., `ANSIColors.CYAN`, `ANSIColors.RED`)
- `enable_color` (bool | None): Override color enablement. If None, uses instance setting.

**Returns:**
- `str`: Colorized text (or original text if colors disabled)

##### `log_dynamic(level: str | int, msg: str, *args: Any, **kwargs: Any) -> None`

Log a message at a dynamically specified level.

**Parameters:**
- `level` (str | int): Log level name or numeric value
- `msg` (str): Message to log
- `*args`: Format arguments
- `**kwargs`: Additional keyword arguments

**Example:**
```python
logger.log_dynamic("warning", "This is a warning")
logger.log_dynamic(logging.ERROR, "This is an error")
```

##### `use_level(level: str | int, *, minimum: bool = False) -> ContextManager`

Context manager to temporarily change log level.

**Parameters:**
- `level` (str | int): Log level to use
- `minimum` (bool): If True, only set the level if it's more verbose (lower numeric value) than the current level. Prevents downgrading from a more verbose level.

**Returns:**
- Context manager that restores the previous level on exit

**Example:**
```python
with logger.use_level("debug"):
    logger.debug("This will be shown")

# Level is restored after the context
```

#### Properties

##### `level: int`

Return the explicit level set on this logger (read-only).

This property is inherited from `logging.Logger` and returns the level
explicitly set on this logger. For the effective level (what's actually used,
considering inheritance), use `effective_level` instead.

**Example:**
```python
logger.set_level("debug")
print(logger.level)  # 10 (DEBUG)
```

##### `level_name: str`

Return the explicit level name set on this logger (read-only).

This property returns the name of the level explicitly set on this logger.
For the effective level name (what's actually used, considering inheritance),
use `effective_level_name` instead.

**Example:**
```python
logger.set_level("debug")
print(logger.level_name)  # "DEBUG"
```

##### `effective_level: int`

Return the effective level (what's actually used) (read-only).

This property returns the effective logging level for this logger, considering
inheritance from parent loggers. This is the preferred way to get the effective
level. Also available via `get_effective_level()` for stdlib compatibility.

**Example:**
```python
parent = get_logger("parent")
parent.set_level("info")

child = get_logger("parent.child")
print(child.level)  # 0 (NOTSET - explicit)
print(child.effective_level)  # 20 (INFO - effective, from parent)
```

##### `effective_level_name: str`

Return the effective level name (what's actually used) (read-only).

This property returns the name of the effective logging level for this logger,
considering inheritance from parent loggers. This is the preferred way to get
the effective level name. Also available via `get_effective_level_name()` for
consistency.

**Example:**
```python
parent = get_logger("parent")
parent.set_level("info")

child = get_logger("parent.child")
print(child.level_name)  # "NOTSET" (explicit)
print(child.effective_level_name)  # "INFO" (effective, from parent)
```

#### Level Access Methods

For users who prefer method-based access or stdlib compatibility, these methods
provide the same functionality as the properties above.

##### `get_level() -> int`

Return the explicit level set on this logger.

This method returns the level explicitly set on this logger (same as `level`
property). For the effective level, use `get_effective_level()` or the
`effective_level` property.

**Returns:**
- `int`: The explicit level value set on this logger

**Example:**
```python
logger.set_level("debug")
print(logger.get_level())  # 10
```

##### `get_level_name() -> str`

Return the explicit level name set on this logger.

This method returns the name of the level explicitly set on this logger (same
as `level_name` property). For the effective level name, use
`get_effective_level_name()` or the `effective_level_name` property.

**Returns:**
- `str`: The explicit level name set on this logger

**Example:**
```python
logger.set_level("debug")
print(logger.get_level_name())  # "DEBUG"
```

##### `get_effective_level() -> int`

Return the effective level (what's actually used).

This method returns the effective logging level for this logger, considering
inheritance from parent loggers. This is inherited from `logging.Logger` and
is available for stdlib compatibility. Prefer the `effective_level` property
for convenience.

**Returns:**
- `int`: The effective level value for this logger

**Example:**
```python
parent = get_logger("parent")
parent.set_level("info")

child = get_logger("parent.child")
print(child.get_effective_level())  # 20 (from parent)
```

##### `get_effective_level_name() -> str`

Return the effective level name (what's actually used).

This method returns the name of the effective logging level for this logger,
considering inheritance from parent loggers. Prefer the `effective_level_name`
property for convenience, or use this method for consistency with
`get_effective_level()`.

**Returns:**
- `str`: The effective level name for this logger

**Example:**
```python
parent = get_logger("parent")
parent.set_level("info")

child = get_logger("parent.child")
print(child.get_effective_level_name())  # "INFO" (from parent)
```

### `TagFormatter`

Custom formatter that adds colored tags to log messages.

#### Constructor

```python
TagFormatter(format: str)
```

**Parameters:**
- `format` (str): Format string (typically `"%(message)s"`)

The formatter automatically adds tags based on log level:
- `TRACE` → `[TRACE]` (gray)
- `DEBUG` → `[DEBUG]` (cyan)
- `WARNING` → `⚠️`
- `ERROR` → `❌`
- `CRITICAL` → `💥`

### `DualStreamHandler`

Stream handler that routes messages to stdout or stderr based on log level.

- **stdout**: Used for INFO messages
- **stderr**: Used for TRACE, DEBUG, WARNING, ERROR, and CRITICAL messages

#### Constructor

```python
DualStreamHandler()
```

#### Properties

##### `enable_color: bool`

Whether to enable colorized output for this handler.

## Constants

### Log Levels

- `TRACE_LEVEL` — Numeric value for TRACE level (`logging.DEBUG - 5`)
- `SILENT_LEVEL` — Numeric value for SILENT level (`logging.CRITICAL + 1`)
- `LEVEL_ORDER` — List of all log level names in order: `["trace", "debug", "info", "warning", "error", "critical", "silent"]`

### ANSI Colors

Access via `ANSIColors` class:

- `ANSIColors.RESET` — ANSI reset code (`\033[0m`)
- `ANSIColors.CYAN` — Cyan color (`\033[36m`)
- `ANSIColors.YELLOW` — Yellow color (`\033[93m`)
- `ANSIColors.RED` — Red color (`\033[91m`)
- `ANSIColors.GREEN` — Green color (`\033[92m`)
- `ANSIColors.GRAY` — Gray color (`\033[90m`)

**Example:**
```python
from apathetic_logging import ANSIColors

message = f"{ANSIColors.CYAN}Colored text{ANSIColors.RESET}"
```

### Tag Styles

- `TAG_STYLES` — Dictionary mapping level names to (color, tag_text) tuples

### Defaults

- `DEFAULT_APATHETIC_LOG_LEVEL` — Default log level string (`"info"`)
- `DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS` — Default environment variable names (`["LOG_LEVEL"]`)

## Testing Utilities

### `SAFE_TRACE(label: str, *args: Any, icon: str = "🧵") -> None`

Debug tracing function for test development. Only active when `TEST_TRACE` environment variable is set.

**Parameters:**
- `label` (str): Trace label
- `*args`: Additional arguments to trace
- `icon` (str): Icon to use (default: `"🧵"`)

### `make_test_trace(icon: str = "🧵") -> Callable`

Create a test trace function with a custom icon.

**Parameters:**
- `icon` (str): Icon to use

**Returns:**
- `Callable`: Test trace function

### `SAFE_TRACE_ENABLED: bool`

Boolean flag indicating if test tracing is enabled (checks `TEST_TRACE` environment variable).

## Breaking Changes

This section documents breaking changes that may affect existing code when upgrading.

### Logger Name Auto-Inference

**Changed in:** Current version

**Affected Function:** `get_logger(logger_name=None)`

When `get_logger(None)` is called, the logger name is now **auto-inferred** from the calling module's `__package__` attribute instead of returning the root logger.

**Migration:**
- **Old behavior:** `get_logger(None)` returned the root logger
- **New behavior:** `get_logger(None)` auto-infers the logger name from the calling module
- **To get root logger:** Use `get_logger("")` instead

**Example:**
```python
# Old (no longer works as before)
logger = get_logger(None)  # Now auto-infers name, doesn't return root

# New (to get root logger)
logger = get_logger("")  # Returns root logger
```

**Why this change:** Auto-inference makes it easier to use the logger without explicitly registering a name, while still allowing explicit root logger access via `""`.

**Compatibility Mode:** If you need stdlib-compatible behavior where `getLogger(None)` returns the root logger, you can enable compatibility mode:

```python
from apathetic_logging import register_compatibility_mode

register_compatibility_mode(compatibility_mode=True)
# Now getLogger(None) returns root logger (stdlib behavior)
```

See `register_compatibility_mode()` for more details.

## CamelCase API Reference

The CamelCase API provides compatibility with existing codebases and follows the naming conventions of Python's standard library `logging` module. All functions behave identically to their snake_case counterparts.

### New and Modified Functions (CamelCase)

- `getLogger(name: str | None = None, *, level: str | int | None = None, minimum: bool | None = None) -> Logger` — Same as `get_logger()`
- `getLoggerOfType(name: str | None, class_type: type[Logger], skip_frames: int = 1, *args: Any, level: str | int | None = None, minimum: bool | None = None, **kwargs: Any) -> Logger` — Same as `get_logger_of_type()`
- `registerLogger(logger_name: str | None = None, logger_class: type[Logger] | None = None, *, target_python_version: tuple[int, int] | None = None, log_level_env_vars: list[str] | None = None, default_log_level: str | None = None, propagate: bool | None = None, compatibility_mode: bool | None = None) -> None` — Same as `register_logger()`
- `registerLogLevelEnvVars(env_vars: list[str] | None) -> None` — Same as `register_log_level_env_vars()`
- `registerDefaultLogLevel(default_level: str | None) -> None` — Same as `register_default_log_level()`
- `registerTargetPythonVersion(version: tuple[int, int] | None) -> None` — Same as `register_target_python_version()`
- `registerCompatibilityMode(*, compatibility_mode: bool | None) -> None` — Same as `register_compatibility_mode()`
- `registerPropagate(*, propagate: bool | None) -> None` — Same as `register_propagate()`
- `safeLog(msg: str) -> None` — Same as `safe_log()`
- `safeTrace(label: str, *args: Any, icon: str = "🧪") -> None` — Same as `safe_trace()`
- `makeSafeTrace(icon: str = "🧪") -> Callable` — Same as `make_safe_trace()`
- `hasLogger(logger_name: str) -> bool` — Same as `has_logger()`
- `removeLogger(logger_name: str) -> None` — Same as `remove_logger()`
- `getDefaultLoggerName(logger_name: str | None = None, *, check_registry: bool = True, skip_frames: int = 1, raise_on_error: bool = False, infer: bool = True, register: bool = False) -> str | None` — Same as `get_default_logger_name()`
- `getLogLevelEnvVars() -> list[str]` — Same as `get_log_level_env_vars()`
- `getDefaultLogLevel() -> str` — Same as `get_default_log_level()`
- `getRegisteredLoggerName() -> str | None` — Same as `get_registered_logger_name()`
- `getTargetPythonVersion() -> tuple[int, int]` — Same as `get_target_python_version()`
- `getCompatibilityMode() -> bool` — Same as `get_compatibility_mode()`
- `getDefaultPropagate() -> bool` — Same as `get_default_propagate()`

### Wrapped stdlib Functions (CamelCase)

All standard library `logging` module functions are available with their original CamelCase names:

- `basicConfig(*args: Any, **kwargs: Any) -> None` — Wrapper for `logging.basicConfig()`
- `addLevelName(level: int, level_name: str) -> None` — Wrapper for `logging.addLevelName()`
- `getLevelName(level: int) -> str` — Wrapper for `logging.getLevelName()`
- `getLevelNamesMapping() -> dict[int, str]` — Wrapper for `logging.getLevelNamesMapping()`
- `getLoggerClass() -> type[logging.Logger]` — Wrapper for `logging.getLoggerClass()`
- `setLoggerClass(klass: type[logging.Logger]) -> None` — Wrapper for `logging.setLoggerClass()`
- `getLogRecordFactory() -> Callable` — Wrapper for `logging.getLogRecordFactory()`
- `setLogRecordFactory(factory: Callable) -> None` — Wrapper for `logging.setLogRecordFactory()`
- `shutdown() -> None` — Wrapper for `logging.shutdown()`
- `disable(level: int) -> None` — Wrapper for `logging.disable()`
- `captureWarnings(capture: bool) -> None` — Wrapper for `logging.captureWarnings()`
- `critical(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.critical()`
- `debug(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.debug()`
- `error(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.error()`
- `exception(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.exception()`
- `fatal(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.fatal()`
- `info(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.info()`
- `log(level: int, msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.log()`
- `warn(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.warn()`
- `warning(msg: str, *args: Any, **kwargs: Any) -> None` — Wrapper for `logging.warning()`
- `getHandlerByName(name: str) -> logging.Handler | None` — Wrapper for `logging.getHandlerByName()`
- `getHandlerNames() -> list[str]` — Wrapper for `logging.getHandlerNames()`
- `makeLogRecord(name: str, level: int, fn: str, lno: int, msg: str, args: tuple, exc_info: Any) -> logging.LogRecord` — Wrapper for `logging.makeLogRecord()`
- `currentframe(*args: Any, **kwargs: Any) -> FrameType | None` — Wrapper for `logging.currentframe()`

For detailed documentation, see the corresponding snake_case functions above or the [Python logging module documentation](https://docs.python.org/3/library/logging.html).
