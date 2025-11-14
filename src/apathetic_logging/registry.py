# src/apathetic_logging/registry.py
"""Registry for configurable log level settings."""

from __future__ import annotations


class ApatheticLogging_Priv_Registry:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides registry storage for configurable settings.

    This class contains class-level attributes for storing registered configuration
    values. When mixed into apathetic_logging, it provides centralized storage for
    log level environment variables, default log level, and logger name.

    Other mixins access these registries via direct class reference:
    ``ApatheticLogging_Priv_Registry.registered_priv_*``
    """

    # Registry for configurable log level settings
    # These are class-level attributes to avoid module-level namespace pollution
    # Public but marked with _priv_ to indicate internal use by other mixins
    registered_priv_log_level_env_vars: list[str] | None = None
    registered_priv_default_log_level: str | None = None
    registered_priv_logger_name: str | None = None
