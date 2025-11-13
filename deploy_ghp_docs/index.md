---
layout: default
title: Home
permalink: /
---

# Apathetic Python Logger 📝

**Minimal wrapper for the Python standard library logger.**  
*Because consistent, colorized logging shouldn't require large dependencies.*

Apathetic Python Logger provides a lightweight, dependency-free logging solution designed for CLI tools. It extends Python's standard library `logging` module with colorized output, dual-stream handling (stdout/stderr), and seamless integration with Apathetic Tools projects.

## Features

- 🎨 **Colorized output** — Automatic color detection with TTY support
- 🔄 **Dual-stream handling** — Smart routing to stdout/stderr
- 🪶 **Zero dependencies** — Uses only Python's standard library
- 🏷️ **Tag-based formatting** — Clean, readable log tags with emoji support
- 🔧 **CLI-friendly** — Designed for command-line applications
- 🧩 **Apathetic Tools integration** — Works seamlessly with serger and other Apathetic Tools

## Quick Example

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

## Requirements

- **Python 3.10+**

No other dependencies required — this library uses only Python's standard library.

## Installation

Install via **poetry** or **pip**:

```bash
# Using poetry
poetry add apathetic-logger

# Using pip
pip install apathetic-logger
```

For alternative installation methods, see the [Installation Guide]({{ '/installation' | relative_url }}).

## Documentation

- **[Installation Guide]({{ '/installation' | relative_url }})** — How to install and set up
- **[Quick Start]({{ '/quickstart' | relative_url }})** — Get up and running in minutes
- **[API Reference]({{ '/api' | relative_url }})** — Complete API documentation
- **[Examples]({{ '/examples' | relative_url }})** — Advanced usage examples
- **[Custom Logger Guide]({{ '/custom-logger' | relative_url }})** — Creating application-specific loggers
- **[Contributing]({{ '/contributing' | relative_url }})** — How to contribute

## License

[MIT-aNOAI License](https://github.com/apathetic-tools/python-logs/blob/main/LICENSE)

You're free to use, copy, and modify the library under the standard MIT terms.  
The additional rider simply requests that this project not be used to train or fine-tune AI/ML systems until the author deems fair compensation frameworks exist.  
Normal use, packaging, and redistribution for human developers are unaffected.

## Links

- 📘 [Roadmap](https://github.com/apathetic-tools/python-logs/blob/main/ROADMAP.md)
- 📝 [Release Notes](https://github.com/apathetic-tools/python-logs/releases)
- 🐛 [Issue Tracker](https://github.com/apathetic-tools/python-logs/issues)
- 💬 [Discord](https://discord.gg/PW6GahZ7)

---

<p align="center">
  <sub>😐 <a href="https://apathetic-tools.github.io/">Apathetic Tools</a> © <a href="https://github.com/apathetic-tools/python-logs/blob/main/LICENSE">MIT-aNOAI</a></sub>
</p>

