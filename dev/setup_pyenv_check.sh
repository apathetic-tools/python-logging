#!/bin/bash
set -euo pipefail
# Check Python 3.10 availability for testing

echo "🔍 Checking Python 3.10 availability for testing..."
echo ""

PYTHON_310_FOUND=false
PYTHON_310_PATH=""

# First, check for system Python 3.10 (apt, etc.) - avoid pyenv shims
# Check common system locations first
for POSSIBLE_PATH in /usr/bin/python3.10 /usr/local/bin/python3.10; do
  if [ -x "$POSSIBLE_PATH" ] && "$POSSIBLE_PATH" --version 2>&1 | grep -q "3.10"; then
    PYTHON_310_PATH="$POSSIBLE_PATH"
    echo "✅ Python 3.10 found via system: $PYTHON_310_PATH"
    PYTHON_310_FOUND=true
    break
  fi
done

# If not found in system locations, check PATH but exclude pyenv shims
if [ "$PYTHON_310_FOUND" = false ]; then
  PYTHON_310_PATH=$(command -v python3.10 2>/dev/null)
  if [ -n "$PYTHON_310_PATH" ] && ! echo "$PYTHON_310_PATH" | grep -q "pyenv/shims"; then
    if "$PYTHON_310_PATH" --version 2>&1 | grep -q "3.10"; then
      echo "✅ Python 3.10 found via system: $PYTHON_310_PATH"
      PYTHON_310_FOUND=true
    fi
  fi
fi

# If not found, check pyenv
if [ "$PYTHON_310_FOUND" = false ]; then
  if command -v pyenv >/dev/null 2>&1 || [ -d "$HOME/.pyenv" ]; then
    # Initialize pyenv (handles case where shell wasn't restarted)
    export PYENV_ROOT="$HOME/.pyenv"
    if [ -d "$PYENV_ROOT/bin" ]; then
      export PATH="$PYENV_ROOT/bin:$PATH"
    fi
    if command -v pyenv >/dev/null 2>&1; then
      eval "$(pyenv init - bash 2>/dev/null)" || true
    fi
    
    # Check if Python 3.10 is already installed via pyenv
    if [ -d "$HOME/.pyenv/versions/3.10.19" ]; then
      PYTHON_310_PATH="$HOME/.pyenv/versions/3.10.19/bin/python3"
      echo "✅ Python 3.10.19 found via pyenv: $PYTHON_310_PATH"
      PYTHON_310_FOUND=true
    elif command -v pyenv >/dev/null 2>&1 && pyenv versions 2>/dev/null | grep -q "3.10"; then
      PYTHON_310_VERSION=$(pyenv versions 2>/dev/null | grep "3.10" | head -1 | awk '{print $1}' | tr -d '* ')
      PYTHON_310_PATH="$HOME/.pyenv/versions/$PYTHON_310_VERSION/bin/python3"
      echo "✅ Python 3.10 found via pyenv: $PYTHON_310_PATH"
      PYTHON_310_FOUND=true
    else
      echo "❌ Python 3.10 not found via pyenv"
      echo ""
      echo "To install Python 3.10.19 via pyenv:"
      echo "  1. Ensure build dependencies are installed (see below)"
      echo "  2. Run: pyenv install 3.10.19"
      echo ""
      echo "Common installation issues:"
      echo "  - Missing build dependencies (install with command below)"
      echo "  - Network issues (check your internet connection)"
      echo "  - pyenv not in PATH (restart your shell or see docs/contributing.md)"
      exit 1
    fi
  else
    echo "❌ Python 3.10 not found and pyenv is not installed"
    echo ""
    echo "Options:"
    echo "  1. Install via system package manager (Ubuntu/Debian):"
    echo "     sudo apt install python3.10 python3.10-venv python3.10-dev"
    echo ""
    echo "  2. Install via pyenv (see docs/contributing.md for full setup):"
    echo "     First install pyenv, then: pyenv install 3.10.19"
    exit 1
  fi
fi

# Check if build tools are available (only needed for pyenv)
if [ "$PYTHON_310_FOUND" = true ] && echo "$PYTHON_310_PATH" | grep -q "pyenv"; then
  if command -v gcc >/dev/null 2>&1; then
    echo "✅ Build tools (gcc) are available"
  else
    echo "⚠️  Build tools not found (needed to install Python via pyenv)"
    echo "   Install with:"
    echo "     sudo apt update && sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev"
  fi
elif [ "$PYTHON_310_FOUND" = false ]; then
  # Only show build tools warning if we're suggesting pyenv installation
  if command -v pyenv >/dev/null 2>&1 || [ -d "$HOME/.pyenv" ]; then
    if ! command -v gcc >/dev/null 2>&1; then
      echo "⚠️  Build tools not found (needed to install Python via pyenv)"
      echo "   Install with:"
      echo "     sudo apt update && sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev"
    fi
  fi
fi

echo ""
echo "✅ Python 3.10 is available! You can use:"
echo "   poetry run poe env:py310    # Switch to Python 3.10"
echo "   poetry run poe test:py310   # Test on Python 3.10"

