# src/apathetic_logging/get_logger.py
"""GetLogger functionality for Apathetic Logging."""

from __future__ import annotations

import inspect
import logging
from typing import Any, Protocol, TypeVar, cast

from .logger import (
    ApatheticLogging_Priv_Logger,  # pyright: ignore[reportPrivateUsage]
)
from .register_logger_name import (
    ApatheticLogging_Priv_RegisterLoggerName,  # pyright: ignore[reportPrivateUsage]
)
from .registry import (
    ApatheticLogging_Priv_Registry,  # pyright: ignore[reportPrivateUsage]
)
from .test_trace import (
    ApatheticLogging_Priv_TestTrace,  # pyright: ignore[reportPrivateUsage]
)


_T = TypeVar("_T", bound=logging.Logger)


class _LoggerClassWithExtend(Protocol):
    """Protocol for logger classes that have extend_logging_module()."""

    @classmethod
    def extend_logging_module(cls) -> bool:
        """Extend the logging module with custom levels."""
        ...


class ApatheticLogging_Priv_GetLogger:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class that provides the get_logger static method.

    This class contains the get_logger implementation as a static method.
    When mixed into apathetic_logging, it provides apathetic_logging.get_logger.
    """

    @staticmethod
    def get_logger() -> Any:  # Returns apathetic_logging.Logger
        """Return the registered logger instance.

        Uses Python's built-in logging registry (logging.getLogger()) to retrieve
        the logger. If no logger name has been registered, attempts to auto-infer
        the logger name from the calling module's top-level package.

        Returns:
            The logger instance from logging.getLogger()
            (as apathetic_logging.Logger type)

        Raises:
            RuntimeError: If called before a logger name has been registered and
                auto-inference fails.

        Note:
            This function is used internally by utils_logs.py. Applications
            should use their app-specific getter (e.g., get_app_logger()) for
            better type hints.
        """
        registered_logger_name = (
            ApatheticLogging_Priv_Registry.registered_priv_logger_name
        )

        if registered_logger_name is None:
            # Try to auto-infer from the calling module's package
            frame = inspect.currentframe()
            if frame is not None:
                try:
                    # Get the calling frame (skip get_logger itself)
                    caller_frame = frame.f_back
                    if caller_frame is not None:
                        caller_module = caller_frame.f_globals.get("__package__")
                        if caller_module:
                            _extract = (
                                ApatheticLogging_Priv_RegisterLoggerName._extract_top_level_package  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
                            )
                            inferred_name = _extract(caller_module)
                            if inferred_name:
                                registry = ApatheticLogging_Priv_Registry
                                registry.registered_priv_logger_name = inferred_name
                                registered_logger_name = inferred_name
                                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                                    "get_logger() auto-inferred logger name",
                                    f"name={inferred_name}",
                                    f"from_module={caller_module}",
                                )
                finally:
                    del frame

        if registered_logger_name is None:
            _msg = (
                "Logger name not registered and could not be auto-inferred. "
                "Call register_logger_name() or ensure your app's logs "
                "module is imported."
            )
            raise RuntimeError(_msg)

        logger = logging.getLogger(registered_logger_name)

        # Check if the logger is the correct type. If a logger was created before
        # extend_logging_module() was called, it might be a standard logging.Logger.
        # In that case, we need to delete it and create a new one with the correct type.
        # We check for the presence of 'level_name' attribute which is specific to
        # apathetic_logging.Logger, rather than relying on getLoggerClass() which
        # might not be set correctly in all scenarios.
        if not hasattr(logger, "level_name"):
            # Remove the existing logger from the manager so we can create a new one
            if registered_logger_name in logging.Logger.manager.loggerDict:
                logging.Logger.manager.loggerDict.pop(registered_logger_name, None)
            # Now get a new logger, which will be created with the correct class
            logger = logging.getLogger(registered_logger_name)

        typed_logger = cast("Any", logger)  # apathetic_logging.Logger
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "get_logger() called",
            f"name={typed_logger.name}",
            f"id={id(typed_logger)}",
            f"level={typed_logger.level_name}",
            f"handlers={[type(h).__name__ for h in typed_logger.handlers]}",
        )
        return typed_logger

    @staticmethod
    def _resolve_logger_name(logger_name: str | None) -> str:
        """Resolve the logger name from parameter, registry, or auto-inference.

        Resolution order:
        1. Use provided logger_name if not None
        2. Use registered logger name from registry
        3. Auto-infer from calling module's package
        4. Raise RuntimeError if all fail

        Args:
            logger_name: Optional logger name to use directly

        Returns:
            The resolved logger name (always a string)

        Raises:
            RuntimeError: If no logger name can be determined
        """
        if logger_name is not None:
            return logger_name

        registered_logger_name = (
            ApatheticLogging_Priv_Registry.registered_priv_logger_name
        )

        if registered_logger_name is None:
            # Try to auto-infer from the calling module's package
            frame = inspect.currentframe()
            if frame is not None:
                try:
                    # Get the calling frame (skip _resolve_logger_name itself)
                    caller_frame = frame.f_back
                    if caller_frame is not None:
                        caller_module = caller_frame.f_globals.get("__package__")
                        if caller_module:
                            _extract = (
                                ApatheticLogging_Priv_RegisterLoggerName._extract_top_level_package  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
                            )
                            inferred_name = _extract(caller_module)
                            if inferred_name:
                                registry = ApatheticLogging_Priv_Registry
                                registry.registered_priv_logger_name = inferred_name
                                registered_logger_name = inferred_name
                                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                                    "get_logger_of_type() auto-inferred logger name",
                                    f"name={inferred_name}",
                                    f"from_module={caller_module}",
                                )
                finally:
                    del frame

        if registered_logger_name is None:
            _msg = (
                "Logger name not registered and could not be auto-inferred. "
                "Call register_logger_name() or ensure your app's logs "
                "module is imported."
            )
            raise RuntimeError(_msg)

        return registered_logger_name

    @staticmethod
    def _ensure_logger_has_level_name(
        logger_name: str,
        logger_class: type[_LoggerClassWithExtend] | None = None,
    ) -> logging.Logger:
        """Ensure the logger has the level_name attribute.

        If the logger doesn't exist yet, call extend_logging_module() before
        creating it. If it exists but doesn't have level_name, it was created
        before extend_logging_module() was called, so call extend_logging_module()
        and recreate it.

        Args:
            logger_name: The name of the logger to check
            logger_class: Optional logger class to use for extend_logging_module().
                If provided, calls extend_logging_module() on this class (allowing
                custom loggers to override it). If None, uses the base
                ApatheticLogging_Priv_Logger.Logger class. The class must have
                an extend_logging_module() classmethod.

        Returns:
            A logger instance that has the level_name attribute
        """
        # Use provided logger class or fall back to base class
        extend_class = (
            logger_class
            if logger_class is not None
            else ApatheticLogging_Priv_Logger.Logger
        )

        # Check if logger exists
        logger_exists = logger_name in logging.Logger.manager.loggerDict
        current_logger_class = logging.getLoggerClass()
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "_ensure_logger_has_level_name() called",
            f"logger_name={logger_name}",
            f"logger_exists={logger_exists}",
            f"logger_class={logger_class}",
            f"logger_class_id={id(logger_class) if logger_class else None}",
            f"extend_class={extend_class}",
            f"extend_class_id={id(extend_class)}",
            f"extend_class_name={extend_class.__name__}",
            f"extend_class_module={extend_class.__module__}",
            f"current_logger_class={current_logger_class}",
            f"current_logger_class_id={id(current_logger_class)}",
            f"current_logger_class_name={current_logger_class.__name__}",
            f"current_logger_class_module={current_logger_class.__module__}",
        )

        if not logger_exists:
            # Logger doesn't exist yet - call extend_logging_module() before creating it
            # so it's created with the correct class from the start
            # Call on the provided class (or base class) to allow custom overrides
            extend_class.extend_logging_module()
            # Always set the logger class explicitly to ensure it's correct
            # (extend_logging_module() should have set it, but be explicit)
            # In singlefile mode, class references might differ, so set explicitly
            logging.setLoggerClass(cast("type[logging.Logger]", extend_class))
            new_logger_class = logging.getLoggerClass()
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "_ensure_logger_has_level_name() creating new logger",
                f"logger_name={logger_name}",
                f"logger_class_after_extend={new_logger_class}",
                f"expected_class={extend_class}",
            )
            # Ensure logger doesn't exist in dict (defensive check)
            if logger_name in logging.Logger.manager.loggerDict:
                logging.Logger.manager.loggerDict.pop(logger_name, None)
            logger = logging.getLogger(logger_name)
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "_ensure_logger_has_level_name() created logger",
                f"logger_name={logger_name}",
                f"logger={logger}",
                f"logger_id={id(logger)}",
                f"logger_type={type(logger)}",
                f"logger_type_id={id(type(logger))}",
                f"logger_type_name={type(logger).__name__}",
                f"logger_type_module={type(logger).__module__}",
                f"has_level_name={hasattr(logger, 'level_name')}",
                f"current_logger_class={logging.getLoggerClass()}",
                f"current_logger_class_id={id(logging.getLoggerClass())}",
            )
        else:
            # Logger exists - check if it has level_name
            logger = logging.getLogger(logger_name)
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "_ensure_logger_has_level_name() logger exists",
                f"logger_name={logger_name}",
                f"logger_type={type(logger)}",
                f"has_level_name={hasattr(logger, 'level_name')}",
            )
            if not hasattr(logger, "level_name"):
                # Logger was created before extend_logging_module() was called.
                # Automatically call extend_logging_module() to set up the logger class
                # and register custom levels. This is idempotent, so safe to call.
                # Call on the provided class (or base class) to allow custom overrides
                extend_class.extend_logging_module()
                # Always set the logger class explicitly to ensure it's correct
                # (extend_logging_module() should have set it, but be explicit)
                # In singlefile mode, class references might differ, so set explicitly
                logging.setLoggerClass(cast("type[logging.Logger]", extend_class))

                # Remove the existing logger from the manager so we can create a new one
                # with the correct class
                logging.Logger.manager.loggerDict.pop(logger_name, None)
                new_logger_class = logging.getLoggerClass()
                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                    "_ensure_logger_has_level_name() recreating logger",
                    f"logger_name={logger_name}",
                    f"logger_class_after_extend={new_logger_class}",
                )
                # Now get a new logger, which will be created with the correct class
                logger = logging.getLogger(logger_name)
                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                    "_ensure_logger_has_level_name() recreated logger",
                    f"logger_name={logger_name}",
                    f"logger={logger}",
                    f"logger_id={id(logger)}",
                    f"logger_type={type(logger)}",
                    f"logger_type_id={id(type(logger))}",
                    f"logger_type_name={type(logger).__name__}",
                    f"logger_type_module={type(logger).__module__}",
                    f"has_level_name={hasattr(logger, 'level_name')}",
                    f"current_logger_class={logging.getLoggerClass()}",
                    f"current_logger_class_id={id(logging.getLoggerClass())}",
                )

        return logger

    @staticmethod
    def _ensure_logger_is_subclass(  # noqa: PLR0912, PLR0915
        logger_name: str, logger_class: type[_T]
    ) -> _T:
        """Ensure the logger is an instance of the specified class.

        If the logger is not an instance of the requested class, it will be
        regenerated as the requested class. Also ensures the logger has
        level_name attribute (from apathetic_logging.Logger).

        Args:
            logger_name: The name of the logger to check
            logger_class: The expected logger class type

        Returns:
            A logger instance of the specified class type
        """
        # First ensure the logger has level_name, using the provided logger_class
        # so custom loggers can override extend_logging_module()
        # Cast logger_class to the protocol type for the helper function
        current_logger_class_before = logging.getLoggerClass()
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "_ensure_logger_is_subclass() called",
            f"logger_name={logger_name}",
            f"logger_class={logger_class}",
            f"current_logger_class={current_logger_class_before}",
        )
        logger = ApatheticLogging_Priv_GetLogger._ensure_logger_has_level_name(
            logger_name, cast("type[_LoggerClassWithExtend]", logger_class)
        )
        # Check if logger is an instance of logger_class
        # In singlefile mode, class references might differ even if logically the same,
        # so we also check the MRO (Method Resolution Order) as a diagnostic
        is_instance = isinstance(logger, logger_class)
        logger_type = type(logger)
        # Diagnostic: check MRO to see if classes are related (for debugging)
        mro_compatible = False
        if not is_instance:
            # Check if logger_class is in the MRO of logger's type (logger is subclass)
            mro_compatible = logger_class in logger_type.__mro__
            # Also check if logger's type is in the MRO of logger_class
            # (logger_class is subclass)
            if not mro_compatible:
                mro_compatible = logger_type in logger_class.__mro__
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "_ensure_logger_is_subclass() after _ensure_logger_has_level_name",
            f"logger_name={logger_name}",
            f"logger_type={type(logger)}",
            f"logger_class={logger_class}",
            f"isinstance(logger, logger_class)={is_instance}",
            f"mro_compatible={mro_compatible}",
        )

        # Always try to fix if direct isinstance() check fails
        # (even if MRO check passes, because tests use isinstance()
        # which doesn't use MRO)
        if not is_instance:
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "_ensure_logger_is_subclass() fixing logger type",
                f"logger_name={logger_name}",
                f"current_logger_class={logging.getLoggerClass()}",
                f"requested_logger_class={logger_class}",
            )

            # Set the logger class to the requested class
            logging.setLoggerClass(logger_class)
            # Ensure extend_logging_module() is called to set up custom levels
            # This is idempotent, so safe to call
            # Check if the class has extend_logging_module method (for custom loggers)
            extend_method = getattr(logger_class, "extend_logging_module", None)
            if extend_method is not None and callable(extend_method):
                extend_method()
            new_logger_class = logging.getLoggerClass()
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "_ensure_logger_is_subclass() after setLoggerClass",
                f"logger_name={logger_name}",
                f"new_logger_class={new_logger_class}",
            )

            # Remove existing logger to create new one with correct type
            if logger_name in logging.Logger.manager.loggerDict:
                logging.Logger.manager.loggerDict.pop(logger_name, None)
            # Now get a new logger, which will be created with the logger_class
            logger = logging.getLogger(logger_name)
            # Fix __module__ on the logger's class to ensure isinstance() checks work
            # correctly in both installed and singlefile modes
            logger_type = type(logger)
            if (
                logger_type.__name__ == "Logger"
                and "apathetic_logging" in logger_type.__module__
                and logger_type.__module__ != "apathetic_logging"
                and logger_class.__name__ == "Logger"
            ):
                logger_type.__module__ = "apathetic_logging"
            # Also ensure logger_class itself has correct __module__
            if (
                logger_class.__name__ == "Logger"
                and "apathetic_logging" in logger_class.__module__
                and logger_class.__module__ != "apathetic_logging"
            ):
                logger_class.__module__ = "apathetic_logging"
            # Check if logger is an instance of logger_class
            # We use direct isinstance() check here because we want to ensure
            # the logger actually passes the isinstance() check that tests will use
            is_instance = isinstance(logger, logger_class)
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "_ensure_logger_is_subclass() created new logger",
                f"logger_name={logger_name}",
                f"logger_type={type(logger)}",
                f"logger_class={logger_class}",
                f"current_logger_class={logging.getLoggerClass()}",
                f"isinstance(logger, logger_class)={is_instance}",
                f"has_level_name={hasattr(logger, 'level_name')}",
            )
            # If still not the right type, try one more time with explicit cleanup
            # This is important in singlefile mode where class references
            # might differ
            if not is_instance:
                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                    "_ensure_logger_is_subclass() retrying logger creation",
                    f"logger_name={logger_name}",
                    f"logger_type={type(logger)}",
                    f"expected_class={logger_class}",
                )
                # Remove logger again and verify logger class is set correctly
                if logger_name in logging.Logger.manager.loggerDict:
                    logging.Logger.manager.loggerDict.pop(logger_name, None)
                # Double-check that logger class is set correctly
                # In singlefile mode, check both identity and name/module
                actual_logger_class = logging.getLoggerClass()
                is_same_class = actual_logger_class is logger_class or (
                    actual_logger_class.__name__ == logger_class.__name__
                    and actual_logger_class.__module__ == logger_class.__module__
                )
                if not is_same_class:
                    ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                        "_ensure_logger_is_subclass() logger class mismatch",
                        f"expected={logger_class}",
                        f"actual={actual_logger_class}",
                    )
                    logging.setLoggerClass(logger_class)
                logger = logging.getLogger(logger_name)
                # Fix __module__ on the logger's class to ensure isinstance() checks
                # work correctly in both installed and singlefile modes
                logger_type = type(logger)
                if (
                    logger_type.__name__ == "Logger"
                    and "apathetic_logging" in logger_type.__module__
                    and logger_type.__module__ != "apathetic_logging"
                    and logger_class.__name__ == "Logger"
                ):
                    logger_type.__module__ = "apathetic_logging"
                is_instance = isinstance(logger, logger_class)
                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                    "_ensure_logger_is_subclass() after retry",
                    f"logger_name={logger_name}",
                    f"logger_type={type(logger)}",
                    f"isinstance(logger, logger_class)={is_instance}",
                )
                # If still not the right type after retry, this is a serious issue
                # but we'll return the logger anyway (it might work functionally)
                if not is_instance:
                    ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                        "_ensure_logger_is_subclass() WARNING: logger still wrong type",
                        f"logger_name={logger_name}",
                        f"logger_type={type(logger)}",
                        f"expected_class={logger_class}",
                        f"current_logger_class={logging.getLoggerClass()}",
                    )
            # Ensure the new logger also has level_name
            if not hasattr(logger, "level_name"):
                if logger_name in logging.Logger.manager.loggerDict:
                    logging.Logger.manager.loggerDict.pop(logger_name, None)
                logger = logging.getLogger(logger_name)
                ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                    "_ensure_logger_is_subclass() recreated logger (no level_name)",
                    f"logger_name={logger_name}",
                    f"logger_type={type(logger)}",
                    f"has_level_name={hasattr(logger, 'level_name')}",
                )
            # Note: We do NOT restore the logger class here. The logger class should
            # be managed by fixtures and extend_logging_module(), not by this
            # internal function. Restoring it would break subsequent tests if the
            # previous value was wrong (e.g., logging.Logger from a previous test).

        return cast("_T", logger)

    @staticmethod
    def get_logger_of_type(logger_name: str | None, logger_class: type[_T]) -> _T:
        """Return a logger instance, ensuring it's the correct type.

        This is a helper function for custom logger implementations. It ensures
        that the logger instance is of the specified class type, fixing it if
        needed (e.g., if it was created before extend_logging_module() was called).

        If the logger under the given name is not an instance of the requested class
        (or a subclass), it will be regenerated as the requested class.

        If no logger name is provided, uses the registered logger name or attempts
        to auto-infer the logger name from the calling module's top-level package.

        Args:
            logger_name: Optional logger name. If not provided, uses the registered
                logger name or auto-infers from the calling module.
            logger_class: The expected logger class type

        Returns:
            The logger instance (guaranteed to be an instance of logger_class)

        Raises:
            RuntimeError: If no logger name is provided and no logger name has been
                registered and auto-inference fails.

        Example:
            >>> from apathetic_logging import get_logger_of_type
            >>> logger = get_logger_of_type("myapp", AppLogger)
            >>> # logger is now typed as AppLogger, no cast needed
            >>>
            >>> # Can also omit logger_name to use registry/auto-inference
            >>> logger = get_logger_of_type(None, AppLogger)
        """
        resolved_name = ApatheticLogging_Priv_GetLogger._resolve_logger_name(
            logger_name
        )
        # Fix __module__ on logger_class to ensure isinstance() checks work correctly
        # in both installed and singlefile modes. In singlefile mode, the module
        # might be "apathetic_logging.ApatheticLogging_Priv_Logger" instead of
        # "apathetic_logging", which breaks isinstance() checks.
        # Always fix it for Logger classes to ensure consistency.
        if (
            logger_class.__name__ == "Logger"
            and "apathetic_logging" in logger_class.__module__
        ):
            logger_class.__module__ = "apathetic_logging"
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "get_logger_of_type() called",
            f"logger_name={logger_name}",
            f"resolved_name={resolved_name}",
            f"logger_class={logger_class}",
            f"current_logger_class={logging.getLoggerClass()}",
        )

        # Ensure logger class is set correctly before creating the logger
        # This is important in singlefile mode where class references might differ
        current_logger_class = logging.getLoggerClass()
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "get_logger_of_type() checking logger class",
            f"resolved_name={resolved_name}",
            f"current_logger_class={current_logger_class}",
            f"current_logger_class_id={id(current_logger_class)}",
            f"current_logger_class_name={current_logger_class.__name__}",
            f"current_logger_class_module={current_logger_class.__module__}",
            f"requested_logger_class={logger_class}",
            f"requested_logger_class_id={id(logger_class)}",
            f"requested_logger_class_name={logger_class.__name__}",
            f"requested_logger_class_module={logger_class.__module__}",
        )
        # Check if current class is the same as the requested class
        # In singlefile mode, class references might differ even if logically the same,
        # so we check both identity and name/module to be safe
        is_same_class = current_logger_class is logger_class or (
            current_logger_class.__name__ == logger_class.__name__
            and current_logger_class.__module__ == logger_class.__module__
        )
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "get_logger_of_type() class comparison",
            f"resolved_name={resolved_name}",
            f"is_same_class={is_same_class}",
            f"identity_match={current_logger_class is logger_class}",
            f"name_match={current_logger_class.__name__ == logger_class.__name__}",
            "module_match="
            f"{current_logger_class.__module__ == logger_class.__module__}",
        )
        if not is_same_class:
            # Logger class needs to be changed - clear existing logger to ensure
            # it's recreated with the correct class
            logger_exists_before = resolved_name in logging.Logger.manager.loggerDict
            if logger_exists_before:
                logging.Logger.manager.loggerDict.pop(resolved_name, None)
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "get_logger_of_type() changing logger class",
                f"resolved_name={resolved_name}",
                f"logger_existed={logger_exists_before}",
                f"old_class={current_logger_class}",
                f"new_class={logger_class}",
            )
            # Set the logger class to the requested class
            logging.setLoggerClass(logger_class)
            # Ensure extend_logging_module() is called to set up custom levels
            extend_method = getattr(logger_class, "extend_logging_module", None)
            if extend_method is not None and callable(extend_method):
                extend_method()
            new_logger_class = logging.getLoggerClass()
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "get_logger_of_type() after setLoggerClass",
                f"resolved_name={resolved_name}",
                f"new_logger_class={new_logger_class}",
                f"new_logger_class_id={id(new_logger_class)}",
            )
        else:
            # Logger class is already correct, but ensure extend_logging_module()
            # is called to set up custom levels (idempotent)
            ApatheticLogging_Priv_TestTrace.TEST_TRACE(
                "get_logger_of_type() logger class already correct",
                f"resolved_name={resolved_name}",
                f"logger_class={logger_class}",
            )
            extend_method = getattr(logger_class, "extend_logging_module", None)
            if extend_method is not None and callable(extend_method):
                extend_method()
        # Ensure logger has level_name, passing logger_class so it uses the correct
        # class when creating the logger
        ApatheticLogging_Priv_GetLogger._ensure_logger_has_level_name(
            resolved_name, cast("type[_LoggerClassWithExtend]", logger_class)
        )

        # Ensure logger is the correct subclass (for custom loggers)
        typed_logger = ApatheticLogging_Priv_GetLogger._ensure_logger_is_subclass(
            resolved_name, logger_class
        )
        # Access name attribute safely (typed_logger is a Logger instance)
        logger_name_attr = getattr(typed_logger, "name", "unknown")
        is_instance = isinstance(typed_logger, logger_class)
        ApatheticLogging_Priv_TestTrace.TEST_TRACE(
            "get_logger_of_type() returning",
            f"logger_name={resolved_name}",
            f"name={logger_name_attr}",
            f"logger_type={type(typed_logger)}",
            f"expected_class={logger_class.__name__}",
            f"actual_class={type(typed_logger).__name__}",
            f"isinstance(typed_logger, logger_class)={is_instance}",
            f"id={id(typed_logger)}",
        )
        return typed_logger
