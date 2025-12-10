# tests/50_core/test_get_logger_porting.py
"""Tests for logger state porting in getLogger/getLoggerOfType."""

import logging

import apathetic_logging as mod_alogs


def test_get_logger_of_type_ports_state_when_replacing() -> None:
    """getLoggerOfType() should port state when replacing a logger."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Create a standard logger
    logging.setLoggerClass(logging.Logger)
    standard_logger = logging.getLogger("test_porting")
    standard_logger.setLevel(logging.WARNING)
    standard_logger.propagate = False
    standard_logger.disabled = True
    test_handler = logging.StreamHandler()
    standard_logger.addHandler(test_handler)

    # Register it
    logging.Logger.manager.loggerDict["test_porting"] = standard_logger

    # --- execute ---
    # Get logger of apathetic type - should replace and port state
    new_logger = mod_alogs.getLoggerOfType("test_porting", mod_alogs.Logger)

    # --- verify ---
    assert isinstance(new_logger, mod_alogs.Logger)
    # State should be ported (default behavior)
    assert new_logger.level == logging.WARNING
    assert new_logger.propagate is False
    assert new_logger.disabled is True
    assert test_handler in new_logger.handlers

    # --- cleanup ---
    _logging_utils.removeLogger("test_porting")


def test_get_logger_of_type_user_level_takes_precedence() -> None:
    """getLoggerOfType() should use user-provided level instead of ported level."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Create a standard logger with WARNING level
    logging.setLoggerClass(logging.Logger)
    standard_logger = logging.getLogger("test_user_level")
    standard_logger.setLevel(logging.WARNING)

    # Register it
    logging.Logger.manager.loggerDict["test_user_level"] = standard_logger

    # --- execute ---
    # Get logger with explicit level=DEBUG - should use DEBUG, not ported WARNING
    new_logger = mod_alogs.getLoggerOfType(
        "test_user_level", mod_alogs.Logger, level="DEBUG"
    )

    # --- verify ---
    assert isinstance(new_logger, mod_alogs.Logger)
    # User-provided level should take precedence
    assert new_logger.level == logging.DEBUG
    assert new_logger.level != logging.WARNING

    # --- cleanup ---
    _logging_utils.removeLogger("test_user_level")


def test_get_logger_of_type_ports_handlers_by_default() -> None:
    """getLoggerOfType() should port handlers by default when replacing."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging

    # Create a standard logger with a handler
    logging.setLoggerClass(logging.Logger)
    standard_logger = logging.getLogger("test_port_handlers")
    test_handler = logging.StreamHandler()
    standard_logger.addHandler(test_handler)

    # Register it
    logging.Logger.manager.loggerDict["test_port_handlers"] = standard_logger

    # --- execute ---
    # Get logger of apathetic type - should port handlers
    new_logger = mod_alogs.getLoggerOfType("test_port_handlers", mod_alogs.Logger)

    # --- verify ---
    assert isinstance(new_logger, mod_alogs.Logger)
    # Handler should be ported (default behavior)
    assert test_handler in new_logger.handlers

    # --- cleanup ---
    _logging_utils.removeLogger("test_port_handlers")


def test_port_handlers_calls_manageHandlers_root_logger() -> None:
    """When porting handlers, manageHandlers() should be called for root logger."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.INFO)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Add a user handler to the standard root logger
    user_handler = logging.StreamHandler()
    standard_root.addHandler(user_handler)

    # --- execute ---
    # Replace root logger - should port handlers and call manageHandlers()
    mod_alogs.Logger.extendLoggingModule(port_handlers=True)

    # --- verify ---
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    assert isinstance(new_root, mod_alogs.Logger)
    # User handler should be ported
    assert user_handler in new_root.handlers
    # Root logger should also have apathetic handler (always gets one)
    apathetic_handlers = [
        h for h in new_root.handlers if isinstance(h, mod_alogs.DualStreamHandler)
    ]
    assert len(apathetic_handlers) > 0, "Root logger should have apathetic handler"

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)


def test_port_handlers_calls_manageHandlers_child_propagate_false() -> None:
    """When porting handlers, manageHandlers() adds handler for propagate=False."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging

    # Create a standard logger with propagate=False
    logging.setLoggerClass(logging.Logger)
    standard_logger = logging.getLogger("test_port_manage_propagate_false")
    standard_logger.propagate = False
    user_handler = logging.StreamHandler()
    standard_logger.addHandler(user_handler)

    # Register it
    logger_name = "test_port_manage_propagate_false"
    logging.Logger.manager.loggerDict[logger_name] = standard_logger

    # --- execute ---
    # Get logger of apathetic type - should port handlers and call manageHandlers()
    new_logger = mod_alogs.getLoggerOfType(
        "test_port_manage_propagate_false", mod_alogs.Logger
    )

    # --- verify ---
    assert isinstance(new_logger, mod_alogs.Logger)
    assert new_logger.propagate is False
    # User handler should be ported
    assert user_handler in new_logger.handlers
    # Child logger with propagate=False should also have apathetic handler
    apathetic_handlers = [
        h for h in new_logger.handlers if isinstance(h, mod_alogs.DualStreamHandler)
    ]
    msg = "Child logger with propagate=False should have apathetic handler"
    assert len(apathetic_handlers) > 0, msg

    # --- cleanup ---
    _logging_utils.removeLogger("test_port_manage_propagate_false")


def test_port_handlers_calls_manageHandlers_child_propagate_true() -> None:
    """manageHandlers() does NOT add handler for propagate=True when porting."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging

    # Create a standard logger with propagate=True
    logging.setLoggerClass(logging.Logger)
    standard_logger = logging.getLogger("test_port_manage_propagate_true")
    standard_logger.propagate = True
    user_handler = logging.StreamHandler()
    standard_logger.addHandler(user_handler)

    # Register it
    logger_name = "test_port_manage_propagate_true"
    logging.Logger.manager.loggerDict[logger_name] = standard_logger

    # --- execute ---
    # Get logger of apathetic type - should port handlers and call manageHandlers()
    new_logger = mod_alogs.getLoggerOfType(
        "test_port_manage_propagate_true", mod_alogs.Logger
    )

    # --- verify ---
    assert isinstance(new_logger, mod_alogs.Logger)
    assert new_logger.propagate is True
    # User handler should be ported
    assert user_handler in new_logger.handlers
    # Child logger with propagate=True should NOT have apathetic handler
    # (it relies on propagation to root logger)
    apathetic_handlers = [
        h for h in new_logger.handlers if isinstance(h, mod_alogs.DualStreamHandler)
    ]
    msg = "Child logger with propagate=True should NOT have apathetic handler"
    assert len(apathetic_handlers) == 0, msg

    # --- cleanup ---
    _logging_utils.removeLogger("test_port_manage_propagate_true")


def test_port_handlers_preserves_user_handlers_with_apathetic() -> None:
    """Ported user handlers should coexist with apathetic handlers."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging

    # Create a standard logger with propagate=False and multiple user handlers
    logging.setLoggerClass(logging.Logger)
    standard_logger = logging.getLogger("test_port_preserve_handlers")
    standard_logger.propagate = False
    user_handler1 = logging.StreamHandler()
    user_handler2 = logging.StreamHandler()
    standard_logger.addHandler(user_handler1)
    standard_logger.addHandler(user_handler2)

    # Register it
    logging.Logger.manager.loggerDict["test_port_preserve_handlers"] = standard_logger

    # --- execute ---
    # Get logger of apathetic type - should port handlers and call manageHandlers()
    logger_name = "test_port_preserve_handlers"
    new_logger = mod_alogs.getLoggerOfType(logger_name, mod_alogs.Logger)

    # --- verify ---
    assert isinstance(new_logger, mod_alogs.Logger)
    # Both user handlers should be ported
    assert user_handler1 in new_logger.handlers
    assert user_handler2 in new_logger.handlers
    # Should also have apathetic handler (propagate=False)
    apathetic_handlers = [
        h for h in new_logger.handlers if isinstance(h, mod_alogs.DualStreamHandler)
    ]
    assert len(apathetic_handlers) > 0, "Should have apathetic handler"
    # Total handlers should be user handlers + apathetic handler
    # 2 user handlers + at least 1 apathetic handler = at least 3 total
    min_expected_handlers = 3
    msg = "Should have user handlers plus apathetic handler"
    assert len(new_logger.handlers) >= min_expected_handlers, msg

    # --- cleanup ---
    _logging_utils.removeLogger("test_port_preserve_handlers")
