<!-- Roadmap.md -->
# 🧭 Roadmap

Some of these we just want to consider, and may not want to implement.

## 🎯 Core Features
Major stitching capabilities and enhancements:


## 🧩 Joiner Scripts (Build System)
Exploring bundling options for generating the single-file release:

- zip file: zipapp / shiv / pyinstaller --onefile
- serger for stitched file

## 🧪 Tests
- can we test on py3.10 locally via poetry venv?
- should we make lint tests that check for new functions we don't cover?

## 🧑‍💻 Development

- **Architectural principle: Use our own wrappers instead of `logging.*` directly**
  - Audit all internal code (excluding wrapper classes) for direct `logging.*` calls
  - Replace with our namespace functions or internal class methods
  - Only wrapper/extender functions (`logging_std_snake.py`, `logging_std_camel.py`) should call `logging.*` directly
  - Document as architectural rule and consider linting/static analysis to catch violations
  - Benefits: consistency, future-proofing, automatic custom feature support, easier refactoring


## 🚀 Deployment
- Deploy action when I tag a release should create a release and attach it to the tagged release.

## 🔌 API
- let getLogger/get_logger/getLoggerOfType/get_logger_of_type() provide the log level using keyword arguments, both exact log level (set the log level on the logger to this) and minimum (make the logger have at least this log level if it doesn't already)
- what to do about new methods or new signatures in newer than 3.10 python? does the user provide a init setting/registry for what py version they support so they can bump beyond 3.10, and our 3.11+ functions should raise() if they don't meet it? do we infer from pyproject.toml?
- make sure all our functions are camelCase, and we have wrappers for snake case.
- **Compatibility mode for `getLevelNumber()` unknown level handling**
  - it does really mess with our type system since the return type becomes ambiguous, may not be worth it?
  - Add a registration/configuration option for backwards-compatible behavior when `getLevelNumber()` encounters unknown levels
  - Default to off (current behavior: raises `ValueError`)
  - When enabled, could return a constant (e.g., `UNKNOWN_LEVEL = 999`) or `None` instead of raising
  - Allows legacy code to opt-in to lenient behavior while maintaining strict defaults
- consider differentiation between "level" and "effectiveLevel" in our functions (which we don't do much of)
- consider making the .level and .levelName the effective properties instead of the explicit ones when not backwards compatible.

## 📚 Documentation
- header is not stickied
- the navbar styling was lost when we customized it for the current page
- home is not bolded when on it
- Where do we document the structure of the project? What do we document inside it vs here?
- Logo? Images? Icon? README banner?
- should we generate API docs? replace the ones in our docs?

## 💡 Ideas & Experiments
Potential quality-of-life features:

- publish to PyPI

> See [REJECTED.md](REJECTED.md) for experiments and ideas that were explored but intentionally not pursued.

---

> ✨ *AI was used to help draft language, formatting, and code — plus we just love em dashes.*

<p align="center">
  <sub>😐 <a href="https://apathetic-tools.github.io/">Apathetic Tools</a> © <a href="./LICENSE">MIT-a-NOAI</a></sub>
</p>
