---
layout: default
title: API Reference
permalink: /api/
---

# API Reference

Complete API documentation for Apathetic Python Logger.

## Core Functions

### `get_logger() -> ApatheticLogger`

Return the registered logger instance.

Uses Python's built-in logging registry (`logging.getLogger()`) to retrieve the logger. If no logger name has been registered, attempts to auto-infer the logger name from the calling module's top-level package.

**Returns:**
- The logger instance from `logging.getLogger()` (as `ApatheticLogger` type)

**Raises:**
- `RuntimeError`: If called before a logger name has been registered and auto-inference fails.

**Example:**
```python
from apathetic_logger import get_logger, register_logger_name

register_logger_name("my_app")
logger = get_logger()
```

### `register_logger_name(logger_name: str | None = None) -> None`

Register a logger name for use by `get_logger()`.

If `logger_name` is not provided, the top-level package is automatically extracted from the calling module's `__package__` attribute.

**Parameters:**
- `logger_name` (str | None): The logger name to register. If None, auto-infers from the calling module.

**Example:**
```python
from apathetic_logger import register_logger_name

register_logger_name("my_app")
# Or let it auto-infer:
register_logger_name()  # Uses top-level package name
```

### `register_log_level_env_vars(env_vars: list[str]) -> None`

Register environment variable names to check for log level.

The environment variables will be checked in order, and the first non-empty value found will be used.

**Parameters:**
- `env_vars` (list[str]): List of environment variable names to check (e.g., `["MYAPP_LOG_LEVEL", "LOG_LEVEL"]`)

**Example:**
```python
from apathetic_logger import register_log_level_env_vars

register_log_level_env_vars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])
```

### `register_default_log_level(default_level: str) -> None`

Register the default log level to use when no other source is found.

**Parameters:**
- `default_level` (str): Default log level name (e.g., `"info"`, `"warning"`)

**Example:**
```python
from apathetic_logger import register_default_log_level

register_default_log_level("warning")
```

### `safe_log(msg: str) -> None`

Emergency logger that never fails.

This function bypasses the normal logging system and writes directly to `sys.__stderr__`. It's designed for use in error handlers where the logging system itself might be broken.

**Parameters:**
- `msg` (str): Message to log

**Example:**
```python
from apathetic_logger import safe_log

try:
    # Some operation
    pass
except Exception:
    safe_log("Critical error: logging system may be broken")
```

## Classes

### `ApatheticLogger`

Logger class for all Apathetic tools. Extends Python's standard `logging.Logger`.

#### Constructor

```python
ApatheticLogger(
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

##### `setLevel(level: int | str) -> None`

Set the logging level. Accepts both string names (case-insensitive) and numeric values.

**Parameters:**
- `level` (int | str): Log level name or numeric value

**Example:**
```python
logger.setLevel("debug")
logger.setLevel(logging.DEBUG)
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
logger.setLevel(level)
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
- Sets `ApatheticLogger` as the default logger class
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
- `color` (str): ANSI color code (e.g., `CYAN`, `RED`)
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

##### `resolve_level_name(level_name: str) -> int | None`

Resolve a log level name to its numeric value.

**Parameters:**
- `level_name` (str): Log level name (case-insensitive)

**Returns:**
- `int | None`: Numeric log level, or None if not found

#### Properties

##### `level_name: str`

Return the current effective level name (read-only).

**Example:**
```python
logger.setLevel("debug")
print(logger.level_name)  # "DEBUG"
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

- **stdout**: Used for TRACE, DEBUG, and INFO messages
- **stderr**: Used for WARNING, ERROR, and CRITICAL messages

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

- `RESET` — ANSI reset code (`\033[0m`)
- `CYAN` — Cyan color (`\033[36m`)
- `YELLOW` — Yellow color (`\033[93m`)
- `RED` — Red color (`\033[91m`)
- `GREEN` — Green color (`\033[92m`)
- `GRAY` — Gray color (`\033[90m`)

### Tag Styles

- `TAG_STYLES` — Dictionary mapping level names to (color, tag_text) tuples

### Defaults

- `DEFAULT_APATHETIC_LOG_LEVEL` — Default log level string (`"info"`)
- `DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS` — Default environment variable names (`["LOG_LEVEL"]`)

## Testing Utilities

### `TEST_TRACE(label: str, *args: Any, icon: str = "🧵") -> None`

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

### `TEST_TRACE_ENABLED: bool`

Boolean flag indicating if test tracing is enabled (checks `TEST_TRACE` environment variable).

