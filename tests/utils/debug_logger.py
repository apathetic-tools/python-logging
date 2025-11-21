"""Debug utilities for logger inspection."""

import logging

import apathetic_logging as mod_alogs
import apathetic_logging.logger as mod_logger


def debug_logger_summary(logger: logging.Logger) -> None:
    """Print detailed debugging information about a logger instance.

    Shows logger type information, class references, and isinstance checks.
    """
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING: debug_logger()")
    print("=" * 80)

    logger_target_list: list[tuple[str, type[logging.Logger]]] = [
        ("logging_getLoggerClass", logging.getLoggerClass()),
        ("mod_alogs_getLoggerClass", mod_alogs.getLoggerClass()),
        ("mod_alogs_Logger", mod_alogs.Logger),
        (
            "mod_logger.ApatheticLogging_Internal_LoggerCore",
            mod_logger.ApatheticLogging_Internal_LoggerCore,
        ),
        ("mod_alogs.apathetic_logging.Logger", mod_alogs.apathetic_logging.Logger),
        # (
        #     "mod_alogs.apathetic_logging.ApatheticLogging_Internal_LoggerCore",
        #     mod_alogs.apathetic_logging.ApatheticLogging_Internal_LoggerCore,
        # ),
    ]

    # print all our loggers
    for logger_ptarget in [{"logger", logger}, *logger_target_list]:
        logger_plabel, logger_pclass = logger_ptarget
        print(f"\n{logger_plabel} = {logger_pclass}")
        print(f"logger type = {type(logger_pclass)}")
        print(f"logger type name = {type(logger_pclass).__name__}")
        logger_pqualname = getattr(type(logger_pclass), "__qualname__", "N/A")
        print(f"logger type qualname = {logger_pqualname}")
        print(f"logger type module = {type(logger_pclass).__module__}")

    # isinstance them
    print("\n")
    for logger_itarget in logger_target_list:
        logger_ilabel, logger_iclass = logger_itarget
        isinstance_logger = isinstance(logger, logger_iclass)  # pyright: ignore[reportUnnecessaryIsInstance]
        print(f"isinstance(logger, {logger_ilabel}) = {isinstance_logger}")

    # is them
    print("\n")
    for logger_starget in logger_target_list:
        logger_slabel, logger_sclass = logger_starget
        is_logger = type(logger) is logger_sclass
        print(f"type(logger) is {logger_slabel} = {is_logger}")

    print("=" * 80 + "\n")
