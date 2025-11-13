# Apathetic Python Logger 📝 

[![CI](https://github.com/apathetic-tools/python-logs/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/goldilocks/python-logs/actions/workflows/ci.yml)
[![License: MIT-aNOAI](https://img.shields.io/badge/License-MIT--aNOAI-blueviolet.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://discord.gg/PW6GahZ7)

📘 **[Roadmap](./ROADMAP.md)** · 📝 **[Release Notes](https://github.com/apathetic-tools/python-logs/releases)**

**Minimal wrapper for the Python standard library logger.**  
*Because consistent, colorized logging shouldn't require large dependencies.*

Apathetic Python Logger provides a lightweight, dependency-free logging solution designed for CLI tools. It extends Python's standard library `logging` module with colorized output, dual-stream handling (stdout/stderr), and seamless integration with Apathetic Tools projects.



---

## 🚀 Installation

### Primary Method: PyPI (Recommended)

Install via **poetry** or **pip**:

```bash
# Using poetry
poetry add apathetic-logger

# Using pip
pip install apathetic-logger
```

This is the recommended installation method for most users.

### Alternative: Single-File Distribution

For projects that prefer a single-file dependency, we also distribute a standalone `apathetic_logger.py` file that you can download directly from [releases](https://github.com/apathetic-tools/python-logs/releases).

Simply download the file and import it:

```python
# Download apathetic_logger.py from releases, then:
import apathetic_logger
```

---

## 🧩 Integration with Apathetic Tools

This library is designed to work seamlessly with **[serger](https://github.com/apathetic-tools/serger)** and other Apathetic Tools projects. It provides:

- **Consistent logging interface** across all Apathetic Tools
- **Colorized output** that works in both modular and single-file builds
- **Zero runtime dependencies** — uses only Python's standard library
- **CLI-friendly** formatting with tag-based log levels

Everything else in this repo (tests, docs, configs) exists only for developing and maintaining the script itself.

---

## 💻 Quick Start

```python
from apathetic_logger import get_logger, register_logger_name

# Register your logger name
register_logger_name("my_app")

# Get the logger instance
logger = get_logger()

# Use it!
logger.info("Hello, world!")
logger.error("Something went wrong")
logger.debug("Debug information")
```

---

## 🧪 Requirements

- **Python 3.10+**

No other dependencies required — this library uses only Python's standard library.

---

## ⚖️ License

- [MIT-aNOAI License](LICENSE)

You're free to use, copy, and modify the library under the standard MIT terms.  
The additional rider simply requests that this project not be used to train or fine-tune AI/ML systems until the author deems fair compensation frameworks exist.  
Normal use, packaging, and redistribution for human developers are unaffected.

---

## 🔄 Maintenance Commitment

This project will be actively maintained as long as it remains relevant to other Apathetic Tools projects. We prioritize compatibility and integration with the broader Apathetic Tools ecosystem.

---

## 🪶 Summary

**Use it. Hack it. Ship it.**  
It's MIT-licensed, minimal, and meant to stay out of your way — just with one polite request: don't feed it to the AIs (yet).

---

> ✨ *AI was used to help draft language, formatting, and code — plus we just love em dashes.*

<p align="center">
  <sub>😐 <a href="https://apathetic-tools.github.io/">Apathetic Tools</a> © <a href="./LICENSE">MIT-aNOAI</a></sub>
</p>