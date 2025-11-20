# src/apathetic_logging/logging_utils.py
"""Logging utilities for Apathetic Logging."""

from __future__ import annotations

import inspect
import logging
from types import FrameType
from typing import TypeVar, cast


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
    def has_logger(logger_name: str) -> bool:
        """Check if a logger exists in the logging manager's registry.

        Args:
            logger_name: The name of the logger to check.

        Returns:
            True if the logger exists in the registry, False otherwise.
        """
        return logger_name in logging.Logger.manager.loggerDict

    @staticmethod
    def remove_logger(logger_name: str) -> None:
        """Remove a logger from the logging manager's registry.

        Args:
            logger_name: The name of the logger to remove.
        """
        logging.Logger.manager.loggerDict.pop(logger_name, None)

    @staticmethod
    def set_logger_class_temporarily(
        logger_name: str,
        logger_class: type[ApatheticLogging_Internal_LoggingUtils._LoggerType],
    ) -> ApatheticLogging_Internal_LoggingUtils._LoggerType:
        """Temporarily set the logger class, get/create a logger, then restore.

        This function temporarily sets the logger class to the desired type,
        gets or creates the logger, then restores the original logger class.

        Args:
            logger_name: The name of the logger to get.
            logger_class: The desired logger class type.

        Returns:
            A logger instance of the specified type.
        """
        original_class = logging.getLoggerClass()
        logging.setLoggerClass(logger_class)
        logger = logging.getLogger(logger_name)
        logging.setLoggerClass(original_class)
        typed_logger = cast(
            "ApatheticLogging_Internal_LoggingUtils._LoggerType", logger
        )
        return typed_logger

    @staticmethod
    def _extract_top_level_package(package: str | None) -> str | None:
        """Extract top-level package name from package string.

        Args:
            package: Package string (e.g., "myapp.submodule") or None.

        Returns:
            Top-level package name (e.g., "myapp") or None if package is None.
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
            skip_frames: Number of frames to skip to get to actual caller.
            frame: Frame to start from, or None.

        Returns:
            Inferred logger name or None if cannot be inferred.
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
    def resolve_logger_name(
        logger_name: str | None,
        *,
        check_registry: bool = True,
        skip_frames: int = 1,
    ) -> str:
        """Resolve logger name with optional inference from caller's frame.

        This is a unified helper that handles the common pattern of:
        1. Using explicit name if provided
        2. Checking registry if requested
        3. Inferring from caller's frame if needed
        4. Storing inferred name in registry
        5. Raising error if still unresolved

        Args:
            logger_name: Explicit logger name, or None to infer.
            check_registry: If True, check registry before inferring. Use False
                when the caller should actively determine the name from current
                context (e.g., register_logger() which should re-infer even
                if a name is already registered). Use True when the caller should
                use a previously registered name if available (e.g., get_logger()
                which should use the registered name).
            skip_frames: Number of frames to skip from this function to get to
                the actual caller. Default is 1 (skips this function's frame).

        Returns:
            Resolved logger name (never None).

        Raises:
            RuntimeError: If logger name cannot be resolved.
        """
        # Import locally to avoid circular import
        from .registry_data import (  # noqa: PLC0415
            ApatheticLogging_Internal_RegistryData,
        )

        _registry_data = ApatheticLogging_Internal_RegistryData

        # If explicit name provided, return it (never store explicit names)
        if logger_name is not None:
            return logger_name

        # Check registry if requested
        if check_registry:
            registered_name = _registry_data.registered_internal_logger_name
            if registered_name is not None:
                return registered_name

        # Try to infer from caller's frame
        # Get current frame (this function's frame) and skip to caller
        frame = inspect.currentframe()
        inferred_name = ApatheticLogging_Internal_LoggingUtils._infer_from_frame(
            skip_frames, frame
        )

        # Store inferred name in registry
        if inferred_name is not None:
            _registry_data.registered_internal_logger_name = inferred_name

        # Return inferred name or raise error
        if inferred_name is not None:
            return inferred_name

        # Raise error with clear message
        error_msg = (
            "Cannot auto-infer logger name: __package__ is not set in the "
            "calling module. Please call register_logger() with an "
            "explicit logger name."
        )
        raise RuntimeError(error_msg)
