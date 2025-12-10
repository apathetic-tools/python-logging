<!-- Roadmap.md -->
# 🧭 Roadmap

Some of these we just want to consider, and may not want to implement.

## 🎯 Core Features
- None currently

## 🧪 Tests
- Tests are slow, when to run what?
- **Update tests for root logger architecture changes:**
  - Tests expecting loggers to have explicit levels: Loggers now default to `NOTSET` (inherit from root) unless `level=None` is passed
  - Tests checking handler attachment: Child loggers with `propagate=True` no longer have handlers (they propagate to root)
  - Tests that manually set `propagate=False`: May need to verify handlers are attached correctly
  - Tests using `module_logger` fixture: Sets `propagate=False` explicitly (line 68), which is fine, but verify behavior
  - Tests that expect auto-level resolution: Only happens when `level=None` is passed, not by default


## 🧑‍💻 Development
- Beta phase, we need to use the library more to identify further improvements or problems
- should we also release to anaconda? others?


## 🔌 API
- Evaluate `_applyPropagateSetting()` and its relationship with `__init__`: Currently, `Logger.__init__()` sets `_propagate_set = False` when `propagate=None`, indicating that `_applyPropagateSetting()` will set it later. This creates a two-phase initialization where propagate can be set either in `__init__` or later via `_applyPropagateSetting()`. Evaluate whether this split responsibility is clear and maintainable, or if propagate should always be set in `__init__` with the registry/default value passed directly. Consider the complexity of tracking `_propagate_set` flag and whether there are edge cases where the propagate value might be inconsistent or set at unexpected times.
- **Root logger replacement: edge cases with custom logger classes:** Review and test situations where we replace the root logger, especially when the default logger class (set via `logging.setLoggerClass()`) is:
  - Not a stdlib `logging.Logger` (e.g., a completely different class)
  - A different subclass of `logging.Logger` (e.g., a third-party logger class)
  - A subclass of our apathetic logger (e.g., `class MyLogger(apathetic_logging.Logger): pass`)
  - Verify that our `isinstance(root_logger, cls)` check in `extendLoggingModule()` correctly identifies when replacement is needed
  - Ensure state porting works correctly when replacing loggers of different types
  - Test behavior when `replace_root=False` is set but the root logger is a different type
  - Consider whether we should warn or error when replacing a logger that's a subclass of our apathetic logger (might indicate user wants to use their subclass)


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
