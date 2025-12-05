---
layout: base
title: Custom Logger Example
permalink: /custom-logger/
---

# Creating a Custom Logger

This guide shows how to create a custom logger subclass for your application, allowing you to extend `apathetic_logging` with application-specific behavior.

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

from apathetic_logging import (
    Logger as ApatheticLogger,
    registerDefaultLogLevel,
    registerLogLevelEnvVars,
    registerLogger,
)

# Application-specific constants
APP_NAME = "myapp"
DEFAULT_LOG_LEVEL = "info"
LOG_LEVEL_ENV_VAR = f"{APP_NAME.upper()}_LOG_LEVEL"


# --- Custom Logger Class -----------------------------------------------------


class AppLogger(ApatheticLogger):
    """Application-specific logger with custom log level resolution."""
    
    def determineLogLevel(
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
# NOTE: This is now optional! getLoggerOfType() will automatically call
# extendLoggingModule() on AppLogger if needed. However, calling it explicitly
# here is still recommended for:
# - Immediate availability of logging.TRACE, logging.DETAIL, etc. after import
# - Better performance (one-time setup at import time)
# - Clear documentation of when the module is extended
AppLogger.extendLoggingModule()

# Register environment variables for log level detection
# These will be checked in order by determineLogLevel()
registerLogLevelEnvVars([LOG_LEVEL_ENV_VAR, "LOG_LEVEL"])

# Register the default log level
registerDefaultLogLevel(DEFAULT_LOG_LEVEL)

# Register the logger
# This allows getLogger() and getLoggerOfType() to find the logger instance
# NOTE: This is also optional if you always pass the logger name explicitly
# to get_app_logger(), but recommended for consistency
# This also automatically extends the logging module with AppLogger
registerLogger(APP_NAME, AppLogger)


# --- Application Logger Getter ------------------------------------------------


def get_app_logger(logger_name: str = APP_NAME) -> AppLogger:
    """Return the configured application logger.
    
    This is the application-specific logger getter that returns AppLogger type.
    Use this in application code instead of apathetic_logging.getLogger() for
    better type hints and to ensure you're using the custom logger.
    
    Args:
        logger_name: The name of the logger to retrieve (defaults to APP_NAME)
    
    Returns:
        The AppLogger instance for this application
        
    Example:
        >>> from myapp.logs import get_app_logger
        >>> logger = get_app_logger()
        >>> logger.info("Application started")
    """
    from apathetic_logging import getLoggerOfType
    return getLoggerOfType(logger_name, AppLogger)
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
    # The logger's determineLogLevel() method will handle this
    log_level = logger.determineLogLevel(args=args)
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

1. **Call `extendLoggingModule()` (Optional but Recommended)** - This registers TRACE, DETAIL, BRIEF, and SILENT levels with the logging module. While `getLoggerOfType()` will automatically call this on your logger class if needed, calling it explicitly is recommended for:
   - Immediate availability of `logging.TRACE`, `logging.DETAIL`, etc. after import
   - Better performance (one-time setup at import time)
   - Clear documentation of when the module is extended
   - If you override `extendLoggingModule()` in your custom logger, calling it explicitly ensures your override runs

2. **Register environment variables** - Use `registerLogLevelEnvVars()` to tell the logger which environment variables to check. This is optional if you handle environment variable checking in your `determineLogLevel()` override.

3. **Register default log level** - Use `registerDefaultLogLevel()` to set the fallback log level. This is optional if you always provide a default in your `determineLogLevel()` override.

4. **Register logger (Optional)** - Use `registerLogger()` so `getLogger()` and `getLoggerOfType()` can auto-infer the logger name. If you always pass the logger name explicitly to `get_app_logger()`, this is optional. You can pass your custom logger class to `registerLogger()` to automatically extend the logging module.

5. **Create a typed getter** - Provide a `get_app_logger()` function that returns your custom logger type for better IDE support. Use the `getLoggerOfType()` helper function for a simple implementation:
     ```python
     def get_app_logger(logger_name: str = APP_NAME) -> AppLogger:
         """Return the configured application logger."""
         from apathetic_logging import getLoggerOfType
         return getLoggerOfType(logger_name, AppLogger)
     ```
     
     The `getLoggerOfType()` helper handles all defensive checks automatically:
     - Automatically calls `AppLogger.extendLoggingModule()` if needed (allowing your override to run)
     - Ensures the logger has the `levelName` attribute (base Logger check)
     - Ensures the logger is an instance of `AppLogger` (subclass check)
     - Fixes the logger type if it was created before `extendLoggingModule()` was called
     - Handles name resolution (from parameter, registry, or auto-inference)

## Integration with Existing Code

If you're migrating from the base `apathetic_logging`, you can gradually adopt the custom logger:

```python
# Old code (still works)
from apathetic_logging import getLogger
logger = getLogger()

# New code (better type hints)
from myapp.logs import get_app_logger
logger = get_app_logger()  # Returns AppLogger type
```

Both will return the same logger instance, but the custom getter provides better type hints and ensures you're using the application-specific logger.

