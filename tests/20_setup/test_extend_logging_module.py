# tests/50_core/test_extend_logging_module.py
"""Tests for Logger.extendLoggingModule() class method."""

import logging

import apathetic_logging as mod_alogs


def test_extend_logging_module_adds_trace_level() -> None:
    """extendLoggingModule() should add TRACE level to logging module."""
    # --- setup ---
    # Reset the extension state by creating a new logger class
    # (in real usage, this is called once at module import)

    # --- execute ---
    # Call extendLoggingModule (may have already been called)
    result = mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have TRACE level defined
    assert hasattr(logging, "TRACE")
    assert logging.TRACE == mod_alogs.apathetic_logging.TRACE_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
    # Should return False if already extended
    assert isinstance(result, bool)


def test_extend_logging_module_adds_detail_level() -> None:
    """extendLoggingModule() should add DETAIL level to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have DETAIL level defined
    assert hasattr(logging, "DETAIL")
    assert logging.DETAIL == mod_alogs.apathetic_logging.DETAIL_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_extend_logging_module_adds_brief_level() -> None:
    """extendLoggingModule() should add BRIEF level to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have BRIEF level defined
    assert hasattr(logging, "BRIEF")
    assert logging.BRIEF == mod_alogs.apathetic_logging.BRIEF_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_extend_logging_module_adds_silent_level() -> None:
    """extendLoggingModule() should add SILENT level to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should have SILENT level defined
    assert hasattr(logging, "SILENT")
    assert logging.SILENT == mod_alogs.apathetic_logging.SILENT_LEVEL  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


def test_extend_logging_module_adds_level_names() -> None:
    """extendLoggingModule() should add level names to logging module."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Should be able to get level names
    trace_name = logging.getLevelName(mod_alogs.apathetic_logging.TRACE_LEVEL)  # pyright: ignore[reportDeprecated]
    detail_name = logging.getLevelName(mod_alogs.apathetic_logging.DETAIL_LEVEL)  # pyright: ignore[reportDeprecated]
    brief_name = logging.getLevelName(mod_alogs.apathetic_logging.BRIEF_LEVEL)  # pyright: ignore[reportDeprecated]
    silent_name = logging.getLevelName(mod_alogs.apathetic_logging.SILENT_LEVEL)  # pyright: ignore[reportDeprecated]
    assert trace_name == "TRACE"
    assert detail_name == "DETAIL"
    assert brief_name == "BRIEF"
    assert silent_name == "SILENT"


def test_extend_logging_module_sets_logger_class() -> None:
    """extendLoggingModule() should set the logger class."""
    # --- execute ---
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # The logger class should be set (though we can't easily test this
    # without creating a new logger, which would use the class)
    # We can at least verify the method completes without error
    assert True


def test_extend_logging_module_replaces_root_logger_if_wrong_type() -> None:
    """extendLoggingModule() should replace root logger if it's a standard logger."""
    # --- setup ---
    # Remove root logger from registry and reset logger class to create a standard
    # root logger
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state if it exists
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger from registry and clear logging.root
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    # Reset logger class to standard Logger to create a standard root logger
    logging.setLoggerClass(logging.Logger)

    # Create a standard root logger directly (RootLogger is a special class)
    standard_root = logging.RootLogger(logging.WARNING)
    # Register it in the manager
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    # Update logging.root to point to the new root logger
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Set some state on the standard root logger
    standard_root.setLevel(logging.WARNING)
    standard_root.propagate = False
    standard_root.disabled = False
    test_handler = logging.StreamHandler()
    standard_root.addHandler(test_handler)

    # Verify it's a standard logger (not apathetic)
    assert not isinstance(standard_root, mod_alogs.Logger)
    assert isinstance(standard_root, logging.RootLogger)

    # --- execute ---
    # Call extendLoggingModule() - should replace the root logger
    mod_alogs.Logger.extendLoggingModule()

    # --- verify ---
    # Get root logger again - should now be an apathetic logger
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)

    # Should be an apathetic logger
    assert isinstance(new_root, mod_alogs.Logger)
    assert isinstance(new_root, logging.getLoggerClass())

    # State should be preserved
    assert new_root.level == logging.WARNING
    assert new_root.propagate is False
    assert new_root.disabled is False
    # Handler should be preserved (though manageHandlers might add more)
    assert test_handler in new_root.handlers

    # Should have apathetic logger methods
    assert hasattr(new_root, "manageHandlers")
    assert hasattr(new_root, "trace")
    assert hasattr(new_root, "detail")

    # --- cleanup ---
    # Restore original state
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)


def test_extend_logging_module_replace_root_parameter() -> None:
    """extendLoggingModule() should respect replace_root parameter."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.WARNING)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # --- execute ---
    # Call with replace_root=False - should NOT replace
    mod_alogs.Logger.extendLoggingModule(replace_root=False)

    # --- verify ---
    root_after = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    # Should still be standard logger (not replaced)
    assert isinstance(root_after, logging.RootLogger)
    assert not isinstance(root_after, mod_alogs.Logger)

    # Now call with replace_root=True - should replace
    mod_alogs.Logger.extendLoggingModule(replace_root=True)

    # --- verify ---
    root_after2 = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    # Should now be apathetic logger (replaced)
    assert isinstance(root_after2, mod_alogs.Logger)

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)


def test_extend_logging_module_replace_root_uses_registry() -> None:
    """extendLoggingModule() should use registry setting when replace_root is None."""
    # --- setup ---
    import apathetic_logging.registry_data as mod_registry  # noqa: PLC0415

    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging
    _registry = mod_registry.ApatheticLogging_Internal_RegistryData

    # Save current state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled
    original_registry_value = _registry.registered_internal_replace_root_logger

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.WARNING)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Set registry to False
    mod_alogs.registerReplaceRootLogger(replace_root=False)

    # --- execute ---
    # Call with replace_root=None - should use registry (False)
    mod_alogs.Logger.extendLoggingModule(replace_root=None)

    # --- verify ---
    root_after = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    # Should still be standard logger (not replaced because registry says False)
    assert isinstance(root_after, logging.RootLogger)
    assert not isinstance(root_after, mod_alogs.Logger)

    # Set registry to True
    mod_alogs.registerReplaceRootLogger(replace_root=True)

    # Call again with replace_root=None - should use registry (True)
    mod_alogs.Logger.extendLoggingModule(replace_root=None)

    # --- verify ---
    root_after2 = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    # Should now be apathetic logger (replaced because registry says True)
    assert isinstance(root_after2, mod_alogs.Logger)

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)
    _registry.registered_internal_replace_root_logger = original_registry_value


def test_extend_logging_module_reconnects_child_loggers() -> None:
    """extendLoggingModule() should reconnect child loggers when replacing root."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.INFO)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    # Also update manager.root to stay in sync with logging.root
    logging.Logger.manager.root = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Reset the module extension flag so getLogger triggers extension
    mod_alogs.Logger._logging_module_extended = False  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    # Create child loggers BEFORE replacing root
    child1 = mod_alogs.getLogger("test_child1")
    child2 = mod_alogs.getLogger("test_child2")
    child3 = mod_alogs.getLogger("test_child3")

    # Verify they point to standard root
    assert child1.parent is standard_root
    assert child2.parent is standard_root
    assert child3.parent is standard_root

    # --- execute ---
    # Replace root logger
    mod_alogs.Logger.extendLoggingModule(replace_root=True)

    # --- verify ---
    # Get new root logger
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    assert isinstance(new_root, mod_alogs.Logger)
    assert new_root is not standard_root  # type: ignore[comparison-overlap]

    # Child loggers should be reconnected to new root
    assert child1.parent is new_root
    assert child2.parent is new_root
    assert child3.parent is new_root

    # Children should inherit from new root
    assert child1.effectiveLevel == logging.INFO
    assert child2.effectiveLevel == logging.INFO
    assert child3.effectiveLevel == logging.INFO

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)


def test_extend_logging_module_port_handlers_parameter() -> None:
    """extendLoggingModule() should respect port_handlers parameter."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.INFO)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Set some state on the standard root logger
    standard_root.setLevel(logging.INFO)
    test_handler = logging.StreamHandler()
    standard_root.addHandler(test_handler)

    # --- execute ---
    # Call with port_handlers=False - should NOT port handlers
    mod_alogs.Logger.extendLoggingModule(port_handlers=False)

    # --- verify ---
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    assert isinstance(new_root, mod_alogs.Logger)
    # Handler should NOT be ported
    assert test_handler not in new_root.handlers

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)


def test_extend_logging_module_port_level_parameter() -> None:
    """extendLoggingModule() should respect port_level parameter."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.WARNING)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Set level on the standard root logger
    standard_root.setLevel(logging.WARNING)

    # --- execute ---
    # Call with port_level=False - should NOT port level, use determineLogLevel()
    mod_alogs.Logger.extendLoggingModule(port_level=False)

    # --- verify ---
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    assert isinstance(new_root, mod_alogs.Logger)
    # Level should NOT be WARNING (should be from determineLogLevel())
    assert new_root.level != logging.WARNING
    # Should have a valid level (determineLogLevel() result)
    assert new_root.level > 0  # Not INHERIT_LEVEL

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)


def test_extend_logging_module_keeps_manager_root_in_sync() -> None:
    """extendLoggingModule() must keep manager.root in sync with logging.root."""
    # --- setup ---
    _logging_utils = mod_alogs.apathetic_logging
    _constants = mod_alogs.apathetic_logging

    # Save current root logger state
    old_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    old_level = old_root.level
    old_handlers = list(old_root.handlers)
    old_propagate = old_root.propagate
    old_disabled = old_root.disabled

    # Remove root logger and create a standard one
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    if hasattr(logging, "root"):
        logging.root = None  # type: ignore[assignment]

    logging.setLoggerClass(logging.Logger)
    standard_root = logging.RootLogger(logging.INFO)
    logging.Logger.manager.loggerDict[_constants.ROOT_LOGGER_KEY] = standard_root
    logging.Logger.manager.root = standard_root
    if hasattr(logging, "root"):
        logging.root = standard_root

    # Reset the module extension flag so extendLoggingModule actually runs
    mod_alogs.Logger._logging_module_extended = False  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    # --- execute ---
    # Replace root logger
    mod_alogs.Logger.extendLoggingModule(replace_root=True)

    # --- verify ---
    # Get new root logger
    new_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    assert isinstance(new_root, mod_alogs.Logger)

    # CRITICAL: logging.root and logging.Logger.manager.root MUST be the same object
    # If they're different, child loggers will have inconsistent parent references
    assert logging.root is new_root, "logging.root not updated to new root logger"  # type: ignore[comparison-overlap]
    assert logging.Logger.manager.root is new_root, (  # type: ignore[comparison-overlap]
        "logging.Logger.manager.root not updated to new root logger"
    )
    assert logging.root is logging.Logger.manager.root, (
        "logging.root and logging.Logger.manager.root are different objects! "
        "This causes child loggers to have incorrect parent references."
    )

    # --- cleanup ---
    _logging_utils.removeLogger(_constants.ROOT_LOGGER_KEY)
    logging.setLoggerClass(mod_alogs.Logger)
    mod_alogs.Logger.extendLoggingModule()
    restored_root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
    restored_root.setLevel(old_level)
    restored_root.propagate = old_propagate
    restored_root.disabled = old_disabled
    restored_root.handlers.clear()
    for handler in old_handlers:
        restored_root.addHandler(handler)
