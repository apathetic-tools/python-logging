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
- **Root logger replacement: porting handlers and level:** When `extendLoggingModule()` replaces the root logger with an apathetic logger, we currently preserve the old root logger's level, handlers, propagate, and disabled state. Evaluate whether this behavior should be configurable:
  - Should we port handlers by default, or should the new apathetic root logger start fresh with its own handlers (via `manageHandlers()`)?
  - Should we port the level by default, or should the new root logger use a default level (NOTSET/INHERIT)?
  - If we make this configurable, do we need keyword arguments to `extendLoggingModule()`, registry settings, or constants for these scenarios?
  - Should users be able to specify they want handlers/level ported, or does porting them not make good sense at all (e.g., because apathetic loggers should manage their own handlers)?
  - Consider edge cases: What if the old root logger has incompatible handlers? What if the level was set to a custom value that doesn't exist in apathetic logging?


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
