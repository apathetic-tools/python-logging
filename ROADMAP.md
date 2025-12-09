<!-- Roadmap.md -->
# 🧭 Roadmap

Some of these we just want to consider, and may not want to implement.

## 🎯 Core Features
- Ensure root logger is always an apathetic logger: Currently, if the root logger is created before `extendLoggingModule()` is called (e.g., if stdlib `logging` is imported first), the root logger will be a standard `logging.Logger` instead of an `apathetic_logging.Logger`. This means it won't have `ensureHandlers()` to attach the DualStreamHandler, and won't have custom methods like `trace()`, `detail()`, etc. Custom levels still work (they're registered globally), but the handler won't be attached automatically. Need to add logic to detect and upgrade/replace the root logger if it's a standard logger, or ensure `extendLoggingModule()` runs before any logger creation.

## 🧪 Tests
- Tests are slow, when to run what?
- **Update tests for root logger architecture changes:**
  - `test_get_default_propagate.py`: Line 17 expects `False`, but default is now `True`
  - Tests expecting loggers to have explicit levels: Loggers now default to `NOTSET` (inherit from root) unless `level=None` is passed
  - Tests checking handler attachment: Child loggers with `propagate=True` no longer have handlers (they propagate to root)
  - Tests that manually set `propagate=False`: May need to verify handlers are attached correctly
  - Tests using `module_logger` fixture: Sets `propagate=False` explicitly (line 68), which is fine, but verify behavior
  - Tests that expect auto-level resolution: Only happens when `level=None` is passed, not by default
- **New tests needed for root logger architecture:**
  - `test_setRootLevel()`: Test the new `setRootLevel()` convenience function
    - Test setting root level affects all child loggers (with propagate=True)
    - Test `apply_to_children=True` updates non-NOTSET child loggers
    - Test `apply_to_children=False` only sets root level
    - Test `set_children_to_level=True` sets children to same level as root
    - Test `set_children_to_level=False` sets children to NOTSET (inherit)
    - Test `root` parameter works with named loggers (not just actual root)
    - Test custom levels work (TRACE, DETAIL, BRIEF, SILENT)
  - `test_ensureHandlers_propagate_behavior()`: Test handler attachment logic
    - Test root logger always gets handler
    - Test child logger with `propagate=True` does NOT get handler
    - Test child logger with `propagate=False` DOES get handler
    - Test handler is attached when logger first logs (via `_log()`)
  - `test_logger_notset_inheritance()`: Test NOTSET inheritance from root
    - Test logger with `level=NOTSET` inherits from root
    - Test `effectiveLevel` matches root when logger is NOTSET
    - Test changing root level affects child loggers with NOTSET
    - Test child logger with explicit level doesn't inherit
  - `test_logger_level_none_auto_resolution()`: Test `level=None` behavior
    - Test `level=None` auto-resolves via `determineLogLevel()`
    - Test `level=NOTSET` (default) does NOT auto-resolve
    - Test `level=<explicit>` sets explicit level
  - `test_root_logger_architecture_integration()`: End-to-end root logger tests
    - Test CLI app sets root level once, all libraries inherit
    - Test multiple libraries all use same level from root
    - Test messages propagate from child to root correctly
    - Test no duplicate messages when propagate=True
    - Test root logger has handler, children don't (when propagating)


## 🧑‍💻 Development
- Beta phase, we need to use the library more to identify further improvements or problems
- should we also release to anaconda? others?


## 🔌 API
- Evaluate renaming `NOTSET` to `INHERIT`: The standard `logging.NOTSET` level name doesn't clearly convey that it means "inherit level from parent". Consider whether providing an `INHERIT` alias or replacement would improve API clarity, while maintaining compatibility with stdlib `logging.NOTSET`.
- Add `manage_handlers` option to `setLevel()`: When a logger's level is set to `NOTSET` (inheriting from parent), it should propagate and not have its own handler. When set away from `NOTSET` to an explicit level, it may need a handler if `propagate=False`. Add a `manage_handlers` parameter to `setLevel()` that automatically manages handler attachment/removal and propagate settings based on whether the level is `NOTSET` or an explicit value.
- Evaluate allowing root logger management through child loggers: Consider whether child logger instances should provide methods or properties to manage the root logger (e.g., `child_logger.setRootLevel()`, `child_logger.root.level`). This could simplify API usage when working with child loggers, but may introduce confusion about which logger is being modified. Evaluate the trade-offs between convenience and clarity.
- Ensure logging functions mirror logger methods on both sides: Audit and ensure that module-level logging functions (e.g., `debug()`, `info()`, `trace()`, `detail()`) have corresponding logger instance methods, and vice versa. For example, if `logger.test()` exists, there should be a module-level `test()` function. If `logger.errorIfNotDebug()` exists, consider whether there should be a module-level equivalent. Maintain consistency between the two APIs so users can use either pattern interchangeably.
- Add convenience functions for common `setLevel()` parameters: Create wrapper functions for frequently used parameter combinations, such as `setLevelMinimum()` for `setLevel(level, minimum=True)`, or `setLevelInherit()` for `setLevel(NOTSET, allow_notset=True)`. This would make common use cases more discoverable and readable, reducing the need to remember parameter names and boolean flags.
- Ensure `addLevelName()` registers levels in both namespaces: Currently `addLevelName()` registers levels in the stdlib `logging` namespace (via `logging.addLevelName()` and `setattr(logging, level_name, level)`), but not in the `apathetic_logging` namespace class. When a user calls `addLevelName(25, "CUSTOM")`, they should be able to access it as both `logging.CUSTOM` and `apathetic_logging.CUSTOM`. Update `addLevelName()` to also set the attribute on the `apathetic_logging` namespace class for consistency.
- Evaluate if `setPropagate()` should automatically manage handlers: When `setPropagate(True)` is called, the logger will propagate to parent loggers and may not need its own handler. When `setPropagate(False)` is called, the logger needs its own handler since it won't propagate. Consider whether `setPropagate()` should automatically add/remove handlers via `ensureHandlers()` or remove handlers when propagate changes, similar to the proposed `manage_handlers` option for `setLevel()`. Evaluate the trade-offs between automatic management and explicit control.
- Evaluate `_applyPropagateSetting()` and its relationship with `__init__`: Currently, `Logger.__init__()` sets `_propagate_set = False` when `propagate=None`, indicating that `_applyPropagateSetting()` will set it later. This creates a two-phase initialization where propagate can be set either in `__init__` or later via `_applyPropagateSetting()`. Evaluate whether this split responsibility is clear and maintainable, or if propagate should always be set in `__init__` with the registry/default value passed directly. Consider the complexity of tracking `_propagate_set` flag and whether there are edge cases where the propagate value might be inconsistent or set at unexpected times.


## 📚 Documentation
- sticky the header
- bold the navbar link when on current page
- Where do we document the structure of the project? What do we document inside it vs here?
- Logo? Images? Icon? README banner?
- should we generate API docs? replace the ones in our docs?


## 💡 Ideas & Experiments
- None currently


> See [REJECTED.md](REJECTED.md) for experiments and ideas that were explored but intentionally not pursued.

---

> ✨ *AI was used to help draft language, formatting, and code — plus we just love em dashes.*

<p align="center">
  <sub>😐 <a href="https://apathetic-tools.github.io/">Apathetic Tools</a> © <a href="./LICENSE">MIT-a-NOAI</a></sub>
</p>
