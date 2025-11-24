---
layout: base
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

### Testing on Python 3.10

The project supports Python 3.10+ and CI tests on both Python 3.10 and the latest 3.x.  
To test locally on Python 3.10, you can either use a system-installed Python 3.10 or mise.

> [!NOTE]
> mise setup is optional. You can develop and test on any Python 3.10+ version.  
> The `test:py310` task is only useful if you want to match CI's Python 3.10 environment exactly.

#### Quick Check

First, run the setup check to see if Python 3.10 is available:

```bash
poetry run poe setup:python:check
```

This command will:
- Check for system Python 3.10
- Check for mise-managed Python 3.10
- Provide installation instructions if not found
- Verify everything is working

#### Option 1: System Python 3.10 (Simplest)

If you're on Ubuntu/Debian and Python 3.10 is available in your repositories:

```bash
sudo apt install python3.10 python3.10-venv python3.10-dev
```

Then you can use `poetry run poe env:py310` directly — no mise needed!

#### Option 2: mise (For Multiple Versions or Newer Systems)

If Python 3.10 isn't available via your system package manager (e.g., Ubuntu 24.04), you can use mise:

**1. Install mise** (if not already installed):

```bash
curl https://mise.run | sh
```

**2. Add to your shell configuration** (`~/.bashrc` or `~/.zshrc`):

```bash
eval "$(mise activate bash)"
```

**3. Restart your shell** or run `source ~/.bashrc`

**4. Run the check command** — it will guide you through the rest:

```bash
poetry run poe setup:python:check
```

The check command will:
- Verify mise is set up correctly
- Check if Python 3.10 is installed
- Provide exact commands for installing Python 3.10 via mise
- Verify everything is working

> [!TIP]
> Run `poetry run poe setup:python:check` repeatedly until it shows all checks passing. It provides interactive, step-by-step guidance.

> [!NOTE]
> The `env:py310` task automatically detects system Python 3.10 first, then falls back to mise if needed.

#### Using Python 3.10 for Testing

Once Python 3.10 is available, you can switch between Python versions:

```bash
# Switch to Python 3.10
poetry run poe env:py310

# Run tests on Python 3.10, then switch back
poetry run poe test:py310

# Switch back to latest Python 3.x
poetry run poe env:py3x
```

## Previewing Documentation Locally

The documentation site is built with Jekyll and can be previewed locally before pushing changes.

### Prerequisites

You'll need Ruby 3.3 for Jekyll. The project supports both system Ruby and mise-managed Ruby.

#### Quick Check

First, run the setup check to see if Ruby 3.3 is available:

```bash
poetry run poe setup:ruby:check
```

This command will:
- Check for system Ruby 3.3
- Check for mise-managed Ruby 3.3
- Provide installation instructions if not found
- Verify everything is working

#### Option 1: System Ruby 3.3 (Simplest)

If you're on Ubuntu/Debian and Ruby 3.3 is available in your repositories:

```bash
sudo apt install ruby3.3 ruby3.3-dev
```

#### Option 2: mise (For Multiple Versions or Newer Systems)

If Ruby 3.3 isn't available via your system package manager, you can use mise:

**1. Install mise** (if not already installed):

```bash
curl https://mise.run | sh
```

**2. Add to your shell configuration** (`~/.bashrc` or `~/.zshrc`):

```bash
eval "$(mise activate bash)"
```

**3. Restart your shell** or run `source ~/.bashrc`

**4. Run the check command** — it will guide you through the rest:

```bash
poetry run poe setup:ruby:check
```

The check command will:
- Verify mise is set up correctly
- Check if Ruby 3.3 is installed
- Provide exact commands for installing Ruby 3.3 via mise
- Verify everything is working

> [!NOTE]
> If you're using mise, Ruby 3.3 will be automatically activated when you enter the project directory (via `.tool-versions`).

### Building and Serving the Documentation

Once Ruby 3.3 is available:

**1. Install Jekyll dependencies:**

```bash
cd docs
bundle install
```

**2. Start the Jekyll server:**

```bash
bundle exec jekyll serve
```

**3. Open your browser:**

Navigate to `http://localhost:4000/python-logging/`

> [!NOTE]
> The baseurl is `/python-logging`, so make sure to include it in the local URL.

The server will automatically rebuild when you make changes to the documentation files.

## Building and Publishing (for maintainers)

Apathetic Python Logger ships in two forms:

| Target | Command | Output |
|--------|---------|--------|
| **Single-file script** | `poetry run poe build:script` | Creates `dist/apathetic_logging.py` |
| **PyPI package** | `poetry build && poetry publish` | Builds and uploads wheel & sdist |

### Release Process (CLI)

To create a new release:

1. **Bump version** in `pyproject.toml`:
   ```bash
   # Edit pyproject.toml and update: version = "X.Y.Z"
   ```

2. **Update RELEASES.md** with the new version section:
   ```bash
   # Add a new section at the top with version, date, and changes
   ```

3. **Commit the changes**:
   ```bash
   git add pyproject.toml RELEASES.md
   git commit -m "chore: bump version to X.Y.Z"
   ```

4. **Create and push the git tag**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z - Description"
   git push origin main
   git push origin vX.Y.Z
   ```

5. **Build the single-file script**:
   ```bash
   poetry run poe build:script
   ```
   This creates `dist/apathetic_logging.py` which should be attached to the GitHub release.

6. **Build and publish to PyPI** (if needed):
   ```bash
   poetry build
   poetry publish --username __token__ --password <your-pypi-token>
   ```

7. **Create GitHub release** (if not automated):
   - Go to GitHub Releases page
   - Click "Draft a new release"
   - Select the tag you just pushed
   - Copy the release notes from `RELEASES.md`
   - Attach `dist/apathetic_logging.py` (single-file build)
   - Publish the release

> **Note:** Verify the package on [Test PyPI](https://test.pypi.org/) before publishing live.

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

