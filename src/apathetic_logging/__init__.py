# src/apathetic_logging/__init__.py
"""Apathetic Logging implementation."""

from typing import TYPE_CHECKING, TypeAlias, cast


if TYPE_CHECKING:
    from .logger_namespace import ApatheticLogging_Internal_Logger
    from .namespace import apathetic_logging as _apathetic_logging_class

# Get reference to the namespace class
# In stitched mode: class is already defined in namespace.py (executed before this)
# In installed mode: import from namespace module
_is_standalone = globals().get("__STANDALONE__", False)

if _is_standalone:
    # Stitched mode: class already defined in namespace.py
    # Get reference to the class (it's already in globals from namespace.py)
    _apathetic_logging_raw = globals().get("apathetic_logging")
    if _apathetic_logging_raw is None:
        # Fallback: should not happen, but handle gracefully
        msg = "apathetic_logging class not found in standalone mode"
        raise RuntimeError(msg)
    # Type cast to help mypy understand this is the apathetic_logging class
    # The import gives us type[apathetic_logging], so cast to
    # type[_apathetic_logging_class]
    apathetic_logging = cast("type[_apathetic_logging_class]", _apathetic_logging_raw)
else:
    # Installed mode: import from namespace module
    # This block is only executed in installed mode, not in standalone builds
    from .namespace import apathetic_logging

    # Ensure the else block is not empty (build script may remove import)
    _ = apathetic_logging

# Export all namespace items for convenience
# These are aliases to apathetic_logging.*
#
# Note: In embedded builds, __init__.py is excluded from the stitch,
# so this code never runs and no exports happen (only the class is available).
# In singlefile/installed builds, __init__.py is included, so exports happen.
DEFAULT_APATHETIC_LOG_LEVEL = apathetic_logging.DEFAULT_APATHETIC_LOG_LEVEL
DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS = (
    apathetic_logging.DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS
)
LEVEL_ORDER = apathetic_logging.LEVEL_ORDER
SILENT_LEVEL = apathetic_logging.SILENT_LEVEL
TAG_STYLES = apathetic_logging.TAG_STYLES
TEST_LEVEL = apathetic_logging.TEST_LEVEL
safeTrace = apathetic_logging.safeTrace
SAFE_TRACE_ENABLED = apathetic_logging.SAFE_TRACE_ENABLED
TRACE_LEVEL = apathetic_logging.TRACE_LEVEL
MINIMAL_LEVEL = apathetic_logging.MINIMAL_LEVEL
DETAIL_LEVEL = apathetic_logging.DETAIL_LEVEL
NOTSET_LEVEL = apathetic_logging.NOTSET_LEVEL

# ANSI Colors
ANSIColors = apathetic_logging.ANSIColors

# Classes
DualStreamHandler = apathetic_logging.DualStreamHandler
TagFormatter = apathetic_logging.TagFormatter
# Logger is a nested class in ApatheticLogging_Internal_Logger that
# inherits from logging.Logger.
# Use TypeAlias to help mypy understand this is a class type.
if TYPE_CHECKING:
    Logger: TypeAlias = ApatheticLogging_Internal_Logger.Logger
else:
    Logger = apathetic_logging.Logger

# Functions (camelCase - stdlib wrappers)
addLevelName = apathetic_logging.addLevelName
basicConfig = apathetic_logging.basicConfig
captureWarnings = apathetic_logging.captureWarnings
currentframe = apathetic_logging.currentframe
getHandlerByName = apathetic_logging.getHandlerByName
getHandlerNames = apathetic_logging.getHandlerNames
getLevelName = apathetic_logging.getLevelName
getLevelNamesMapping = apathetic_logging.getLevelNamesMapping
getLogRecordFactory = apathetic_logging.getLogRecordFactory
getLogger = apathetic_logging.getLogger
getLoggerClass = apathetic_logging.getLoggerClass
makeLogRecord = apathetic_logging.makeLogRecord
setLogRecordFactory = apathetic_logging.setLogRecordFactory
setLoggerClass = apathetic_logging.setLoggerClass

# Functions (camelCase - library functions)
getDefaultLogLevel = apathetic_logging.getDefaultLogLevel
getDefaultLoggerName = apathetic_logging.getDefaultLoggerName
getDefaultPropagate = apathetic_logging.getDefaultPropagate
getLevelNumber = apathetic_logging.getLevelNumber
getLogLevelEnvVars = apathetic_logging.getLogLevelEnvVars
getLoggerOfType = apathetic_logging.getLoggerOfType
getRegisteredLoggerName = apathetic_logging.getRegisteredLoggerName
getTargetPythonVersion = apathetic_logging.getTargetPythonVersion
hasLogger = apathetic_logging.hasLogger
makeSafeTrace = apathetic_logging.makeSafeTrace
registerDefaultLogLevel = apathetic_logging.registerDefaultLogLevel
registerLogLevelEnvVars = apathetic_logging.registerLogLevelEnvVars
registerLogger = apathetic_logging.registerLogger
registerPropagate = apathetic_logging.registerPropagate
registerTargetPythonVersion = apathetic_logging.registerTargetPythonVersion
removeLogger = apathetic_logging.removeLogger
safeLog = apathetic_logging.safeLog

# Functions (snake_case - stdlib wrappers)
add_level_name = apathetic_logging.add_level_name
basic_config = apathetic_logging.basic_config
capture_warnings = apathetic_logging.capture_warnings
critical = apathetic_logging.critical
currentframe = apathetic_logging.currentframe
debug = apathetic_logging.debug
disable = apathetic_logging.disable
error = apathetic_logging.error
exception = apathetic_logging.exception
fatal = apathetic_logging.fatal
get_handler_by_name = apathetic_logging.get_handler_by_name
get_handler_names = apathetic_logging.get_handler_names
get_level_name = apathetic_logging.get_level_name
get_level_names_mapping = apathetic_logging.get_level_names_mapping
get_logger = apathetic_logging.get_logger
get_logger_class = apathetic_logging.get_logger_class
get_log_record_factory = apathetic_logging.get_log_record_factory
info = apathetic_logging.info
log = apathetic_logging.log
make_log_record = apathetic_logging.make_log_record
set_logger_class = apathetic_logging.set_logger_class
set_log_record_factory = apathetic_logging.set_log_record_factory
shutdown = apathetic_logging.shutdown
warn = apathetic_logging.warn
warning = apathetic_logging.warning

# Functions (snake_case - library wrappers)
get_default_log_level = apathetic_logging.get_default_log_level
get_default_logger_name = apathetic_logging.get_default_logger_name
get_default_propagate = apathetic_logging.get_default_propagate
get_level_number = apathetic_logging.get_level_number
get_log_level_env_vars = apathetic_logging.get_log_level_env_vars
get_logger_of_type = apathetic_logging.get_logger_of_type
get_registered_logger_name = apathetic_logging.get_registered_logger_name
get_target_python_version = apathetic_logging.get_target_python_version
has_logger = apathetic_logging.has_logger
make_safe_trace = apathetic_logging.make_safe_trace
register_default_log_level = apathetic_logging.register_default_log_level
register_log_level_env_vars = apathetic_logging.register_log_level_env_vars
register_logger = apathetic_logging.register_logger
register_propagate = apathetic_logging.register_propagate
register_target_python_version = apathetic_logging.register_target_python_version
remove_logger = apathetic_logging.remove_logger
safe_log = apathetic_logging.safe_log
safe_trace = apathetic_logging.safe_trace


__all__ = [
    "DEFAULT_APATHETIC_LOG_LEVEL",
    "DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS",
    "DETAIL_LEVEL",
    "LEVEL_ORDER",
    "MINIMAL_LEVEL",
    "NOTSET_LEVEL",
    "SAFE_TRACE_ENABLED",
    "SILENT_LEVEL",
    "TAG_STYLES",
    "TEST_LEVEL",
    "TRACE_LEVEL",
    "ANSIColors",
    "DualStreamHandler",
    "Logger",
    "TagFormatter",
    "addLevelName",
    "add_level_name",
    "apathetic_logging",
    "basicConfig",
    "basic_config",
    "captureWarnings",
    "capture_warnings",
    "critical",
    "currentframe",
    "debug",
    "disable",
    "error",
    "exception",
    "fatal",
    "getDefaultLogLevel",
    "getDefaultLoggerName",
    "getDefaultPropagate",
    "getHandlerByName",
    "getHandlerNames",
    "getLevelName",
    "getLevelNamesMapping",
    "getLevelNumber",
    "getLogLevelEnvVars",
    "getLogRecordFactory",
    "getLogger",
    "getLoggerClass",
    "getLoggerOfType",
    "getRegisteredLoggerName",
    "getTargetPythonVersion",
    "get_default_log_level",
    "get_default_logger_name",
    "get_default_propagate",
    "get_handler_by_name",
    "get_handler_names",
    "get_level_name",
    "get_level_names_mapping",
    "get_level_number",
    "get_log_level_env_vars",
    "get_log_record_factory",
    "get_logger",
    "get_logger_class",
    "get_logger_of_type",
    "get_registered_logger_name",
    "get_target_python_version",
    "hasLogger",
    "has_logger",
    "info",
    "log",
    "makeLogRecord",
    "makeSafeTrace",
    "make_log_record",
    "make_safe_trace",
    "registerDefaultLogLevel",
    "registerLogLevelEnvVars",
    "registerLogger",
    "registerPropagate",
    "registerTargetPythonVersion",
    "register_default_log_level",
    "register_log_level_env_vars",
    "register_logger",
    "register_propagate",
    "register_target_python_version",
    "removeLogger",
    "remove_logger",
    "safeLog",
    "safeTrace",
    "safe_log",
    "safe_trace",
    "setLogRecordFactory",
    "setLoggerClass",
    "set_log_record_factory",
    "set_logger_class",
    "shutdown",
    "warn",
    "warning",
]
