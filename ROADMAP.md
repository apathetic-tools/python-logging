<!-- Roadmap.md -->
# 🧭 Roadmap

Some of these we just want to consider, and may not want to implement.

## 🎯 Core Features
- None currently

## 🧪 Tests
- None currently

## 🧑‍💻 Development
- Beta phase, we need to use the library more to identify further improvements or problems
- should we also release to anaconda? others?


## 🔌 API
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
