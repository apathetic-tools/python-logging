---
layout: default
title: Examples
permalink: /examples/
---

# Usage Examples

Advanced usage patterns and examples for Apathetic Python Logger.

## Basic CLI Application

A complete example of a command-line application using Apathetic Python Logger:

```python
#!/usr/bin/env python3
"""Example CLI application with Apathetic Logger."""

import argparse
import sys
from apathetic_logger import get_logger, register_logger_name

def main():
    parser = argparse.ArgumentParser(description="Example CLI tool")
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["trace", "debug", "info", "warning", "error", "critical", "silent"],
        help="Set the log level",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Register logger name
    register_logger_name("example_cli")
    logger = get_logger()
    
    # Set log level from arguments
    if args.verbose:
        logger.setLevel("debug")
    else:
        logger.setLevel(args.log_level)
    
    # Use the logger
    logger.info("Application started")
    logger.debug("Debug information (only shown with --verbose or --log-level debug)")
    
    try:
        # Your application logic here
        result = process_data()
        logger.info(f"Processing complete: {result}")
    except Exception:
        logger.error_if_not_debug("Processing failed")
        sys.exit(1)

def process_data():
    """Example processing function."""
    return "success"

if __name__ == "__main__":
    main()
```

## Context Manager for Temporary Verbosity

Temporarily increase verbosity for specific operations:

```python
from apathetic_logger import get_logger, register_logger_name

register_logger_name("my_app")
logger = get_logger()

# Normal operation
logger.info("Starting operation")

# Temporarily enable debug for a specific block
with logger.use_level("debug"):
    logger.debug("Detailed step 1")
    logger.debug("Detailed step 2")
    logger.trace("Very detailed trace")

# Back to normal level
logger.info("Operation complete")
```

## Conditional Exception Logging

Show full tracebacks only in debug mode:

```python
from apathetic_logger import get_logger, register_logger_name

register_logger_name("my_app")
logger = get_logger()

def risky_operation():
    """An operation that might fail."""
    raise ValueError("Something went wrong")

try:
    risky_operation()
except Exception:
    # Full traceback only if debug/trace is enabled
    logger.error_if_not_debug("Risky operation failed")
    # In production (info level), users see: "❌ Risky operation failed"
    # In development (debug level), users see full traceback
```

## Custom Environment Variables

Register custom environment variables for log level:

```python
from apathetic_logger import (
    get_logger,
    register_logger_name,
    register_log_level_env_vars,
    register_default_log_level,
)

# Use custom environment variable names
register_log_level_env_vars(["MYAPP_LOG_LEVEL", "APP_LOG_LEVEL", "LOG_LEVEL"])

# Set a custom default
register_default_log_level("warning")

register_logger_name("my_app")
logger = get_logger()

# Logger will check MYAPP_LOG_LEVEL, then APP_LOG_LEVEL, then LOG_LEVEL
# If none are set, defaults to "warning"
logger.info("This might not show if default is warning")
```

## Integration with argparse

Seamless integration with argparse for CLI tools:

```python
import argparse
from apathetic_logger import get_logger, register_logger_name

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-level",
        default=None,  # Let logger determine from env/default
        choices=["trace", "debug", "info", "warning", "error", "critical", "silent"],
        help="Set the log level",
    )
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    register_logger_name("my_cli")
    logger = get_logger()
    
    # Determine log level from args, env, or default
    level = logger.determine_log_level(args=args)
    logger.setLevel(level)
    
    logger.info("CLI tool started")
    logger.debug("Debug mode enabled")
```

## Dynamic Log Levels

Log at different levels dynamically:

```python
from apathetic_logger import get_logger, register_logger_name

register_logger_name("my_app")
logger = get_logger()

# Log at different levels based on conditions
def log_result(success: bool, message: str):
    if success:
        logger.log_dynamic("info", message)
    else:
        logger.log_dynamic("error", message)

# Or use numeric levels
import logging
logger.log_dynamic(logging.WARNING, "This is a warning")
```

## Color Customization

Work with colors directly:

```python
from apathetic_logger import ApatheticLogger, CYAN, GREEN, RED

# Create logger with explicit color control
logger = ApatheticLogger("my_app", enable_color=True)

# Use colorize method
colored_text = logger.colorize("Important message", RED)
print(colored_text)

# Or use color constants directly
from apathetic_logger import CYAN, RESET
message = f"{CYAN}This is cyan{RESET}"
print(message)
```

## Testing with Logger

Example of using the logger in tests:

```python
import pytest
from apathetic_logger import get_logger, register_logger_name

@pytest.fixture
def logger():
    register_logger_name("test_app")
    logger = get_logger()
    logger.setLevel("debug")  # Verbose for tests
    return logger

def test_operation(logger):
    logger.info("Starting test")
    # Test logic here
    logger.debug("Test step completed")
    assert True
```

## Silent Mode

Completely disable logging:

```python
from apathetic_logger import get_logger, register_logger_name

register_logger_name("my_app")
logger = get_logger()

# Enable silent mode
logger.setLevel("silent")

# These won't be shown
logger.info("This won't show")
logger.error("This won't show either")
logger.critical("Even this won't show")

# Re-enable logging
logger.setLevel("info")
logger.info("Now this will show")
```

## Multi-Module Application

Using the logger across multiple modules:

```main.py```
```python
from apathetic_logger import register_logger_name
import module_a
import module_b

# Register once at application entry point
register_logger_name("my_app")

# Modules can now use get_logger()
module_a.do_something()
module_b.do_something_else()
```

```module_a.py```
```python
from apathetic_logger import get_logger

logger = get_logger()  # Gets the "my_app" logger

def do_something():
    logger.info("Module A doing something")
```

```module_b.py```
```python
from apathetic_logger import get_logger

logger = get_logger()  # Gets the same "my_app" logger

def do_something_else():
    logger.info("Module B doing something else")
```

## Error Handling with Safe Logging

Use `safe_log` for critical error reporting:

```python
from apathetic_logger import safe_log, get_logger, register_logger_name

register_logger_name("my_app")
logger = get_logger()

def critical_operation():
    try:
        # Some operation that might break logging
        pass
    except Exception as e:
        # If normal logging fails, use safe_log
        try:
            logger.critical(f"Critical error: {e}")
        except Exception:
            # Fallback to safe_log which never fails
            safe_log(f"CRITICAL: {e}")
        raise
```

## Minimum Level Context

Only increase verbosity, never decrease:

```python
from apathetic_logger import get_logger, register_logger_name

register_logger_name("my_app")
logger = get_logger()
logger.setLevel("trace")  # Most verbose

# This won't downgrade to debug (trace is more verbose)
with logger.use_level("debug", minimum=True):
    logger.trace("This will still show (trace is more verbose)")
    logger.debug("This will also show")

# But if current level is info, this will upgrade to debug
logger.setLevel("info")
with logger.use_level("debug", minimum=True):
    logger.debug("This will show (upgraded from info to debug)")
```

These examples demonstrate the flexibility and power of Apathetic Python Logger. 

## Next Steps

- **[API Reference]({{ '/api' | relative_url }})** — Complete API documentation
- **[Quick Start Guide]({{ '/quickstart' | relative_url }})** — Get up and running quickly
- **[Custom Logger Guide]({{ '/custom-logger' | relative_url }})** — Learn how to create application-specific logger subclasses

