# src/apathetic_logging/registry_data.py
"""Registry for configurable log level settings."""

from __future__ import annotations


class ApatheticLogging_Internal_RegistryData:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides registry storage for configurable settings.

    This class contains class-level attributes for storing registered configuration
    values. When mixed into apathetic_logging, it provides centralized storage for
    log level environment variables, default log level, logger name, target
    Python version, and propagate setting.

    Other mixins access these registries via direct class reference:
    ``ApatheticLogging_Internal_RegistryData.registered_internal_*``
    """

    # Registry for configurable log level settings
    # These are class-level attributes to avoid module-level namespace pollution
    # Public but marked with _internal_ to indicate internal use by other mixins
    registered_internal_log_level_env_vars: list[str] | None = None
    """Environment variable names to check for log level configuration.

    If None, falls back to DEFAULT_APATHETIC_LOG_LEVEL_ENV_VARS from constants.py.
    The environment variables are checked in order, and the first non-empty value
    found is used. Set via registerLogLevelEnvVars() or register_log_level_env_vars().
    """
    registered_internal_default_log_level: str | None = None
    """Default log level to use when no other source is found.

    If None, falls back to DEFAULT_APATHETIC_LOG_LEVEL from constants.py.
    Used when no environment variable is set and no root log level is provided.
    Set via registerDefaultLogLevel() or register_default_log_level().
    """
    registered_internal_logger_name: str | None = None
    """Registered logger name to use for logger name inference.

    If None, logger names are inferred from the calling module's __package__
    attribute. When set, this value is returned by getDefaultLoggerName() instead
    of inferring from the call stack. Set via registerLogger() or register_logger().
    """
    registered_internal_target_python_version: tuple[int, int] | None = None
    """Target Python version (major, minor) for compatibility checking.

    If None, falls back to TARGET_PYTHON_VERSION from constants.py.
    Used to validate function calls against target version, not just runtime version.
    """
    registered_internal_propagate: bool | None = None
    """Propagate setting for loggers.

    If None, falls back to DEFAULT_PROPAGATE from constants.py.
    When False, loggers do not propagate messages to parent loggers.
    """
    registered_internal_compatibility_mode: bool | None = None
    """Compatibility mode setting for stdlib drop-in replacement.

    If None, defaults to False (current improved behavior).
    When True, restores stdlib-compatible behavior where possible
    (e.g., getLogger(None) returns root logger).
    Set via registerCompatibilityMode() or register_compatibility_mode().
    """
