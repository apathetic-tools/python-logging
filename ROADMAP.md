<!-- Roadmap.md -->
# 🧭 Roadmap

Some of these we just want to consider, and may not want to implement.

## 🎯 Core Features


## 🧩 Joiner Scripts (Build System)
Exploring bundling options for generating the single-file release:

- zip file: zipapp / shiv / pyinstaller --onefile


## 🧪 Tests
- should we make lint tests that check for new functions we don't cover?

## 🧑‍💻 Development


## 🚀 Deployment
- Deploy action when I tag a release should create a release and attach it to the tagged release.

- look into ignores of this one https://docs.astral.sh/ruff/rules/builtin-argument-shadowing/
- look into if we can make ruff enforce camelcase for function names and method names

## 🔌 API
- **Compatibility mode for `getLevelNumber()` unknown level handling** (deferred)
  - it does really mess with our type system since the return type becomes ambiguous, may not be worth it?
  - Add a registration/configuration option for backwards-compatible behavior when `getLevelNumber()` encounters unknown levels
  - Default to off (current behavior: raises `ValueError`)
  - When enabled, could return `None` instead of raising
  - Allows legacy code to opt-in to lenient behavior while maintaining strict defaults
- consider differentiation between "level" and "effectiveLevel" in our functions (which we don't do much of)


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
