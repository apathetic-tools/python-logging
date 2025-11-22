# src/apathetic_logging/logging_utils.py
"""Logging utilities for Apathetic Logging.

Docstrings are adapted from the standard library logging module documentation
licensed under the Python Software Foundation License Version 2.
"""

from __future__ import annotations

import inspect
import logging
import sys
from types import FrameType
from typing import TypeVar


class ApatheticLogging_Internal_LoggingUtils:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides helper functions for the standard logging module.

    This class contains utility functions that operate directly on or replace
    standard library `logging.*` utilities and functions. These helpers extend
    or wrap the built-in logging module functionality to provide enhanced
    capabilities or safer alternatives.

    When mixed into apathetic_logging, it provides utility functions that
    interact with Python's standard logging module.
    """

    _LoggerType = TypeVar("_LoggerType", bound=logging.Logger)

    @staticmethod
    def getLevelName(level: int | str, *, strict: bool = False) -> str:
        """Return the textual representation of a logging level.

        Extended version of logging.getLevelName that always returns a string.

        **Breaking change from stdlib**: Unlike `logging.getLevelName` which is
        bidirectional (returns str for int input, int for str input), this function
        always returns a string. The stdlib's string->int behavior was considered
        an undocumented mistake and removed in Python 3.4, but reinstated in 3.4.2
        for backward compatibility. While not deprecated, this behavior is not endorsed.
        This function provides the cleaner, intended API.

        For string->int conversion, use `getLevelNumber()` instead.

        Extended features:
        - Always returns a string (unlike stdlib which returns int for string input)
        - Accepts both int and str inputs (returns str uppercased if already str)
        - Optional strict mode to raise ValueError for unknown levels
        - Supports all levels registered via logging.addLevelName() (including
          custom apathetic levels and user-registered levels)

        Args:
            level: Log level as integer or string name
            strict: If True, raise ValueError for unknown levels. If False (default),
                returns "Level {level}" format for unknown integer levels (matching
                stdlib behavior).

        Returns:
            Level name (uppercase string). If level is already a string,
            returns it as-is (uppercased). For unknown integer levels (when
            strict=False), returns "Level {level}" format (e.g., "Level 999").

        Raises:
            ValueError: If strict=True and level cannot be resolved to a known
                level name.

        Example:
            >>> getLevelName(10)
            "DEBUG"
            >>> getLevelName(5)
            "TRACE"
            >>> getLevelName("DEBUG")
            "DEBUG"
            >>> getLevelName(999)
            "Level 999"
            >>> getLevelName(999, strict=True)
            ValueError: Unknown log level: 999
            >>> getLevelNumber("DEBUG")  # For string->int conversion
            10

        Wrapper for logging.getLevelName with extensions.

        https://docs.python.org/3.10/library/logging.html#logging.getLevelName
        """
        # If already a string, return it uppercased
        if isinstance(level, str):
            return level.upper()

        # Use logging.getLevelName() which handles all registered levels:
        # - Standard library levels (DEBUG, INFO, etc.)
        # - Custom apathetic levels (TEST, TRACE, etc.)
        #   registered via extendLoggingModule()
        # - User-registered levels via logging.addLevelName()
        level_name = logging.getLevelName(level)
        # getLevelName returns "Level {level}" format for unknown levels
        # Check if this is a known level (not in "Level {number}" format)
        if level_name.startswith("Level "):
            # Unknown level: raise if strict, otherwise return stdlib format
            if strict:
                msg = f"Unknown log level: {level}"
                raise ValueError(msg)
            return level_name

        # Known level (from stdlib, our custom levels, or user-registered levels)
        return level_name

    @staticmethod
    def getLevelNumber(level: str | int) -> int:
        """Convert a log level name to its numeric value.

        Recommended way to convert string level names to integers. This function
        explicitly performs string->int conversion, unlike `getLevelName()` which
        has bidirectional behavior for backward compatibility.

        Handles all levels registered via logging.addLevelName() (including
        standard library levels, custom apathetic levels, and user-registered levels).

        Args:
            level: Log level as string name (case-insensitive) or integer

        Returns:
            Integer level value

        Raises:
            ValueError: If level cannot be resolved

        Example:
            >>> getLevelNumber("DEBUG")
            10
            >>> getLevelNumber("TRACE")
            5
            >>> getLevelNumber(20)
            20

        See Also:
            getLevelName() - Convert int to string (intended use)
        """
        if isinstance(level, int):
            return level

        level_str = level.upper()

        # Use getattr() to find level constants registered via logging.addLevelName():
        # - Standard library levels (DEBUG, INFO, etc.) - registered by default
        # - Custom apathetic levels (TEST, TRACE, etc.)
        #   registered via extendLoggingModule()
        # - User-registered levels via our addLevelName() method
        #   (but not stdlib's logging.addLevelName() which doesn't set attribute)
        # - User-registered levels via setattr(logging, level_str, value)
        resolved = getattr(logging, level_str, None)
        if isinstance(resolved, int):
            return resolved

        msg = f"Unknown log level: {level!r}"
        raise ValueError(msg)

    @staticmethod
    def hasLogger(logger_name: str) -> bool:
        """Check if a logger exists in the logging manager's registry.

        Args:
            logger_name: The name of the logger to check.

        Returns:
            True if the logger exists in the registry, False otherwise.
        """
        return logger_name in logging.Logger.manager.loggerDict

    @staticmethod
    def removeLogger(logger_name: str) -> None:
        """Remove a logger from the logging manager's registry.

        Args:
            logger_name: The name of the logger to remove.
        """
        logging.Logger.manager.loggerDict.pop(logger_name, None)

    @staticmethod
    def _extract_top_level_package(package: str | None) -> str | None:
        """Extract top-level package name from package string.

        Args:
            package: Package string (e.g., "myapp.submodule") or None

        Returns:
            Top-level package name (e.g., "myapp") or None if package is None
        """
        if package is None:
            return None
        if "." in package:
            return package.split(".", 1)[0]
        return package

    @staticmethod
    def _infer_from_frame(skip_frames: int, frame: FrameType | None) -> str | None:
        """Infer logger name from caller's frame.

        Args:
            skip_frames: Number of frames to skip to get to actual caller
            frame: Frame to start from, or None

        Returns:
            Inferred logger name or None if cannot be inferred
        """
        if frame is None:
            return None
        try:
            # Skip the specified number of frames to get to the actual caller
            caller_frame = frame.f_back
            for _ in range(skip_frames):
                if caller_frame is None:
                    break
                caller_frame = caller_frame.f_back
            if caller_frame is None:
                return None
            caller_package = caller_frame.f_globals.get("__package__")
            return ApatheticLogging_Internal_LoggingUtils._extract_top_level_package(
                caller_package
            )
        finally:
            del frame

    @staticmethod
    def getDefaultLoggerName(
        logger_name: str | None = None,
        *,
        check_registry: bool = True,
        skip_frames: int = 1,
        raise_on_error: bool = False,
        infer: bool = True,
        register: bool = False,
    ) -> str | None:
        """Get default logger name with optional inference from caller's frame.

        This function handles the common pattern of:
        1. Using explicit name if provided
        2. Checking registry if requested
        3. Inferring from caller's frame if needed (when infer=True)
        4. Storing inferred name in registry (when register=True)
        5. Returning None or raising error if still unresolved

        Args:
            logger_name: Explicit logger name, or None to infer.
            check_registry: If True, check registry before inferring. Use False
                when the caller should actively determine the name from current
                context (e.g., registerLogger() which should re-infer even
                if a name is already registered). Use True when the caller should
                use a previously registered name if available (e.g., getLogger()
                which should use the registered name).
            skip_frames: Number of frames to skip from this function to get to
                the actual caller. Default is 1 (skips this function's frame).
            raise_on_error: If True, raise RuntimeError if logger name cannot be
                resolved. If False (default), return None instead. Use True when
                a logger name is required (e.g., when creating a logger).
            infer: If True (default), attempt to infer logger name from caller's
                frame when not found in registry. If False, skip inference and
                return None if not found in registry.
            register: If True, store inferred name in registry. If False (default),
                do not modify registry. Note: Explicit names are never stored regardless
                of this parameter.

        Returns:
            Resolved logger name, or None if cannot be resolved and
            raise_on_error=False.

        Raises:
            RuntimeError: If logger name cannot be resolved and raise_on_error=True.
        """
        # Import locally to avoid circular import
        from .registry_data import (  # noqa: PLC0415
            ApatheticLogging_Internal_RegistryData,
        )

        _registry_data = ApatheticLogging_Internal_RegistryData

        # If explicit name provided, return it (never store explicit names)
        # Note: Empty string ("") is a special case - it represents the root logger
        # and is returned as-is to match standard library behavior.
        if logger_name is not None:
            return logger_name

        # Check registry if requested
        if check_registry:
            registered_name = _registry_data.registered_internal_logger_name
            if registered_name is not None:
                return registered_name

        # Try to infer from caller's frame if inference is enabled
        if not infer:
            # Inference disabled - return None or raise error
            if raise_on_error:
                error_msg = (
                    "Cannot resolve logger name: not in registry and inference "
                    "is disabled. Please call registerLogger() with an "
                    "explicit logger name or enable inference."
                )
                raise RuntimeError(error_msg)
            return None

        # Get current frame (this function's frame) and skip to caller
        frame = inspect.currentframe()
        inferred_name = ApatheticLogging_Internal_LoggingUtils._infer_from_frame(
            skip_frames, frame
        )

        # Store inferred name in registry if requested
        if inferred_name is not None and register:
            _registry_data.registered_internal_logger_name = inferred_name

        # Return inferred name or handle error
        if inferred_name is not None:
            return inferred_name

        # Handle error case
        if raise_on_error:
            error_msg = (
                "Cannot auto-infer logger name: __package__ is not set in the "
                "calling module. Please call registerLogger() with an "
                "explicit logger name."
            )
            raise RuntimeError(error_msg)

        return None

    @staticmethod
    def checkPythonVersionRequirement(
        required_version: tuple[int, int],
        function_name: str,
    ) -> None:
        """Check if the target or runtime Python version meets the requirement.

        This method validates that a function requiring a specific Python version
        can be called safely. It checks:
        1. Target version (if set via registerTargetPythonVersion), otherwise
           falls back to MIN_PYTHON_VERSION from constants
        2. Runtime version (as a safety net to catch actual runtime issues)

        This allows developers to catch version incompatibilities during development
        even when running on a newer Python version than their target.

        Args:
            required_version: Minimum Python version required (major, minor) tuple
            function_name: Name of the function being checked (for error messages)

        Raises:
            NotImplementedError: If target version or runtime version doesn't meet
                the requirement. Error message includes guidance on raising target
                version if applicable.

        Example:
            >>> checkPythonVersionRequirement((3, 11), "get_level_names_mapping")
            # Raises if target version < 3.11 or runtime version < 3.11
        """
        # Import locally to avoid circular imports
        from .constants import (  # noqa: PLC0415
            ApatheticLogging_Internal_Constants,
        )
        from .registry_data import (  # noqa: PLC0415
            ApatheticLogging_Internal_RegistryData,
        )

        _constants = ApatheticLogging_Internal_Constants
        _registry_data = ApatheticLogging_Internal_RegistryData

        # Determine effective target version
        # If target version is set, use it; otherwise fall back to MIN_PYTHON_VERSION
        target_version = _registry_data.registered_internal_target_python_version
        if target_version is None:
            target_version = _constants.MIN_PYTHON_VERSION

        # Check target version first (primary check)
        if target_version < required_version:
            req_major, req_minor = required_version
            tgt_major, tgt_minor = target_version
            msg = (
                f"{function_name} requires Python {req_major}.{req_minor}+, "
                f"but target version is {tgt_major}.{tgt_minor}. "
                f"To use this function, call "
                f"registerTargetPythonVersion(({req_major}, {req_minor})) "
                f"or raise your target version to at least {req_major}.{req_minor}."
            )
            raise NotImplementedError(msg)

        # Check runtime version as safety net
        runtime_version = (sys.version_info.major, sys.version_info.minor)
        if runtime_version < required_version:
            req_major, req_minor = required_version
            rt_major, rt_minor = runtime_version
            msg = (
                f"{function_name} requires Python {req_major}.{req_minor}+, "
                f"but runtime version is {rt_major}.{rt_minor}. "
                f"This function is not available in your Python version."
            )
            raise NotImplementedError(msg)
