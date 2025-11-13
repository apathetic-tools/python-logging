---
layout: default
title: Contributing
permalink: /contributing/
---

# Contributing Guide

Thanks for your interest in contributing to **Apathetic Python Logger** — a minimal wrapper for the Python standard library logger.  
This guide explains how to set up your environment, run checks, and safely contribute code.

## Supported Python Versions

Apathetic Python Logger targets **Python 3.10+**.  
That keeps compatibility with Ubuntu 22.04 (the baseline CI OS) while staying modern.

> The library itself has **no runtime dependencies** — only dev tools use Poetry.

## Setting Up the Environment

We use **[Poetry](https://python-poetry.org/)** for dependency and task management.

### 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry --version
```

If Poetry isn't on your `PATH`, add it to your shell configuration (usually `~/.bashrc` or `~/.zshrc`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Install Dependencies

```bash
poetry install --with dev
```

This creates an isolated virtual environment with Ruff, Mypy, pytest, and Poe tasks.

## Development Commands

All key workflows are defined in **`[tool.poe.tasks]`** inside `pyproject.toml`.

| Command | Description |
|---------|-------------|
| `poetry run poe check:fix` | Auto-fix issues, re-format, type-check, and re-test. |
| `poetry run poe check` | Run linting (`ruff`), type checks (`mypy`), and tests (`pytest`). |
| `poetry run poe fix` | Run all auto-fixers (`ruff`). |
| `poetry run poe build:script` | Bundle the project into a single portable script in `dist/`. |

Example workflow:

```bash
# Auto-fix & re-check
poetry run poe check:fix
```

## Pre-commit Hook

Pre-commit is configured to run **`poe fix`** on each commit,  
and **`poe check`** before every push.  
This keeps your local commits tidy and ensures CI stays green.

Install the hook once:

```bash
poetry run pre-commit install --install-hooks
poetry run pre-commit install --hook-type pre-push
```

If any linter, type check, or test fails, the commit is blocked. It may have auto-fixed the problem, try committing again before troubleshooting.

## Testing

Run the test suite directly:

```bash
poetry run poe test
```

Pytest will discover all files in `tests/` automatically.

## Building and Publishing (for maintainers)

Apathetic Python Logger ships in two forms:

| Target | Command | Output |
|--------|---------|--------|
| **Single-file script** | `poetry run poe build:script` | Creates `dist/apathetic_logger.py` |
| **PyPI package** | `poetry build && poetry publish` | Builds and uploads wheel & sdist |

To publish to PyPI:

```bash
poetry build
poetry publish --username __token__ --password <your-pypi-token>
```

> Verify the package on [Test PyPI](https://test.pypi.org/) before publishing live.

The single-file version should be attached to GitHub releases for direct download.

## Integration with Apathetic Tools

When contributing, keep in mind that this library is designed to integrate strongly with:

- **[serger](https://github.com/apathetic-tools/serger)** — the module stitching tool
- Other Apathetic Tools projects

Changes should maintain compatibility with the broader Apathetic Tools ecosystem and work seamlessly in both modular and single-file distributions.

## Contribution Rules

- Follow [PEP 8](https://peps.python.org/pep-0008/) (enforced via Ruff).  
- Keep the **core library dependency-free** — dev tooling lives only in `pyproject.toml`'s `dev` group.  
- Run `poetry run poe check` before committing.  
- Open PRs against the **`main`** branch.  
- Be kind: small tools should have small egos.

## Getting Help

- 📘 [Roadmap](https://github.com/apathetic-tools/python-logs/blob/main/ROADMAP.md)
- 🐛 [Issue Tracker](https://github.com/apathetic-tools/python-logs/issues)
- 💬 [Discord](https://discord.gg/PW6GahZ7)

**Thank you for helping keep Apathetic Python Logger minimal, dependency-free, and delightful.**

