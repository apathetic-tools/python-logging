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


## 🧑‍💻 Development


## 🚀 Deployment
- Deploy action when I tag a release should create a release and attach it to the tagged release.

## 🔌 API
- ✅ **RESOLVED**: `get_logger()` is safe - `extend_logging_module()` is called automatically at import time, and `get_logger()` has defensive code to fix logger instances created before extend was called. `get_app_logger()` can also be made safe by adding defensive checks (see `dev/serger.py` for implementation pattern).
- if we call extend, does that mess up the app class?


## 📚 Documentation
- Where do we document the structure of the project? What do we document inside it vs here?
- Where do we do longer usage documentation? README can get a bit big
- Logo? Images? Icon? README banner?
- API docs

## 💡 Ideas & Experiments
Potential quality-of-life features:

- publish to PyPI

> See [REJECTED.md](REJECTED.md) for experiments and ideas that were explored but intentionally not pursued.

---

> ✨ *AI was used to help draft language, formatting, and code — plus we just love em dashes.*

<p align="center">
  <sub>😐 <a href="https://apathetic-tools.github.io/">Apathetic Tools</a> © <a href="./LICENSE">MIT-aNOAI</a></sub>
</p>
