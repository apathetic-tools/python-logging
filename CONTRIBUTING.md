# 🧩 Contributing Guide

Thanks for your interest in contributing to **Apathetic Python Logger** — a minimal wrapper for the Python standard library logger.

📚 **[Full Contributing Guide →](https://apathetic-tools.github.io/python-logging/contributing)**

For detailed information on setting up your environment, running checks, and contributing code, please visit our documentation website.

This file provides a quick reference for common development tasks.

---

## Quick Reference

### Development Commands

| Command | Description |
|----------|-------------|
| `poetry run poe check:fix` | Auto-fix issues, re-format, type-check, and re-test. |
| `poetry run poe check` | Run linting (`ruff`), type checks (`mypy`), and tests (`pytest`). |
| `poetry run poe fix` | Run all auto-fixers (`ruff`). |
| `poetry run poe build:script` | Bundle the project into a single portable script in `dist/`. |

### Setup

```bash
# Install dependencies
poetry install --with dev

# Run checks before committing
poetry run poe check:fix
```

---

## 📦 Publishing (for maintainers)

**Release Process:**
1. Bump version in `pyproject.toml`
2. Update `RELEASES.md` with new version section
3. Commit: `git commit -m "chore: bump version to X.Y.Z"`
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z - Description"`
5. Push: `git push origin main && git push origin vX.Y.Z`
6. Build: `poetry run poe build:script` (for single-file) or `poetry build` (for PyPI)
7. Publish: `poetry publish` (if needed) and create GitHub release with `dist/apathetic_logging.py`

See [docs/contributing.md](docs/contributing.md) for detailed publishing instructions.

---

## 🪶 Contribution Rules

- Follow [PEP 8](https://peps.python.org/pep-0008/) (enforced via Ruff).  
- Keep the **core library dependency-free** — dev tooling lives only in `pyproject.toml`'s `dev` group.  
- Run `poetry run poe check` before committing.  
- Open PRs against the **`main`** branch.  
- Be kind: small tools should have small egos.

---

**Thank you for helping keep Apathetic Python Logger minimal, dependency-free, and delightful.**
