---
layout: base
title: API Reference
permalink: /api/
---

# API Reference

Complete API documentation for Apathetic Python Logger.

> **Note:** This library uses **camelCase** naming to match Python's standard library `logging` module conventions.
>
> By default, this library provides improved behavior with enhancements over the standard library. For stdlib-compatible behavior with no breaking changes, enable [Compatibility Mode](#compatibility-mode).


## Quick Reference: `apathetic_logging` Module Functions

\* Improvements over Stdlib `logging`  
\† Ported or fallthrough to Stdlib `logging`

### Setup

| Function | Summary |
|-----------|---------|
| [`basicConfig()`<sup>†</sup>](#basicconfig) | Configure logging system |
| [`getLevelName()`<sup>*</sup>](#getlevelname) / [`getLevelNameStr()`](#getlevelnamestr) | Convert a log level to its string name (always returns string) |
| [`getLevelNumber()`](#getlevelnumber) | Convert a log level name to its numeric value |
| [`getLogger()`<sup>*</sup>](#getlogger) | Return the registered logger instance (auto-infers name when None) |
| [`getLoggerOfType()`](#getloggeroftype) | Get a logger of the specified type, creating it if necessary |
| [`getRootLogger()`](#getrootlogger) | Return the root logger instance (primary way to access root logger) |
| [`registerLogger()`](#registerlogger) | Register a logger for use by `getLogger()` |
| [`setLoggerClass()`<sup>†</sup>](#setloggerclass) | Set the class to be used when instantiating a logger |
| [`shutdown()`<sup>†</sup>](#shutdown) | Perform an orderly shutdown of the logging system |

### Logging Messages (to *Root Logger*)

| Function | Summary |
|-----------|---------|
| [`brief()`](#brief) | Log a message with severity BRIEF |
| [`critical()`<sup>†</sup>](#critical) / [`fatal()`<sup>†</sup>](#fatal) | Log a message with severity CRITICAL |
| [`debug()`<sup>†</sup>](#debug) | Log a message with severity DEBUG |
| [`detail()`](#detail) | Log a message with severity DETAIL |
| [`error()`<sup>†</sup>](#error) / [`exception()`<sup>†</sup>](#exception) | Log a message with severity ERROR |
| [`info()`<sup>†</sup>](#info) | Log a message with severity INFO |
| [`log()`<sup>†</sup>](#log) | Log a message with an explicit level |
| [`test()`](#test) | Log a message with severity TEST |
| [`trace()`<sup>†</sup>](#trace) | Log a message with severity TRACE |
| [`warning()`<sup>†</sup>](#warning) / [`warn()`<sup>†</sup>](#warn) | Log a message with severity WARNING |

### Logging Extras
| [`captureWarnings()`<sup>†</sup>](#capturewarnings) | Capture warnings issued by the warnings module |
| [`currentframe()`<sup>†</sup>](#currentframe) | Return the frame object for the caller's stack frame |
| [`disable()`<sup>†</sup>](#disable) | Disable all logging calls of severity 'level' and below |


### Safety Logging
For when the framework isn't initialzied yet, or you're troubleshooting.

| Function | Summary |
|-----------|---------|
| [`makeSafeTrace()`](#makesafetrace) | Create a test trace function with a custom icon |
| [`safeLog()`](#safelog) | Emergency logger that never fails |
| [`safeTrace()`](#safetrace) | Debug tracing function for test development |


### Settings Registry

The library provides a registry system for configuring default settings that apply when creating loggers or performing operations. These settings allow you to bypass needing to pass parameters to every function call.

| Function | Purpose | Default Value |
|----------|---------|---------------|
| [`registerCompatibilityMode()`](#registercompatibilitymode) / [`getCompatibilityMode()`](#getcompatibilitymode) | Enable stdlib-compatible behavior | `False` (improved behavior) |
| [`registerDefaultLogLevel()`](#registerdefaultloglevel) / [`getDefaultLogLevel()`](#getdefaultloglevel) | Default log level when no other source found | `"INFO"` |
| [`registerLogLevelEnvVars()`](#registerloglevelenvvars) / [`getLogLevelEnvVars()`](#getloglevelenvvars) | Environment variables to check for log level | `["LOG_LEVEL"]` |
| [`registerLogger()`](#registerlogger) /  | Register a logger for use by `getLogger()` |
| [`registerPortHandlers()`](#registerporthandlers) | Whether to port handlers when replacing loggers | `True` |
| [`registerPortLevel()`](#registerportlevel) | Whether to port level when replacing loggers | `True` |
| [`registerPropagate()`](#registerpropagate) / [`getDefaultPropagate()`](#getdefaultpropagate) | Default propagate setting for loggers | `False` |
| [`registerReplaceRootLogger()`](#registerreplacerootlogger) | Whether to replace root logger if not correct type | `True` |
| [`registerTargetPythonVersion()`](#registertargetpythonversion) / [`getTargetPythonVersion()`](#gettargetpythonversion) | Target Python version for compatibility checking | `(3, 10)` |

### Internal
For writing library extensions.

| Function | Summary |
|-----------|---------|
| [`addLevelName()`<sup>†</sup>](#addlevelname) | Associate a level name with a numeric level |
| [`getDefaultLoggerName()`](#getdefaultloggername) | Get default logger name with optional inference from caller's frame |
| [`getHandlerByName()`<sup>†</sup>](#gethandlerbyname) | 3.12+: Get a handler with the specified name |
| [`getHandlerNames()`<sup>†</sup>](#gethandlernames) | 3.12+: Return all known handler names |
| [`getLevelNamesMapping()`<sup>†</sup>](#getlevelnamesmapping) | 3.11+: Get mapping of level names to numeric values |
| [`getLoggerClass()`<sup>†</sup>](#getloggerclass) | Return the class to be used when instantiating a logger |
| [`getLogRecordFactory()`<sup>†</sup>](#getlogrecordfactory) | Return the factory function used to create LogRecords |
| [`getRegisteredLoggerName()`](#getregisteredloggername) | Get the registered logger name |
| [`getTargetPythonVersion()`](#gettargetpythonversion) | Get the target Python version |
| [`hasLogger()`](#haslogger) | Check if a logger exists in the logging manager's registry |
| [`makeLogRecord()`<sup>†</sup>](#makelogrecord) | Create a LogRecord from the given parameters |
| [`removeLogger()`](#removelogger) | Remove a logger from the logging manager's registry |
| [`setLogRecordFactory()`<sup>†</sup>](#setlogrecordfactory) | Set the factory function used to create LogRecords |


## Quick Reference: `apathetic_logging.Logger` Class Methods

\* Improvements over Stdlib `logging.Logger`  
\† Ported or fallthrough to Stdlib `logging.Logger`. See the [Python logging.Logger documentation](https://docs.python.org/3/library/logging.html#logging.Logger) for the complete list. 

### Setup

| Method | Summary |
|--------|---------|
| [`determineColorEnabled()`](#determinecolorenabled) | Return True if colored output should be enabled (classmethod) |
| [`determineLogLevel()`](#determineloglevel) | Resolve log level from CLI → env → root config → default |
| [`effectiveLevel`](#effectivelevel) | Return the effective level (what's actually used) (property) |
| [`effectiveLevelName`](#effectivelevelname) | Return the effective level name (what's actually used) (property) |
| [`extendLoggingModule()`](#extendloggingmodule) | Extend Python's logging module with TRACE and SILENT levels (classmethod) |
| [`getEffectiveLevelName()`](#geteffectivelevelname) | Return the effective level name (what's actually used) |
| [`getLevel()`](#getlevel) | Return the explicit level set on this logger |
| [`getLevelName()`](#getlevelname) | Return the explicit level name set on this logger |
| [`levelName`](#levelname) | Return the explicit level name set on this logger (property) |
| [`setLevel()`<sup>*</sup>](#setlevel) | Set the logging level (accepts string names and has minimum parameter) |
| [`setLevelInherit()`](#setlevelinherit) | Set logger to inherit level from parent |
| [`setLevelMinimum()`](#setlevelminimum) | Set level only if it's more verbose than current level |
| [`useLevel()`](#uselevel) | Context manager to temporarily change log level |
| [`useLevelMinimum()`](#uselevelminimum) | Context manager to temporarily change log level (only if more verbose) |


### Advanced Setup
- [`getChildren()`<sup>†</sup>](#getchildren) - 3.12+: Return a set of loggers that are immediate children of this logger
| [`setLevelAndPropagate()`](#setlevelandpropagate) | Set level and propagate together with smart defaults |
| [`useLevelAndPropagate()`](#uselevelandpropagate) | Context manager to temporarily set level and propagate together |
| [`usePropagate()`](#usepropagate) | Context manager to temporarily change propagate setting |

### Logging Levels

| Method | Summary |
|--------|---------|
| [`brief()`](#brief) | Log a message at BRIEF level |
| [`criticalIfNotDebug()`](#criticalifnotdebug) | Log a critical error with full traceback only if debug/trace is enabled |
| [`detail()`](#detail) | Log a message at DETAIL level |
| [`errorIfNotDebug()`](#errorifnotdebug) | Log an error with full traceback only if debug/trace is enabled |
| [`logDynamic()`](#logdynamic) | Log a message at a dynamically specified level |
| [`test()`](#test) | Log a message at TEST level |
| [`trace()`](#trace) | Log a message at TRACE level |

### Logging Extras
| [`colorize()`](#colorize) | Apply ANSI color codes to text |

### Internal

| Method | Summary |
|--------|---------|
| [`_log()`<sup>*</sup>](#_log) | Log a message with the specified level (automatically ensures handlers) |
| [`addLevelName()`<sup>*</sup>](#addlevelname) | Associate a level name with a numeric level (validates level > 0) (staticmethod) |
| [`ensureHandlers()`](#ensurehandlers) | Ensure handlers are attached to this logger |
| [`validateLevel()`](#validatelevel) | Validate that a level value is positive (> 0) (staticmethod) |

## `apathetic_logging` Function Reference

### addLevelName

```python
addLevelName(level: int, level_name: str) -> None
```

Wrapper for `logging.addLevelName()`. Associate a level name with a numeric level.

For detailed documentation, see the [Python logging.addLevelName() documentation](https://docs.python.org/3/library/logging.html#logging.addLevelName).

### basicConfig

```python
basicConfig(*args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.basicConfig()`. Configure the logging system.

For detailed documentation, see the [Python logging.basicConfig() documentation](https://docs.python.org/3/library/logging.html#logging.basicConfig).

### brief

```python
brief(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message with severity BRIEF on the root logger.

BRIEF is less detailed than INFO. This function gets an `apathetic_logging.Logger` instance (ensuring the root logger is an apathetic logger) and calls its `brief()` method.

If the logger has no handlers, `basicConfig()` is automatically called to add a console handler with a pre-defined format.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments for message formatting |
| `**kwargs` | Any | Additional keyword arguments (e.g., `exc_info`, `stacklevel`) |

**Example:**
```python
import apathetic_logging

# Log a brief message
apathetic_logging.brief("brief information: %s", summary)
```

### captureWarnings

```python
captureWarnings(capture: bool, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.captureWarnings()`. Redirect warnings to the logging package.

If `capture` is `True`, redirect all warnings issued by the `warnings` module to the logging package. If `capture` is `False`, ensure that warnings are not redirected to logging but to their original destinations.

For detailed documentation, see the [Python logging.captureWarnings() documentation](https://docs.python.org/3/library/logging.html#logging.captureWarnings).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `capture` | bool | If True, redirect warnings to logging. If False, restore original warning behavior. |
| `*args` | Any | Additional positional arguments (passed through to stdlib) |
| `**kwargs` | Any | Additional keyword arguments (passed through to stdlib) |

**Example:**
```python
import apathetic_logging
import warnings

# Capture warnings and log them
apathetic_logging.captureWarnings(True)
warnings.warn("This warning will be logged")

# Stop capturing warnings
apathetic_logging.captureWarnings(False)
```

### critical

```python
critical(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.critical()`. Log a message with severity CRITICAL.

For detailed documentation, see the [Python logging.critical() documentation](https://docs.python.org/3/library/logging.html#logging.critical).

### currentframe

```python
currentframe(*args: Any, **kwargs: Any) -> FrameType | None
```

Wrapper for `logging.currentframe()`. Return the frame object for the caller's stack frame.

For detailed documentation, see the [Python logging.currentframe() documentation](https://docs.python.org/3/library/logging.html#logging.currentframe).

### debug

```python
debug(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.debug()`. Log a message with severity DEBUG.

For detailed documentation, see the [Python logging.debug() documentation](https://docs.python.org/3/library/logging.html#logging.debug).

### detail

```python
detail(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message with severity DETAIL on the root logger.

DETAIL is more detailed than INFO. This function gets an `apathetic_logging.Logger` instance (ensuring the root logger is an apathetic logger) and calls its `detail()` method.

If the logger has no handlers, `basicConfig()` is automatically called to add a console handler with a pre-defined format.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments for message formatting |
| `**kwargs` | Any | Additional keyword arguments (e.g., `exc_info`, `stacklevel`) |

**Example:**
```python
import apathetic_logging

# Log a detail message
apathetic_logging.detail("Additional detail: %s", information)
```

### disable

```python
disable(level: int) -> None
```

Wrapper for `logging.disable()`. Disable all logging calls of severity 'level' and below.

For detailed documentation, see the [Python logging.disable() documentation](https://docs.python.org/3/library/logging.html#logging.disable).

### error

```python
error(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.error()`. Log a message with severity ERROR.

For detailed documentation, see the [Python logging.error() documentation](https://docs.python.org/3/library/logging.html#logging.error).

### exception

```python
exception(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.exception()`. Log a message with severity ERROR with exception info.

For detailed documentation, see the [Python logging.exception() documentation](https://docs.python.org/3/library/logging.html#logging.exception).

### fatal

```python
fatal(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.fatal()`. Log a message with severity CRITICAL.

For detailed documentation, see the [Python logging.fatal() documentation](https://docs.python.org/3/library/logging.html#logging.fatal).

### info

```python
info(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.info()`. Log a message with severity INFO on the root logger.

If the logger has no handlers, `basicConfig()` is automatically called to add a console handler with a pre-defined format.

For detailed documentation, see the [Python logging.info() documentation](https://docs.python.org/3/library/logging.html#logging.info).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments for message formatting |
| `**kwargs` | Any | Additional keyword arguments (e.g., `exc_info`, `stacklevel`) |

**Example:**
```python
import apathetic_logging

# Log an info message
apathetic_logging.info("Application started")
apathetic_logging.info("Processing %d items", count)
```

### log

```python
log(level: int, msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.log()`. Log a message with an explicit level on the root logger.

If the logger has no handlers, `basicConfig()` is automatically called to add a console handler with a pre-defined format.

For detailed documentation, see the [Python logging.log() documentation](https://docs.python.org/3/library/logging.html#logging.log).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int | The numeric logging level (e.g., `logging.DEBUG`, `logging.INFO`) |
| `msg` | str | Message to log |
| `*args` | Any | Format arguments for message formatting |
| `**kwargs` | Any | Additional keyword arguments (e.g., `exc_info`, `stacklevel`) |

**Example:**
```python
import apathetic_logging
import logging

# Log with explicit level
apathetic_logging.log(logging.INFO, "Info message")
apathetic_logging.log(logging.DEBUG, "Debug message: %s", variable)
apathetic_logging.log(logging.WARNING, "Warning: %d items processed", count)
```

### getCompatibilityMode

```python
getCompatibilityMode() -> bool
```

Get the compatibility mode setting.

Returns the registered compatibility mode setting, or `False` (improved behavior) if not registered.

**Returns:**
- `bool`: Compatibility mode setting. `False` means improved behavior with enhancements (default). `True` means stdlib-compatible behavior with no breaking changes.

**Example:**
```python
from apathetic_logging import getCompatibilityMode

compat_mode = getCompatibilityMode()
print(compat_mode)  # False (default: improved behavior)
```

### getDefaultLogLevel

```python
getDefaultLogLevel() -> str
```

Get the default log level.

Returns the registered default log level, or the default value if not registered.

**Returns:**
- `str`: Default log level name

**Example:**
```python
from apathetic_logging import getDefaultLogLevel

default_level = getDefaultLogLevel()
print(default_level)  # "INFO" (default)
```

### getDefaultLoggerName

```python
getDefaultLoggerName(
    logger_name: str | None = None,
    *,
    check_registry: bool = True,
    skip_frames: int = 1,
    raise_on_error: bool = False,
    infer: bool = True,
    register: bool = False
) -> str | None
```

Get default logger name with optional inference from caller's frame.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `logger_name` | str \| None | Explicit logger name, or None to infer (default: None) |
| `check_registry` | bool | If True, check registry before inferring (default: True) |
| `skip_frames` | int | Number of frames to skip (default: 1) |
| `raise_on_error` | bool | If True, raise RuntimeError if logger name cannot be resolved. If False (default), return None instead |
| `infer` | bool | If True (default), attempt to infer logger name from caller's frame when not found in registry. If False, skip inference |
| `register` | bool | If True, store inferred name in registry. If False (default), do not modify registry. Note: Explicit names are never stored regardless of this parameter |

**Returns:**
- `str | None`: Resolved logger name, or None if cannot be resolved and raise_on_error=False

**Raises:**
- `RuntimeError`: If logger name cannot be resolved and raise_on_error=True

### getDefaultPropagate

```python
getDefaultPropagate() -> bool
```

Get the default propagate setting.

Returns the registered propagate setting, or the default value if not registered.

**Returns:**
- `bool`: Default propagate setting

**Example:**
```python
from apathetic_logging import getDefaultPropagate

propagate = getDefaultPropagate()
print(propagate)  # False (default)
```

### getHandlerByName

```python
getHandlerByName(name: str) -> logging.Handler | None
```

**Requires Python 3.12+**

Wrapper for `logging.getHandlerByName()`. Get a handler with the specified name.

For detailed documentation, see the [Python logging.getHandlerByName() documentation](https://docs.python.org/3.12/library/logging.html#logging.getHandlerByName).

### getHandlerNames

```python
getHandlerNames() -> list[str]
```

**Requires Python 3.12+**

Wrapper for `logging.getHandlerNames()`. Return all known handler names.

For detailed documentation, see the [Python logging.getHandlerNames() documentation](https://docs.python.org/3.12/library/logging.html#logging.getHandlerNames).

### getLevelName

```python
getLevelName(level: int | str, *, strict: bool = False) -> str | int
```

Return the textual or numeric representation of a logging level.

Behavior depends on compatibility mode (set via `registerCompatibilityMode()`):

**Compatibility mode enabled (`compat_mode=True`):**
- Behaves like stdlib `logging.getLevelName()` (bidirectional)
- Returns `str` for integer input, `int` for string input (known levels)
- Returns `"Level {level}"` string for unknown levels
- Value-add: Uppercases string inputs before processing (case-insensitive)

**Compatibility mode disabled (`compat_mode=False`, default):**
- Accepts both integer and string input
- For string input: uppercases and returns the string (value-add, no conversion)
- For integer input: returns level name as string (never returns `int`)
- Optional strict mode to raise `ValueError` for unknown integer levels

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int \| str | Log level as integer or string name |
| `strict` | bool | If True, raise ValueError for unknown levels. If False (default), returns "Level {level}" format for unknown integer levels (matching stdlib behavior). Only used when compatibility mode is disabled and level is an integer. |

**Returns:**
- Compatibility mode enabled: `str | int` (bidirectional like stdlib)
- Compatibility mode disabled: `str` (always string; string input is uppercased and returned, int input is converted to name)

**Raises:**
- `ValueError`: If strict=True and level is an integer that cannot be resolved to a known level name

**Example:**
```python
from apathetic_logging import getLevelName, getLevelNumber, registerCompatibilityMode

# Compatibility mode enabled (stdlib-like behavior):
registerCompatibilityMode(compat_mode=True)
getLevelName(10)  # "DEBUG" (str)
getLevelName("DEBUG")  # 10 (int)
getLevelName("debug")  # 10 (int, case-insensitive)

# Compatibility mode disabled (improved behavior):
registerCompatibilityMode(compat_mode=False)
getLevelName(10)  # "DEBUG"
getLevelName("DEBUG")  # "DEBUG" (uppercased and returned)
getLevelName("debug")  # "DEBUG" (uppercased)
getLevelName(999, strict=True)  # ValueError: Unknown log level: 999

# For string→int conversion when compat mode disabled, use getLevelNumber()
getLevelNumber("DEBUG")  # 10
```

### getLevelNameStr

```python
getLevelNameStr(level: int | str, *, strict: bool = False) -> str
```

Convert a log level to its string name representation.

Unidirectional function that always returns a string. This is the recommended way to convert log levels to strings when you want guaranteed string output without compatibility mode behavior.

Unlike `getLevelName()` which has compatibility mode and bidirectional behavior, this function always returns a string:
- Integer input: converts to level name string (returns "Level {level}" for unknown levels unless strict=True)
- String input: validates level exists, then returns uppercased string

Handles all levels registered via `logging.addLevelName()` (including standard library levels, custom apathetic levels, and user-registered levels).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int \| str | Log level as integer or string name (case-insensitive) |
| `strict` | bool | If True, raise ValueError for unknown integer levels. If False (default), returns "Level {level}" format for unknown integer levels (matching stdlib behavior). |

**Returns:**
- `str`: Level name as uppercase string

**Raises:**
- `ValueError`: If string level cannot be resolved to a known level, or if strict=True and integer level cannot be resolved to a known level

**Example:**
```python
from apathetic_logging import getLevelNameStr

# Integer input converts to level name
getLevelNameStr(10)  # "DEBUG"
getLevelNameStr(5)   # "TRACE"
getLevelNameStr(20)  # "INFO"

# String input validates and returns uppercased string
getLevelNameStr("DEBUG")  # "DEBUG"
getLevelNameStr("debug")  # "DEBUG"
getLevelNameStr("Info")  # "INFO"

# Unknown integer levels return "Level {level}" format (strict=False, default)
getLevelNameStr(999)  # "Level 999"

# Unknown integer levels raise ValueError when strict=True
getLevelNameStr(999, strict=True)  # ValueError: Unknown log level: 999

# Unknown string input raises ValueError
getLevelNameStr("UNKNOWN")  # ValueError: Unknown log level: 'UNKNOWN'
```

**See Also:**
- `getLevelNumber()` - Convert string to int (complementary function)
- `getLevelName()` - Bidirectional conversion with compatibility mode

### getLevelNamesMapping

```python
getLevelNamesMapping() -> dict[int, str]
```

**Requires Python 3.11+**

Wrapper for `logging.getLevelNamesMapping()`. Get mapping of level names to numeric values.

For detailed documentation, see the [Python logging.getLevelNamesMapping() documentation](https://docs.python.org/3.11/library/logging.html#logging.getLevelNamesMapping).

### getLevelNumber

```python
getLevelNumber(level: str | int) -> int
```

Convert a log level name to its numeric value.

Recommended way to convert string level names to integers. This function explicitly performs string→int conversion, unlike `getLevelName()` which has bidirectional behavior for backward compatibility.

Handles all levels registered via `logging.addLevelName()` (including standard library levels, custom apathetic levels, and user-registered levels).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | str \| int | Log level as string name (case-insensitive) or integer |

**Returns:**
- `int`: Integer level value

**Raises:**
- `ValueError`: If level cannot be resolved to a known level

**Example:**
```python
from apathetic_logging import getLevelNumber

# Known levels return int
getLevelNumber("DEBUG")  # 10
getLevelNumber("TRACE")  # 5
getLevelNumber(20)       # 20

# Unknown level raises ValueError
getLevelNumber("UNKNOWN")  # ValueError: Unknown log level: 'UNKNOWN'
```

**See Also:**
- `getLevelName()` - Bidirectional conversion with compatibility mode
- `getLevelNameStr()` - Unidirectional conversion (always returns string)

### getLogLevelEnvVars

```python
getLogLevelEnvVars() -> list[str]
```

Get the environment variable names to check for log level.

Returns the registered environment variable names, or the default environment variables if none are registered. These environment variables are checked in order by `determineLogLevel()` when resolving the log level.

**Returns:**
- `list[str]`: List of environment variable names to check for log level. Defaults to `["LOG_LEVEL"]` if not registered.

**Example:**
```python
from apathetic_logging import getLogLevelEnvVars, registerLogLevelEnvVars

# Get default environment variables
env_vars = getLogLevelEnvVars()
print(env_vars)  # ["LOG_LEVEL"]

# Register custom environment variables
registerLogLevelEnvVars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])
env_vars = getLogLevelEnvVars()
print(env_vars)  # ["MYAPP_LOG_LEVEL", "LOG_LEVEL"]
```

**See Also:**
- `registerLogLevelEnvVars()` - Register environment variables to check for log level
- `determineLogLevel()` - Resolve log level from CLI → env → root config → default

### getLogRecordFactory

```python
getLogRecordFactory() -> Callable
```

Wrapper for `logging.getLogRecordFactory()`. Return the factory function used to create LogRecords.

For detailed documentation, see the [Python logging.getLogRecordFactory() documentation](https://docs.python.org/3/library/logging.html#logging.getLogRecordFactory).

### getLogger

```python
getLogger(
    name: str | None = None,
    *args: Any,
    level: str | int | None = None,
    minimum: bool | None = None,
    extend: bool | None = None,
    **kwargs: Any
) -> Logger
```

Return a logger with the specified name, creating it if necessary.

**Changed from stdlib:** This function has several improvements over `logging.getLogger()`:

- **Auto-inference:** When `name` is `None`, automatically infers the logger name from the calling module's `__package__` attribute by examining the call stack, instead of returning the root logger. This makes it convenient to use `getLogger()` without explicitly passing a name.
- **Root logger access:** When `name` is an empty string (`""`), returns the root logger as usual, matching standard library behavior.
- **Apathetic logger:** Returns an `apathetic_logging.Logger` instance instead of the standard `logging.Logger`.
- **Level setting:** Optional `level` parameter to set the logger's level when creating it.
- **Minimum level:** Optional `minimum` parameter to only set the level if it's more verbose than the current level.
- **Compatibility mode:** In compatibility mode, `getLogger(None)` returns the root logger (stdlib behavior).

For detailed documentation on the base functionality, see the [Python logging.getLogger() documentation](https://docs.python.org/3/library/logging.html#logging.getLogger).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str \| None | The name of the logger to get. If `None`, the logger name will be auto-inferred from the calling module's `__package__`. If an empty string (`""`), returns the root logger. |
| `*args` | Any | Additional positional arguments (for future-proofing) |
| `level` | str \| int \| None | Exact log level to set on the logger. Accepts both string names (case-insensitive) and numeric values. If provided, sets the logger's level to this value. Defaults to `None`. |
| `minimum` | bool \| None | If `True`, only set the level if it's more verbose (lower numeric value) than the current level. This prevents downgrading from a more verbose level (e.g., TRACE) to a less verbose one (e.g., DEBUG). If `None`, defaults to `False`. Only used when `level` is provided. |
| `extend` | bool \| None | If `True` (default), extend the logging module. If `False`, skip extension. |
| `**kwargs` | Any | Additional keyword arguments (for future-proofing) |

**Returns:**
- `Logger`: An `apathetic_logging.Logger` instance

**Example:**
```python
from apathetic_logging import getLogger

# Auto-infer logger name from calling module
logger = getLogger()  # Uses __package__ from caller

# Explicit logger name
logger = getLogger("mymodule")

# Get root logger
root = getLogger("")

# Create logger with level
logger = getLogger("mymodule", level="DEBUG")

# Create logger with minimum level (won't downgrade from TRACE)
logger = getLogger("mymodule", level="DEBUG", minimum=True)
```

**See Also:**
- `getLoggerOfType()` - Get a logger of a specific type
- `getRootLogger()` - Return the root logger instance
- `registerLogger()` - Register a logger name for use by `getLogger()`

### getLoggerOfType

```python
getLoggerOfType(
    name: str | None,
    class_type: type[Logger],
    skip_frames: int = 1,
    *args: Any,
    level: str | int | None = None,
    minimum: bool | None = None,
    extend: bool | None = True,
    replace_root: bool | None = None,
    **kwargs: Any
) -> Logger
```

Get a logger of the specified type, creating it if necessary.

This function is similar to `getLogger()`, but allows you to specify a custom logger class type. This is useful when you have a custom logger subclass and want to ensure you get an instance of that specific type.

**Key Features:**

- **Custom logger type:** Returns a logger instance of the specified `class_type` instead of the default `apathetic_logging.Logger`.
- **Auto-inference:** When `name` is `None`, automatically infers the logger name from the calling module's `__package__` attribute by examining the call stack, instead of returning the root logger.
- **Root logger access:** When `name` is an empty string (`""`), returns the root logger as usual, matching standard library behavior.
- **Level setting:** Optional `level` parameter to set the logger's level when creating it.
- **Minimum level:** Optional `minimum` parameter to only set the level if it's more verbose than the current level.
- **Type safety:** Ensures the logger is of the specified type, replacing it if necessary and porting state (handlers, level, etc.) from the old logger.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str \| None | The name of the logger to get. If `None`, the logger name will be auto-inferred from the calling module's `__package__`. If an empty string (`""`), returns the root logger. |
| `class_type` | type[Logger] | The logger class type to use (e.g., `AppLogger`, `CustomLogger`). |
| `skip_frames` | int | Number of frames to skip when inferring logger name. Prefer using as a keyword argument (e.g., `skip_frames=2`) for clarity. Defaults to `1`. |
| `*args` | Any | Additional positional arguments (for future-proofing) |
| `level` | str \| int \| None | Exact log level to set on the logger. Accepts both string names (case-insensitive) and numeric values. If provided, sets the logger's level to this value. Defaults to `None`. |
| `minimum` | bool \| None | If `True`, only set the level if it's more verbose (lower numeric value) than the current level. This prevents downgrading from a more verbose level (e.g., TRACE) to a less verbose one (e.g., DEBUG). If `None`, defaults to `False`. Only used when `level` is provided. |
| `extend` | bool \| None | If `True` (default), extend the logging module. If `False`, skip extension. |
| `replace_root` | bool \| None | Whether to replace the root logger if it's not the correct type. If `None` (default), uses registry setting or constant default. Only used when `extend=True`. |
| `**kwargs` | Any | Additional keyword arguments (for future-proofing) |

**Returns:**
- `Logger`: A logger instance of the specified type

**Example:**
```python
from apathetic_logging import getLoggerOfType, Logger

# Get a standard apathetic logger
logger = getLoggerOfType("mymodule", Logger)

# Get a custom logger type (e.g., AppLogger)
from myapp.logs import AppLogger
app_logger = getLoggerOfType("myapp", AppLogger)

# Auto-infer name with custom type
app_logger = getLoggerOfType(None, AppLogger)

# Create logger with level
app_logger = getLoggerOfType("myapp", AppLogger, level="DEBUG")
```

**See Also:**
- `getLogger()` - Get a logger (returns default `apathetic_logging.Logger` type)
- `registerLogger()` - Register a logger name for use by `getLogger()`

### getLoggerClass

```python
getLoggerClass() -> type[logging.Logger]
```

Wrapper for `logging.getLoggerClass()`. Return the class to be used when instantiating a logger.

For detailed documentation, see the [Python logging.getLoggerClass() documentation](https://docs.python.org/3/library/logging.html#logging.getLoggerClass).

### getRegisteredLoggerName

```python
getRegisteredLoggerName() -> str | None
```

Get the registered logger name.

Returns the registered logger name, or None if no logger name has been registered. Unlike `getDefaultLoggerName()`, this does not perform inference - it only returns the explicitly registered value.

**Returns:**
- `str | None`: Registered logger name, or None if not registered

**Note:** This is a registry getter function. For other registry getters, see the subsections above.

### getRootLogger

```python
getRootLogger() -> Logger | logging.RootLogger
```

Return the root logger instance.

This is the primary way to access the root logger. It's more explicit and discoverable than using `logging.getLogger("")` or `getLogger("")`.

The root logger may be either:
- An `apathetic_logging.Logger` if it was created after `extendLoggingModule()` was called (expected/common case)
- A standard `logging.RootLogger` if it was created before `extendLoggingModule()` was called (fallback)

**Returns:**
- `Logger | logging.RootLogger`: The root logger instance (either `apathetic_logging.Logger` or `logging.RootLogger`)

**Example:**
```python
from apathetic_logging import getRootLogger

# Get the root logger
root = getRootLogger()

# Configure the root logger
root.setLevel("debug")
root.info("This logs to the root logger")
```

**See Also:**
- `getLogger("")` - Alternative way to get the root logger
- `extendLoggingModule()` - Extend the logging module and ensure root logger is apathetic type

### getTargetPythonVersion

```python
getTargetPythonVersion() -> tuple[int, int] | None
```

Get the target Python version.

Returns the registered target Python version, or the minimum supported version if none is registered. This version is used by `checkPythonVersionRequirement()` to determine if version-gated functions should be available.

**Returns:**
- `tuple[int, int] | None`: Target Python version as `(major, minor)` tuple, or `None` if no version is registered and `TARGET_PYTHON_VERSION` is `None` (checks disabled)

**Example:**
```python
from apathetic_logging import getTargetPythonVersion, registerTargetPythonVersion

# Get default target version
version = getTargetPythonVersion()
print(version)  # (3, 10) or None if checks are disabled

# Register a custom target version
registerTargetPythonVersion((3, 11))
version = getTargetPythonVersion()
print(version)  # (3, 11)
```

**See Also:**
- `registerTargetPythonVersion()` - Register the target Python version for compatibility checking
- `checkPythonVersionRequirement()` - Check if a function is available for the target Python version

### hasLogger

```python
hasLogger(logger_name: str) -> bool
```

Check if a logger exists in the logging manager's registry.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `logger_name` | str | The name of the logger to check |

**Returns:**
- `bool`: True if the logger exists, False otherwise

### removeLogger

```python
removeLogger(logger_name: str) -> None
```

Remove a logger from the logging manager's registry.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `logger_name` | str | The name of the logger to remove |

### safeLog

```python
safeLog(msg: str) -> None
```

Emergency logger that never fails.

This function bypasses the normal logging system and writes directly to `sys.__stderr__`. It's designed for use in error handlers where the logging system itself might be broken.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |

**Example:**
```python
from apathetic_logging import safeLog

try:
    # Some operation
    pass
except Exception:
    safeLog("Critical error: logging system may be broken")
```

### safeTrace

```python
safeTrace(label: str, *args: Any, icon: str = "🧪") -> None
```

Debug tracing function for test development. Only active when safe trace is enabled via environment variables.

Safe trace is enabled when any of the following conditions are met:
1. `SAFE_TRACE` environment variable is set to `"1"`, `"true"`, or `"yes"` (case insensitive)
2. `LOG_LEVEL` environment variable (case insensitive) is set to `"TRACE"` or `"TEST"`
3. `LOG_LEVEL` numeric value is less than or equal to `TRACE_LEVEL` (supports both numeric strings like `"5"` and standard logging level names like `"DEBUG"`)

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `label` | str | Trace label |
| `*args` | Any | Additional arguments to trace |
| `icon` | str | Icon to use (default: `"🧪"`) |

**Example:**
```python
from apathetic_logging import safeTrace
import os

# Enable via SAFE_TRACE
os.environ["SAFE_TRACE"] = "1"
safeTrace("debug", "message")  # Will output

# Enable via LOG_LEVEL
os.environ["LOG_LEVEL"] = "TRACE"
safeTrace("debug", "message")  # Will output

# Or via numeric LOG_LEVEL
os.environ["LOG_LEVEL"] = "5"  # TRACE_LEVEL is 5
safeTrace("debug", "message")  # Will output
```

### makeSafeTrace

```python
makeSafeTrace(icon: str = "🧪") -> Callable
```

Create a test trace function with a custom icon.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `icon` | str | Icon to use |

**Returns:**
- `Callable`: Test trace function

### makeLogRecord

```python
makeLogRecord(
    name: str,
    level: int,
    fn: str,
    lno: int,
    msg: str,
    args: tuple,
    exc_info: Any
) -> logging.LogRecord
```

Wrapper for `logging.makeLogRecord()`. Create a LogRecord from the given parameters.

For detailed documentation, see the [Python logging.makeLogRecord() documentation](https://docs.python.org/3/library/logging.html#logging.makeLogRecord).

### test

```python
test(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message at TEST level.

TEST is the most verbose level and bypasses capture. This function gets an `apathetic_logging.Logger` instance (ensuring the root logger is an apathetic logger) and calls its `test()` method.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments |

**Example:**
```python
import apathetic_logging

# Log a test message
apathetic_logging.test("Test message: %s", variable)
```

### trace

```python
trace(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message with severity TRACE on the root logger.

TRACE is more verbose than DEBUG. This function gets an `apathetic_logging.Logger` instance (ensuring the root logger is an apathetic logger) and calls its `trace()` method.

If the logger has no handlers, `basicConfig()` is automatically called to add a console handler with a pre-defined format.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments for message formatting |
| `**kwargs` | Any | Additional keyword arguments (e.g., `exc_info`, `stacklevel`) |

**Example:**
```python
import apathetic_logging

# Log a trace message
apathetic_logging.trace("Detailed trace information: %s", variable)
```

### warn

```python
warn(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.warn()`. Log a message with severity WARNING.

For detailed documentation, see the [Python logging.warn() documentation](https://docs.python.org/3/library/logging.html#logging.warn).

### warning

```python
warning(msg: str, *args: Any, **kwargs: Any) -> None
```

Wrapper for `logging.warning()`. Log a message with severity WARNING.

For detailed documentation, see the [Python logging.warning() documentation](https://docs.python.org/3/library/logging.html#logging.warning).

### registerCompatibilityMode

```python
registerCompatibilityMode(*, compat_mode: bool | None) -> None
```

Register the compatibility mode setting for stdlib drop-in replacement.

This sets the compatibility mode that will be used when creating loggers. If not set, the library defaults to `False` (improved behavior).

When `compat_mode` is `True`, restores stdlib-compatible behavior where possible (e.g., `getLogger(None)` returns root logger instead of auto-inferring).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `compat_mode` | bool \| None | Compatibility mode setting (`True` or `False`). If `None`, returns immediately without making any changes. |

**Example:**
```python
from apathetic_logging import registerCompatibilityMode, getLogger

# Enable compatibility mode (stdlib behavior)
registerCompatibilityMode(compat_mode=True)
# Now getLogger(None) returns root logger (stdlib behavior)

# Disable compatibility mode (improved behavior, default)
registerCompatibilityMode(compat_mode=False)
# Now getLogger(None) auto-infers logger name
```

**See Also:**
- `getCompatibilityMode()` - Get the compatibility mode setting

### registerDefaultLogLevel

```python
registerDefaultLogLevel(default_level: str | None) -> None
```

Register the default log level to use when no other source is found.

This sets the default log level that will be used by `determineLogLevel()` when no other source (CLI args, environment variables, root logger level) provides a log level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `default_level` | str \| None | Default log level name (e.g., `"info"`, `"warning"`). If `None`, returns immediately without making any changes. |

**Example:**
```python
from apathetic_logging import registerDefaultLogLevel, getLogger

# Set default log level
registerDefaultLogLevel("warning")

# Now determineLogLevel() will use "warning" as fallback
logger = getLogger("mymodule")
level = logger.determineLogLevel()
print(level)  # "WARNING"
```

**See Also:**
- `getDefaultLogLevel()` - Get the registered default log level
- `determineLogLevel()` - Resolve log level from CLI → env → root config → default

### registerLogLevelEnvVars

```python
registerLogLevelEnvVars(env_vars: list[str] | None) -> None
```

Register environment variable names to check for log level.

The environment variables will be checked in order by `determineLogLevel()`, and the first non-empty value found will be used.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `env_vars` | list[str] \| None | List of environment variable names to check (e.g., `["MYAPP_LOG_LEVEL", "LOG_LEVEL"]`). If `None`, returns immediately without making any changes. |

**Example:**
```python
from apathetic_logging import registerLogLevelEnvVars, getLogger
import os

# Register custom environment variables
registerLogLevelEnvVars(["MYAPP_LOG_LEVEL", "LOG_LEVEL"])

# Set environment variable
os.environ["MYAPP_LOG_LEVEL"] = "debug"

# Now determineLogLevel() will check MYAPP_LOG_LEVEL first, then LOG_LEVEL
logger = getLogger("mymodule")
level = logger.determineLogLevel()
print(level)  # "DEBUG" (from MYAPP_LOG_LEVEL)
```

**See Also:**
- `getLogLevelEnvVars()` - Get the registered environment variable names
- `determineLogLevel()` - Resolve log level from CLI → env → root config → default

### registerLogger

```python
registerLogger(
    logger_name: str | None = None,
    logger_class: type[Logger] | None = None,
    *,
    target_python_version: tuple[int, int] | None = None,
    log_level_env_vars: list[str] | None = None,
    default_log_level: str | None = None,
    propagate: bool | None = None,
    compat_mode: bool | None = None,
    replace_root: bool | None = None
) -> None
```

Register a logger for use by `getLogger()`.

This is the public API for registering a logger. It registers the logger name and extends the logging module with custom levels if needed.

If `logger_name` is not provided, the top-level package is automatically extracted from the calling module's `__package__` attribute.

If `logger_class` is provided and has an `extendLoggingModule()` method, it will be called to extend the logging module with custom levels and set the logger class. If `logger_class` is provided but does not have `extendLoggingModule()`, `logging.setLoggerClass()` will be called directly to set the logger class. If `logger_class` is not provided, nothing is done with the logger class (the default `Logger` is already extended at import time).

**Important**: If you're using a custom logger class that has `extendLoggingModule()`, do not call `logging.setLoggerClass()` directly. Instead, pass the class to `registerLogger()` and let `extendLoggingModule()` handle setting the logger class. This ensures consistent behavior and avoids class identity issues in singlefile mode.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `logger_name` | str \| None | The name of the logger to retrieve (e.g., `"myapp"`). If `None`, extracts the top-level package from `__package__`. |
| `logger_class` | type[Logger] \| None | Optional logger class to use. If provided and the class has an `extendLoggingModule()` method, it will be called. If the class doesn't have that method, `logging.setLoggerClass()` will be called directly. If `None`, nothing is done (default `Logger` is already set up at import time). |
| `target_python_version` | tuple[int, int] \| None | Optional target Python version `(major, minor)` tuple. If provided, sets the target Python version in the registry permanently. Defaults to `None` (no change). |
| `log_level_env_vars` | list[str] \| None | Optional list of environment variable names to check for log level. If provided, sets the log level environment variables in the registry permanently. Defaults to `None` (no change). |
| `default_log_level` | str \| None | Optional default log level name. If provided, sets the default log level in the registry permanently. Defaults to `None` (no change). |
| `propagate` | bool \| None | Optional propagate setting. If provided, sets the propagate value in the registry permanently. Defaults to `None` (no change). |
| `compat_mode` | bool \| None | Optional compatibility mode setting. If provided, sets the compatibility mode in the registry permanently. When `True`, restores stdlib-compatible behavior where possible (e.g., `getLogger(None)` returns root logger). Defaults to `None` (no change). |
| `replace_root` | bool \| None | Optional setting for whether to replace root logger. If provided, passes this value to `extendLoggingModule()` when extending the logging module. If `None`, uses registry setting or constant default. Only used when `logger_class` has an `extendLoggingModule()` method. |

**Example:**
```python
from apathetic_logging import registerLogger, getLogger

# Explicit registration with default Logger (already extended)
registerLogger("myapp")
logger = getLogger()  # Uses "myapp" as logger name

# Auto-infer from __package__
registerLogger()  # Uses top-level package from __package__

# Register with custom logger class (has extendLoggingModule)
from apathetic_logging import Logger

class AppLogger(Logger):
    pass

# Don't call AppLogger.extendLoggingModule() or
# logging.setLoggerClass() directly - registerLogger() handles it
registerLogger("myapp", AppLogger)

# Register with convenience parameters
registerLogger(
    "myapp",
    AppLogger,
    target_python_version=(3, 10),
    log_level_env_vars=["MYAPP_LOG_LEVEL", "LOG_LEVEL"],
    default_log_level="info",
    propagate=False,
    compat_mode=False
)
```

**See Also:**
- `getLogger()` - Get a logger instance (uses registered name if available)
- `getLoggerOfType()` - Get a logger of a specific type
- `getRegisteredLoggerName()` - Get the registered logger name

### registerPortHandlers

```python
registerPortHandlers(*, port_handlers: bool | None) -> None
```

Register whether to port handlers when replacing a logger.

This sets whether logger replacement should port handlers from the old logger to the new logger. If not set, the library defaults to `DEFAULT_PORT_HANDLERS` from constants.py (True by default - port handlers to preserve existing configuration).

When `port_handlers` is `True`, handlers from the old logger are ported to the new logger. When `False`, the new logger manages its own handlers via `manageHandlers()`.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `port_handlers` | bool \| None | Whether to port handlers (True or False). If None, the registration is skipped. |

**Example:**
```python
from apathetic_logging import registerPortHandlers

# Enable handler porting to preserve existing handlers
registerPortHandlers(port_handlers=True)
# Now logger replacement will port handlers
```

### registerPortLevel

```python
registerPortLevel(*, port_level: bool | None) -> None
```

Register whether to port level when replacing a logger.

This sets whether logger replacement should port the log level from the old logger to the new logger. If not set, the library defaults to `DEFAULT_PORT_LEVEL` from constants.py (True by default - port level to preserve existing configuration).

When `port_level` is `True`, the log level is ported from the old logger. When `False`, the new logger uses apathetic defaults (determineLogLevel() for root logger, INHERIT_LEVEL for leaf loggers).

**Note:** User-provided level parameters in `getLogger()`/`getLoggerOfType()` take precedence over ported level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `port_level` | bool \| None | Whether to port level (True or False). If None, the registration is skipped. |

**Example:**
```python
from apathetic_logging import registerPortLevel

# Enable level porting to preserve existing level
registerPortLevel(port_level=True)
# Now logger replacement will port level
```

### registerPropagate

```python
registerPropagate(*, propagate: bool | None) -> None
```

Register the propagate setting for loggers.

This sets the default propagate value that will be used when creating loggers. If not set, the library defaults to `DEFAULT_PROPAGATE` from constants.py (`True` by default - propagate to parent loggers).

When `propagate` is `True`, loggers propagate messages to parent loggers, allowing centralized control via root logger. When `False`, messages only go to the logger's own handlers.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `propagate` | bool \| None | Propagate setting (`True` or `False`). If `None`, returns immediately without making any changes. |

**Example:**
```python
from apathetic_logging import registerPropagate, getLogger

# Enable propagation (default)
registerPropagate(propagate=True)
logger = getLogger("mymodule")
# Messages will propagate to root logger

# Disable propagation (isolated logging)
registerPropagate(propagate=False)
logger = getLogger("mymodule")
# Messages only go to logger's own handlers
```

**See Also:**
- `getDefaultPropagate()` - Get the registered propagate setting
- `setLevelAndPropagate()` - Set level and propagate together with smart defaults

### registerReplaceRootLogger

```python
registerReplaceRootLogger(*, replace_root: bool | None) -> None
```

Register whether to replace root logger if it's not the correct type.

This sets whether `extendLoggingModule()` should replace the root logger if it's not an instance of the apathetic logger class. If not set, the library defaults to `DEFAULT_REPLACE_ROOT_LOGGER` from constants.py (True by default - replace root logger to ensure it's an apathetic logger).

When `replace_root` is `False`, `extendLoggingModule()` will not replace the root logger, allowing applications to use their own custom logger class for the root logger.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `replace_root` | bool \| None | Whether to replace root logger (True or False). If None, the registration is skipped. |

**Example:**
```python
from apathetic_logging import registerReplaceRootLogger

# Disable root logger replacement to use your own logger class
registerReplaceRootLogger(replace_root=False)
# Now extendLoggingModule() won't replace the root logger
```

### registerTargetPythonVersion

```python
registerTargetPythonVersion(version: tuple[int, int] | None) -> None
```

Register the target Python version for compatibility checking.

This sets the target Python version that will be used to validate function calls. If a function requires a Python version newer than the target version, it will raise a `NotImplementedError` even if the runtime version is sufficient.

If not set, the library defaults to `TARGET_PYTHON_VERSION` from constants.py `(3, 10)`. This allows developers to catch version incompatibilities during development even when running on a newer Python version than their target.

**Note:** The runtime version is still checked as a safety net. If the runtime version is older than required, the function will still raise an error even if the target version is sufficient.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | tuple[int, int] \| None | Target Python version as `(major, minor)` tuple (e.g., `(3, 10)` or `(3, 11)`). If `None`, returns immediately without making any changes. |

**Example:**
```python
from apathetic_logging import registerTargetPythonVersion, getLevelNamesMapping

# Register target Python version
registerTargetPythonVersion((3, 10))

# Now functions requiring 3.11+ will raise even if running on 3.12
try:
    mapping = getLevelNamesMapping()  # Requires Python 3.11+
except NotImplementedError as e:
    print(f"Function not available: {e}")
    # Error message suggests raising target version if needed
```

**Why this matters:**
- Prevents accidental use of newer Python features during development
- Ensures your code works on your target Python version
- Error messages guide you to either avoid the function or raise your target version

**See Also:**
- `getTargetPythonVersion()` - Get the registered target Python version
- `checkPythonVersionRequirement()` - Check if a function is available for the target Python version

### setLogRecordFactory

```python
setLogRecordFactory(factory: Callable) -> None
```

Wrapper for `logging.setLogRecordFactory()`. Set the factory function used to create LogRecords.

For detailed documentation, see the [Python logging.setLogRecordFactory() documentation](https://docs.python.org/3/library/logging.html#logging.setLogRecordFactory).

### setLoggerClass

```python
setLoggerClass(klass: type[logging.Logger]) -> None
```

Wrapper for `logging.setLoggerClass()`. Set the class to be used when instantiating a logger.

For detailed documentation, see the [Python logging.setLoggerClass() documentation](https://docs.python.org/3/library/logging.html#logging.setLoggerClass).

### shutdown

```python
shutdown() -> None
```

Wrapper for `logging.shutdown()`. Perform an orderly shutdown of the logging system.

For detailed documentation, see the [Python logging.shutdown() documentation](https://docs.python.org/3/library/logging.html#logging.shutdown).


## `apathetic_logging.Logger` Function Reference

### Constructor

```python
Logger(
    name: str,
    level: int = logging.NOTSET,
    *,
    enable_color: bool | None = None
)
```

Logger class for all Apathetic tools. Extends Python's standard `logging.Logger`.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Logger name |
| `level` | int | Initial log level (defaults to `INHERIT_LEVEL` (i.e. `logging.NOTSET`)) |
| `enable_color` | bool \| None | Whether to enable colorized output. If None, auto-detects based on TTY and environment variables. |

### _log

```python
_log(level: int, msg: str, args: tuple[Any, ...], **kwargs: Any) -> None
```

Log a message with the specified level.

**Changed from stdlib:** Automatically ensures handlers are attached via `ensureHandlers()`.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int | The numeric logging level |
| `msg` | str | The message format string |
| `args` | tuple[Any, ...] | Arguments for the message format string |
| `**kwargs` | Any | Additional keyword arguments passed to the base implementation |

### addLevelName

```python
addLevelName(level: int, level_name: str) -> None
```

Associate a level name with a numeric level. (staticmethod)

**Changed from stdlib:** Validates that level value is positive (> 0) to prevent INHERIT_LEVEL (i.e. NOTSET)
inheritance issues. Sets `logging.<LEVEL_NAME>` attribute for convenience.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int | The numeric level value (must be > 0 for custom levels) |
| `level_name` | str | The name to associate with this level |

**Raises:**
- `ValueError`: If level <= 0 (which would cause INHERIT_LEVEL (i.e. NOTSET) inheritance)
- `ValueError`: If `logging.<LEVEL_NAME>` already exists with an invalid value

### brief

```python
brief(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message at BRIEF level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments |

### colorize

```python
colorize(text: str, color: str, *, enable_color: bool | None = None) -> str
```

Apply ANSI color codes to text.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | str | Text to colorize |
| `color` | str | ANSI color code (e.g., `ANSIColors.CYAN`, `ANSIColors.RED`) |
| `enable_color` | bool \| None | Override color enablement. If None, uses instance setting. |

**Returns:**
- `str`: Colorized text (or original text if colors disabled)

### criticalIfNotDebug

```python
criticalIfNotDebug(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a critical error with full traceback only if debug/trace is enabled.

Similar to `errorIfNotDebug()` but logs at CRITICAL level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Error message |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments |

### detail

```python
detail(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message at DETAIL level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments |

### determineColorEnabled

```python
determineColorEnabled() -> bool
```

Return True if colored output should be enabled. (classmethod)

Checks:
- `NO_COLOR` environment variable (disables colors)
- `FORCE_COLOR` environment variable (enables colors)
- TTY detection (enables colors if stdout is a TTY)

**Returns:**
- `bool`: True if colors should be enabled

### determineLogLevel

```python
determineLogLevel(
    *,
    args: argparse.Namespace | None = None,
    root_log_level: str | None = None
) -> str
```

Resolve log level from CLI → env → root config → default.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `args` | argparse.Namespace \| None | Parsed command-line arguments (checks for `args.log_level`) |
| `root_log_level` | str \| None | Root logger level to use as fallback |

**Returns:**
- `str`: Resolved log level name (uppercase)

**Example:**
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--log-level", default="info")
args = parser.parse_args()

level = logger.determineLogLevel(args=args)
logger.setLevel(level)
```

### effectiveLevel

```python
effectiveLevel: int
```

Return the effective level (what's actually used) (read-only property).

This property returns the effective logging level for this logger, considering
inheritance from parent loggers. This is the preferred way to get the effective
level. Also available via `getEffectiveLevel()` for stdlib compatibility.

**Example:**
```python
parent = getLogger("parent")
parent.setLevel("info")

child = getLogger("parent.child")
print(child.level)  # 0 (INHERIT_LEVEL, i.e. NOTSET - explicit)
print(child.effectiveLevel)  # 20 (INFO - effective, from parent)
```

### effectiveLevelName

```python
effectiveLevelName: str
```

Return the effective level name (what's actually used) (read-only property).

This property returns the name of the effective logging level for this logger,
considering inheritance from parent loggers. This is the preferred way to get
the effective level name. Also available via `getEffectiveLevelName()` for
consistency.

**Example:**
```python
parent = getLogger("parent")
parent.setLevel("info")

child = getLogger("parent.child")
print(child.levelName)  # "NOTSET" (explicit - INHERIT_LEVEL, i.e. NOTSET)
print(child.effectiveLevelName)  # "INFO" (effective, from parent)
```

### errorIfNotDebug

```python
errorIfNotDebug(msg: str, *args: Any, **kwargs: Any) -> None
```

Log an error with full traceback only if debug/trace is enabled.

If debug mode is enabled, shows full exception traceback. Otherwise, shows only the error message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Error message |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments |

**Example:**
```python
try:
    risky_operation()
except Exception:
    logger.errorIfNotDebug("Operation failed")
```

### extendLoggingModule

```python
extendLoggingModule(
    *,
    replace_root: bool | None = None,
    port_handlers: bool | None = None,
    port_level: bool | None = None
) -> bool
```

Extend Python's logging module with TRACE and SILENT levels. (classmethod)

This method:
- Sets `apathetic_logging.Logger` as the default logger class
- Adds `TRACE` and `SILENT` level names
- Adds `logging.TRACE` and `logging.SILENT` constants
- Optionally replaces the root logger if it's not the correct type

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `replace_root` | bool \| None | Whether to replace the root logger if it's not the correct type. If None (default), checks the registry setting (set via `registerReplaceRootLogger()`). If not set in registry, defaults to True for backward compatibility. When False, the root logger will not be replaced, allowing applications to use their own custom logger class for the root logger. |
| `port_handlers` | bool \| None | Whether to port handlers from the old root logger to the new logger. If None (default), checks the registry setting (set via `registerPortHandlers()`). If not set in registry, defaults to True. When True, handlers from the old logger are ported. When False, the new logger manages its own handlers via `manageHandlers()`. |
| `port_level` | bool \| None | Whether to port level from the old root logger to the new logger. If None (default), checks the registry setting (set via `registerPortLevel()`). If not set in registry, defaults to True. When True, the old level is preserved. When False, the new root logger uses `determineLogLevel()` to get a sensible default. |

**Returns:**
- `bool`: True if the extension ran, False if it was already extended

**Note:** When the root logger is replaced, its state is preserved by default (handlers and level are ported, propagate and disabled are always ported). Child loggers are automatically reconnected to the new root logger instance.

### getChildren

```python
getChildren() -> set[logging.Logger]
```

**Requires Python 3.12+**

Return a set of loggers that are immediate children of this logger.

This method returns only the direct children of the logger (loggers whose names are one level deeper in the hierarchy). For example, if you have loggers named `foo`, `foo.bar`, and `foo.bar.baz`, calling `getLogger("foo").getChildren()` will return a set containing only the `foo.bar` logger, not `foo.bar.baz`.

**Returns:**
- `set[logging.Logger]`: A set of Logger instances that are immediate children of this logger

**Example:**
```python
from apathetic_logging import getLogger

root = getLogger("")
foo = getLogger("foo")
bar = getLogger("foo.bar")
baz = getLogger("foo.bar.baz")

# Get immediate children of root logger
children = root.getChildren()  # {foo logger}

# Get immediate children of foo logger
children = foo.getChildren()  # {bar logger}

# Get immediate children of bar logger
children = bar.getChildren()  # {baz logger}
```

For detailed documentation, see the [Python logging.Logger.getChildren() documentation](https://docs.python.org/3.12/library/logging.html#logging.Logger.getChildren).

### getEffectiveLevelName

```python
getEffectiveLevelName() -> str
```

Return the effective level name (what's actually used).

This method returns the name of the effective logging level for this logger,
considering inheritance from parent loggers. Prefer the `effectiveLevelName` property
for convenience, or use this method for consistency with `getEffectiveLevel()`.

**Returns:**
- `str`: The effective level name for this logger

**Example:**
```python
parent = getLogger("parent")
parent.setLevel("info")

child = getLogger("parent.child")
print(child.getEffectiveLevelName())  # "INFO" (from parent)
```

### getLevel

```python
getLevel() -> int
```

Return the explicit level set on this logger.

This method returns the level explicitly set on this logger (same as `level`
property). For the effective level, use `getEffectiveLevel()` or the
`effectiveLevel` property.

**Returns:**
- `int`: The explicit level value set on this logger

**Example:**
```python
logger.setLevel("debug")
print(logger.getLevel())  # 10
```

### getLevelName

```python
getLevelName() -> str
```

Return the explicit level name set on this logger.

This method returns the name of the level explicitly set on this logger (same
as `levelName` property). For the effective level name, use
`getEffectiveLevelName()` or the `effectiveLevelName` property.

**Returns:**
- `str`: The explicit level name set on this logger

**Example:**
```python
logger.setLevel("debug")
print(logger.getLevelName())  # "DEBUG"
```

### ensureHandlers

```python
ensureHandlers() -> None
```

Ensure handlers are attached to this logger.

DualStreamHandler is what will ensure logs go to the write channel.
Rebuilds handlers if they're missing or if stdout/stderr have changed.

**Note:** This method is automatically called by `_log()` when logging. You typically don't need to call it directly.

### levelName

```python
levelName: str
```

Return the explicit level name set on this logger (read-only property).

This property returns the name of the level explicitly set on this logger.
For the effective level name (what's actually used, considering inheritance),
use `effectiveLevelName` instead.

**Example:**
```python
logger.setLevel("debug")
print(logger.levelName)  # "DEBUG"
```

### logDynamic

```python
logDynamic(level: str | int, msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message at a dynamically specified level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | str \| int | Log level name or numeric value |
| `msg` | str | Message to log |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments |

**Example:**
```python
logger.logDynamic("warning", "This is a warning")
logger.logDynamic(logging.ERROR, "This is an error")
```

### setLevel

```python
setLevel(level: int | str, *, minimum: bool | None = False, allow_inherit: bool = False) -> None
```

Set the logging level. Accepts both string names (case-insensitive) and numeric values.

**Changed from stdlib:** Accepts string level names and has `minimum` and `allow_inherit` parameters. In improved mode (default), validates that levels are > 0 to prevent accidental INHERIT_LEVEL (i.e. NOTSET) inheritance. In compatibility mode, accepts any level value (including 0 and negative) matching stdlib behavior.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int \| str | Log level name or numeric value |
| `minimum` | bool \| None | If True, only set the level if it's more verbose (lower numeric value) than the current level. Defaults to False. |
| `allow_inherit` | bool | If True, allows setting level to 0 (INHERIT_LEVEL, i.e. NOTSET) in improved mode. In compatibility mode, this parameter is ignored and 0 is always accepted. Defaults to False. |

**Behavior:**

- **Improved mode (default):** Rejects level 0 (INHERIT_LEVEL, i.e. NOTSET) unless `allow_inherit=True` is explicitly provided. This prevents accidental INHERIT_LEVEL (i.e. NOTSET) inheritance from custom levels that accidentally evaluate to 0.
- **Compatibility mode:** Accepts any level value (including 0 and negative) matching stdlib behavior. The `allow_inherit` parameter is ignored in this mode.

**Example:**
```python
logger.setLevel("debug")
logger.setLevel(logging.DEBUG)

# Set to INHERIT_LEVEL (i.e. NOTSET) (inherits from parent) - requires explicit allow_inherit=True
logger.setLevel(0, allow_inherit=True)

# In compatibility mode, INHERIT_LEVEL (i.e. NOTSET) is accepted without allow_inherit
from apathetic_logging import registerCompatibilityMode
registerCompatibilityMode(compat_mode=True)
logger.setLevel(0)  # Works in compat mode
```

### setLevelAndPropagate

```python
setLevelAndPropagate(
    level: int | str,
    *,
    minimum: bool | None = False,
    allow_inherit: bool = False,
    manage_handlers: bool | None = None
) -> None
```

Set the logging level and propagate setting together in a smart way.

This convenience method combines `setLevel()` and `setPropagate()` with intelligent defaults:
- If level is `INHERIT_LEVEL` (NOTSET): sets `propagate=True`
- If level is a specific level: sets `propagate=False`
- On root logger: only sets level (propagate is unchanged)

This matches common use cases: when inheriting level, you typically want to propagate to parent handlers. When setting an explicit level, you typically want isolated logging with your own handler.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int \| str | Log level name or numeric value. Use `INHERIT_LEVEL` (0) or "NOTSET" to inherit. |
| `minimum` | bool \| None | If True, only set the level if it's more verbose (lower numeric value) than the current level. Defaults to False. |
| `allow_inherit` | bool | If True, allows setting level to 0 (INHERIT_LEVEL, i.e. NOTSET) in improved mode. Defaults to False. |
| `manage_handlers` | bool \| None | If True, automatically manage apathetic handlers based on propagate setting. If None, uses DEFAULT_MANAGE_HANDLERS from constants. If False, only sets propagate without managing handlers. |

**Example:**
```python
logger = getLogger("mymodule")

# Set to inherit level and propagate to root
from apathetic_logging import INHERIT_LEVEL
logger.setLevelAndPropagate(INHERIT_LEVEL, allow_inherit=True)

# Set explicit level and disable propagation (isolated logging)
logger.setLevelAndPropagate("debug")
```

### setLevelInherit

```python
setLevelInherit() -> None
```

Set the logger to inherit its level from the parent logger.

This convenience method is equivalent to calling `setLevel(NOTSET, allow_inherit=True)`. It explicitly sets the logger to INHERIT_LEVEL (i.e. NOTSET) so it inherits its effective level from the root logger or parent logger.

**Example:**
```python
logger.setLevel("DEBUG")
# Set to inherit from root logger
logger.setLevelInherit()
assert logger.levelName == "NOTSET"
assert logger.effectiveLevel == root.level  # Inherits from root
```

### setLevelMinimum

```python
setLevelMinimum(level: int | str) -> None
```

Set the logging level only if it's more verbose than the current level.

This convenience method is equivalent to calling `setLevel(level, minimum=True)`. It prevents downgrading from a more verbose level (e.g., TRACE) to a less verbose one (e.g., DEBUG).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int \| str | Log level name or numeric value. Only set if it's more verbose (lower numeric value) than the current effective level. |

**Example:**
```python
logger.setLevel("TRACE")
# This won't downgrade from TRACE to DEBUG
logger.setLevelMinimum("DEBUG")
assert logger.levelName == "TRACE"  # Still TRACE

# This will upgrade from INFO to DEBUG
logger.setLevel("INFO")
logger.setLevelMinimum("DEBUG")
assert logger.levelName == "DEBUG"  # Upgraded to DEBUG
```

### test

```python
test(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message at TEST level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments |

### trace

```python
trace(msg: str, *args: Any, **kwargs: Any) -> None
```

Log a message at TRACE level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `msg` | str | Message to log |
| `*args` | Any | Format arguments |
| `**kwargs` | Any | Additional keyword arguments (e.g., `exc_info`, `stacklevel`) |

### useLevel

```python
useLevel(level: str | int, *, minimum: bool = False) -> ContextManager
```

Context manager to temporarily change log level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | str \| int | Log level to use |
| `minimum` | bool | If True, only set the level if it's more verbose (lower numeric value) than the current level. Prevents downgrading from a more verbose level. |

**Returns:**
- Context manager that restores the previous level on exit

**Example:**
```python
with logger.useLevel("debug"):
    logger.debug("This will be shown")

# Level is restored after the context
```

### useLevelAndPropagate

```python
useLevelAndPropagate(
    level: str | int,
    *,
    minimum: bool = False,
    manage_handlers: bool | None = None
) -> ContextManager
```

Context manager to temporarily set level and propagate together.

This convenience context manager combines `useLevel()` and `usePropagate()` with intelligent defaults:
- If level is `INHERIT_LEVEL` (NOTSET): sets `propagate=True`
- If level is a specific level: sets `propagate=False`
- On root logger: only sets level (propagate is unchanged)

Both settings are restored when the context exits.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | str \| int | Log level to use (string name or numeric value). Use `INHERIT_LEVEL` (0) or "NOTSET" to inherit. |
| `minimum` | bool | If True, only set the level if it's more verbose (lower numeric value) than the current effective level. Prevents downgrading from a more verbose level. Defaults to False. |
| `manage_handlers` | bool \| None | If True, automatically manage apathetic handlers based on propagate setting. If None, uses DEFAULT_MANAGE_HANDLERS from constants. If False, only sets propagate without managing handlers. |

**Returns:**
- Context manager that restores both the previous level and propagate setting on exit

**Example:**
```python
logger = getLogger("mymodule")

# Temporarily set to inherit level and propagate to root
with logger.useLevelAndPropagate(INHERIT_LEVEL, allow_inherit=True):
    logger.info("This will propagate to root")

# Temporarily set explicit level and disable propagation
with logger.useLevelAndPropagate("debug"):
    logger.debug("This only goes to logger's handlers")

# Both settings are restored after the context
```

### useLevelMinimum

```python
useLevelMinimum(level: str | int) -> ContextManager
```

Context manager to temporarily change log level, only if it's more verbose than the current level.

This convenience method is equivalent to calling `useLevel(level, minimum=True)`. It prevents downgrading from a more verbose level (e.g., TRACE) to a less verbose one (e.g., DEBUG).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | str \| int | Log level to use. Only applied if it's more verbose than the current effective level. |

**Returns:**
- Context manager that restores the previous level on exit

**Example:**
```python
logger.setLevel("TRACE")
# This won't downgrade from TRACE to DEBUG
with logger.useLevelMinimum("DEBUG"):
    assert logger.levelName == "TRACE"  # Still TRACE

# This will upgrade from INFO to DEBUG
logger.setLevel("INFO")
with logger.useLevelMinimum("DEBUG"):
    assert logger.levelName == "DEBUG"  # Upgraded to DEBUG
```

### usePropagate

```python
usePropagate(propagate: bool, *, manage_handlers: bool | None = None) -> ContextManager
```

Context manager to temporarily change propagate setting.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `propagate` | bool | If True, messages propagate to parent loggers. If False, messages only go to this logger's handlers. |
| `manage_handlers` | bool \| None | If True, automatically manage apathetic handlers based on propagate setting. If None, uses DEFAULT_MANAGE_HANDLERS from constants. If False, only sets propagate without managing handlers. In compat_mode, this may default to False. |

**Returns:**
- Context manager that restores the previous propagate setting on exit

**Example:**
```python
# Temporarily disable propagation to capture logs locally
with logger.usePropagate(False):
    logger.info("This message only goes to logger's handlers")
    # Do something that should not propagate to root

# Propagate setting is restored after the context
```

### validateLevel

```python
validateLevel(level: int, *, level_name: str | None = None, allow_inherit: bool = False) -> None
```

Validate that a level value is positive (> 0). (staticmethod)

Custom levels with values <= 0 will inherit from the root logger,
causing INHERIT_LEVEL (i.e. NOTSET) inheritance issues. In compatibility mode, validation is skipped.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | int | The numeric level value to validate |
| `level_name` | str \| None | Optional name for the level (for error messages). If None, will attempt to get from getLevelName() |
| `allow_inherit` | bool | If True, allows level 0 (INHERIT_LEVEL, i.e. NOTSET). Defaults to False. |

**Raises:**
- `ValueError`: If level <= 0 (or level == 0 without `allow_inherit=True`)

**Example:**
```python
Logger.validateLevel(5, level_name="TRACE")
Logger.validateLevel(0, level_name="TEST")
# ValueError: setLevel(0) sets the logger to INHERIT_LEVEL (i.e. NOTSET)...

Logger.validateLevel(0, level_name="TEST", allow_inherit=True)
# Passes validation
```

**Note:** This method is automatically called by `setLevel()` and `addLevelName()`. You typically don't need to call it directly unless you're implementing custom level validation logic.

