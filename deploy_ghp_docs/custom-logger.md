---
layout: default
title: Custom Logger Example
permalink: /custom-logger/
---

# Creating a Custom Logger

This guide shows how to create a custom logger subclass for your application, allowing you to extend `ApatheticLogger` with application-specific behavior.

## Why Create a Custom Logger?

Creating a custom logger subclass allows you to:

- **Customize log level resolution** - Add application-specific logic for determining log levels
- **Add application-specific methods** - Extend the logger with domain-specific logging methods
- **Provide type hints** - Create a typed getter function that returns your custom logger type
- **Centralize configuration** - Set up environment variables and defaults in one place

## Complete Example

Here's a complete example of creating a custom `AppLogger` for your application:

```python
# src/myapp/logs.py

import argparse
import logging
import os
from typing import cast

from apathetic_logger import (
    ApatheticLogger,
    get_logger,
    register_default_log_level,
    register_log_level_env_vars,
    register_logger_name,
)

# Application-specific constants
APP_NAME = "myapp"
DEFAULT_LOG_LEVEL = "info"
LOG_LEVEL_ENV_VAR = f"{APP_NAME.upper()}_LOG_LEVEL"


# --- Custom Logger Class -----------------------------------------------------


class AppLogger(ApatheticLogger):
    """Application-specific logger with custom log level resolution."""
    
    def determine_log_level(
        self,
        *,
        args: argparse.Namespace | None = None,
        root_log_level: str | None = None,
    ) -> str:
        """Resolve log level from CLI → env → root config → default.
        
        Priority order:
        1. Command-line argument (args.log_level)
        2. Environment variable (MYAPP_LOG_LEVEL or LOG_LEVEL)
        3. Root logger level
        4. Application default
        """
        # Check command-line arguments first
        if args is not None:
            args_level = getattr(args, "log_level", None)
            if args_level is not None and args_level:
                return str(args_level).upper()
        
        # Check environment variables (registered ones are checked automatically)
        # This will check MYAPP_LOG_LEVEL, then LOG_LEVEL
        env_vars = [LOG_LEVEL_ENV_VAR, "LOG_LEVEL"]
        for env_var in env_vars:
            env_log_level = os.getenv(env_var)
            if env_log_level:
                return env_log_level.upper()
        
        # Fall back to root logger level if set
        if root_log_level:
            return root_log_level.upper()
        
        # Use application default
        return DEFAULT_LOG_LEVEL.upper()


# --- Logger Initialization ----------------------------------------------------

# Extend the logging module to support TRACE and SILENT levels
# This must happen before any loggers are created
AppLogger.extend_logging_module()

# Register environment variables for log level detection
# These will be checked in order by determine_log_level()
register_log_level_env_vars([LOG_LEVEL_ENV_VAR, "LOG_LEVEL"])

# Register the default log level
register_default_log_level(DEFAULT_LOG_LEVEL)

# Register the logger name
# This allows get_logger() to find the logger instance
register_logger_name(APP_NAME)

# Get the logger instance from the logging registry
# The logging module acts as the registry, so we use logging.getLogger()
_APP_LOGGER = cast("AppLogger", logging.getLogger(APP_NAME))


# --- Application Logger Getter ------------------------------------------------


def get_app_logger() -> AppLogger:
    """Return the configured application logger.
    
    This is the application-specific logger getter that returns AppLogger type.
    Use this in application code instead of apathetic_logger.get_logger() for
    better type hints and to ensure you're using the custom logger.
    
    Returns:
        The AppLogger instance for this application
        
    Example:
        >>> from myapp.logs import get_app_logger
        >>> logger = get_app_logger()
        >>> logger.info("Application started")
    """
    logger = cast("AppLogger", get_logger())
    return logger
```

## Using the Custom Logger

Once you've set up your custom logger, use it throughout your application:

```python
# src/myapp/main.py

import argparse
from myapp.logs import get_app_logger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["trace", "debug", "info", "warning", "error", "critical", "silent"],
        help="Set the log level",
    )
    args = parser.parse_args()
    
    # Get the custom logger
    logger = get_app_logger()
    
    # Set log level from command-line arguments
    # The logger's determine_log_level() method will handle this
    log_level = logger.determine_log_level(args=args)
    logger.setLevel(log_level)
    
    # Use the logger
    logger.info("Application started")
    logger.debug("Debug information")
    
    # Your application logic here
    process_data()
    
    logger.info("Application completed successfully")

if __name__ == "__main__":
    main()
```

## Setting Log Levels

With the custom logger, log levels can be set in multiple ways:

### 1. Command-Line Argument

```bash
python myapp.py --log-level debug
```

### 2. Environment Variable

```bash
export MYAPP_LOG_LEVEL=debug
python myapp.py
```

Or use the generic `LOG_LEVEL`:

```bash
export LOG_LEVEL=debug
python myapp.py
```

### 3. Programmatically

```python
logger = get_app_logger()
logger.setLevel("debug")
```

## Extending the Custom Logger

You can add custom methods to your logger subclass:

```python
class AppLogger(ApatheticLogger):
    """Application-specific logger."""
    
    def log_operation(self, operation: str, status: str) -> None:
        """Log an operation with consistent formatting."""
        self.info(f"[{operation}] Status: {status}")
    
    def log_performance(self, metric: str, value: float) -> None:
        """Log performance metrics."""
        if self.isEnabledFor(logging.DEBUG):
            self.debug(f"Performance: {metric} = {value:.2f}")
```

## Key Points

1. **Call `extend_logging_module()`** - This must be called before creating any loggers to register TRACE and SILENT levels.

2. **Register environment variables** - Use `register_log_level_env_vars()` to tell the logger which environment variables to check.

3. **Register default log level** - Use `register_default_log_level()` to set the fallback log level.

4. **Register logger name** - Use `register_logger_name()` so `get_logger()` can find your logger.

5. **Use type casting** - When getting the logger from `logging.getLogger()`, cast it to your custom type for proper type hints.

6. **Create a typed getter** - Provide a `get_app_logger()` function that returns your custom logger type for better IDE support.

## Integration with Existing Code

If you're migrating from the base `ApatheticLogger`, you can gradually adopt the custom logger:

```python
# Old code (still works)
from apathetic_logger import get_logger
logger = get_logger()

# New code (better type hints)
from myapp.logs import get_app_logger
logger = get_app_logger()  # Returns AppLogger type
```

Both will return the same logger instance, but the custom getter provides better type hints and ensures you're using the application-specific logger.

