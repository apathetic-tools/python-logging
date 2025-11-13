---
layout: default
title: Quick Start
permalink: /quickstart/
---

# Quick Start Guide

Get up and running with Apathetic Python Logger in minutes.

## Basic Usage

The simplest way to use Apathetic Python Logger is to register a logger name and get a logger instance:

```python
from apathetic_logger import get_logger, register_logger_name

# Register your logger name
register_logger_name("my_app")

# Get the logger instance
logger = get_logger()

# Start logging!
logger.info("Application started")
logger.debug("Debug information")
logger.warning("This is a warning")
logger.error("An error occurred")
```

## Log Levels

Apathetic Python Logger supports the following log levels (in order of verbosity):

- `trace` — Most verbose, for detailed tracing
- `debug` — Debug information
- `info` — General informational messages (default)
- `warning` — Warning messages
- `error` — Error messages
- `critical` — Critical errors
- `silent` — Disables all logging

### Setting Log Levels

You can set the log level in several ways:

#### 1. Environment Variable

```bash
export LOG_LEVEL=debug
python my_app.py
```

#### 2. Programmatically

```python
logger.setLevel("debug")  # Case-insensitive
logger.setLevel(logging.DEBUG)  # Or use logging constants
```

#### 3. Using Context Manager

Temporarily change the log level for a specific block:

```python
with logger.use_level("debug"):
    logger.debug("This will be shown")
    logger.trace("This will also be shown if trace is enabled")
```

## Colorized Output

Apathetic Python Logger automatically detects if your terminal supports colors and enables colorized output by default.

### Color Detection

Colors are enabled when:
- Output is a TTY (terminal)
- `FORCE_COLOR` environment variable is set to `1`, `true`, or `yes`

Colors are disabled when:
- `NO_COLOR` environment variable is set
- Output is redirected to a file or pipe

### Manual Control

```python
from apathetic_logger import ApatheticLogger

# Create logger with colors explicitly enabled/disabled
logger = ApatheticLogger("my_app", enable_color=True)
```

## Tag Formatting

Log messages are automatically prefixed with tags:

- `[TRACE]` — Gray tag
- `[DEBUG]` — Cyan tag
- `⚠️` — Warning emoji
- `❌` — Error emoji
- `💥` — Critical emoji

## Dual-Stream Handling

Apathetic Python Logger automatically routes log messages to the appropriate stream:

- **stdout** — Used for normal output
- **stderr** — Used for errors and warnings

This ensures proper separation of output and error streams, which is important for CLI tools.

## Advanced Features

### Dynamic Log Levels

Log at different levels dynamically:

```python
logger.log_dynamic("warning", "This is a warning")
logger.log_dynamic(logging.ERROR, "This is an error")
```

### Conditional Exception Logging

Only show full tracebacks when debug mode is enabled:

```python
try:
    risky_operation()
except Exception:
    logger.error_if_not_debug("Operation failed")
    # Full traceback only shown if debug/trace is enabled
```

### Temporary Level Changes

Use a context manager to temporarily change log levels:

```python
# Only set level if it's more verbose (won't downgrade from trace to debug)
with logger.use_level("debug", minimum=True):
    logger.debug("This will be shown")
```

## Integration with CLI Tools

For command-line applications, you can integrate with `argparse`:

```python
import argparse
from apathetic_logger import get_logger, register_logger_name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args()
    
    register_logger_name("my_cli")
    logger = get_logger()
    
    # Logger will automatically use args.log_level
    logger.determine_log_level(args=args)
    logger.setLevel(logger.determine_log_level(args=args))
    
    logger.info("CLI tool started")
```

## Next Steps

- Read the [API Reference]({{ '/api' | relative_url }}) for complete documentation
- Check out [Examples]({{ '/examples' | relative_url }}) for more advanced patterns
- See [Contributing]({{ '/contributing' | relative_url }}) if you want to help improve the project

