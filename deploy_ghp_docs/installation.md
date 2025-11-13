---
layout: default
title: Installation
permalink: /installation/
---

# Installation Guide

Apathetic Python Logger can be installed using several methods. Choose the one that best fits your project's needs.

## Primary Method: PyPI (Recommended)

The recommended way to install Apathetic Python Logger is via PyPI using `poetry` or `pip`.

### Using Poetry

```bash
poetry add apathetic-logger
```

### Using pip

```bash
pip install apathetic-logger
```

This is the recommended installation method for most users as it provides:
- Easy dependency management
- Version pinning
- Integration with your existing Python project structure

## Alternative: Single-File Distribution

For projects that prefer a single-file dependency, we also distribute a standalone `apathetic_logger.py` file that you can download directly from [releases](https://github.com/apathetic-tools/python-logs/releases).

### Download and Use

1. Download `apathetic_logger.py` from the [latest release](https://github.com/apathetic-tools/python-logs/releases)
2. Place it in your project directory
3. Import it directly:

```python
import apathetic_logger
```

This method is useful for:
- Projects that want to minimize external dependencies
- Single-file Python scripts
- Embedded systems or restricted environments
- Integration with tools like [serger](https://github.com/apathetic-tools/serger) that bundle dependencies

## Requirements

- **Python 3.10+**

Apathetic Python Logger has **zero runtime dependencies** — it uses only Python's standard library. This makes it perfect for CLI tools and applications where dependency bloat is a concern.

## Verification

After installation, verify that it works:

```python
from apathetic_logger import get_logger, register_logger_name

register_logger_name("test")
logger = get_logger()
logger.info("Installation successful!")
```

If you see the info message, installation was successful!

## Next Steps

- Read the [Quick Start Guide]({{ '/quickstart' | relative_url }}) to get up and running
- Check out the [API Reference]({{ '/api' | relative_url }}) for detailed documentation
- See [Examples]({{ '/examples' | relative_url }}) for advanced usage patterns

