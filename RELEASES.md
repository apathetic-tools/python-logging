# Releases

## v0.1.0 - Initial Release

### 🎉 What's New

#### Core Functions

- **`registerLogger(name)`** - Register a logger name for use by `getLogger()`
- **`getLogger(name=None)`** - Get a logger instance (uses registered name if available)
- **`getLoggerOfType(logger_type, name=None)`** - Get a logger of a specific type
- **`registerDefaultLogLevel(level)`** - Set the default log level
- **`registerLogLevelEnvVars(*env_vars)`** - Register environment variables to check for log level
- **`registerCompatibilityMode(enabled)`** - Enable/disable stdlib compatibility mode
- **`registerPropagate(propagate)`** - Set default propagate setting for loggers
- **`registerTargetPythonVersion(version)`** - Register target Python version for compatibility

#### Logger Management

- **`hasLogger(name)`** - Check if a logger exists in the registry
- **`removeLogger(name)`** - Remove a logger from the registry
- **`getRegisteredLoggerName()`** - Get the currently registered logger name
- **`getDefaultLoggerName()`** - Get default logger name with optional inference

#### Logging Utilities

- **`getLevelNumber(level)`** - Get numeric value for a log level
- **`getLevelNameStr(level)`** - Get string name for a log level
- **`getLogLevelEnvVars()`** - Get registered environment variable names
- **`getDefaultLogLevel()`** - Get the registered default log level
- **`getCompatibilityMode()`** - Get compatibility mode setting
- **`getTargetPythonVersion()`** - Get target Python version
- **`getDefaultPropagate()`** - Get default propagate setting

#### Safe Logging

- **`safeLog(level, message, *args, **kwargs)`** - Emergency logger that never fails
- **`safeTrace(message, icon='🔍')`** - Debug tracing function for test development
- **`makeSafeTrace(icon='🔍')`** - Create a test trace function with a custom icon

---

**Note**: This release includes a single-file build (`apathetic_logging.py`) attached to this release for easy embedding in projects that need a standalone logging solution.

