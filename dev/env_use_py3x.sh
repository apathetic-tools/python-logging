#!/bin/bash
set -euo pipefail
# Switch Poetry environment to the highest available Python 3.x version
# Tries system Python first, then falls back to pyenv

PYTHON_PATH=""
HIGHEST_MINOR=0

# Check system Python versions (avoid pyenv shims)
# Try versioned python3.x in descending order (3.20 down to 3.10)
for MINOR in $(seq 20 -1 10); do
  # Check common system locations
  for POSSIBLE_PATH in "/usr/bin/python3.$MINOR" "/usr/local/bin/python3.$MINOR"; do
    if [ -x "$POSSIBLE_PATH" ]; then
      if "$POSSIBLE_PATH" --version 2>&1 | grep -q "3\.$MINOR" || "$POSSIBLE_PATH" --version 2>&1 | grep -q "^Python 3\.$MINOR"; then
        PYTHON_PATH="$POSSIBLE_PATH"
        HIGHEST_MINOR=$MINOR
        break 2
      fi
    fi
  done
  
  # Check PATH but exclude pyenv shims
  CMD_PATH=$(command -v "python3.$MINOR" 2>/dev/null || true)
  if [ -n "$CMD_PATH" ] && ! echo "$CMD_PATH" | grep -q "pyenv/shims"; then
    if "$CMD_PATH" --version 2>&1 | grep -q "3\.$MINOR" || "$CMD_PATH" --version 2>&1 | grep -q "^Python 3\.$MINOR"; then
      PYTHON_PATH="$CMD_PATH"
      HIGHEST_MINOR=$MINOR
      break
    fi
  fi
done

# Fallback to plain python3 if no versioned one found
if [ -z "$PYTHON_PATH" ]; then
  CMD_PATH=$(command -v python3 2>/dev/null)
  if [ -n "$CMD_PATH" ] && ! echo "$CMD_PATH" | grep -q "pyenv/shims"; then
    if "$CMD_PATH" --version 2>&1 | grep -q "3\."; then
      PYTHON_PATH="$CMD_PATH"
    fi
  fi
fi

# Use system Python if found
if [ -n "$PYTHON_PATH" ]; then
  poetry env use "$PYTHON_PATH" && poetry install
# Fall back to pyenv - find highest version
elif command -v pyenv >/dev/null 2>&1 || [ -d "$HOME/.pyenv" ]; then
  export PYENV_ROOT="$HOME/.pyenv"
  [ -d "$PYENV_ROOT/bin" ] && export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - bash 2>/dev/null)" || true
  
  HIGHEST_PYENV_VERSION=""
  HIGHEST_PYENV_MINOR=0
  
  # Check pyenv versions directory
  if [ -d "$HOME/.pyenv/versions" ]; then
    for VERSION_DIR in "$HOME/.pyenv/versions"/*; do
      if [ -d "$VERSION_DIR" ]; then
        VERSION_NAME=$(basename "$VERSION_DIR")
        # Extract minor version (e.g., "3.12.3" -> "12")
        MINOR=$(echo "$VERSION_NAME" | sed -n 's/^3\.\([0-9][0-9]*\)\..*/\1/p')
        if [ -n "$MINOR" ] && [ "$MINOR" -gt "$HIGHEST_PYENV_MINOR" ]; then
          HIGHEST_PYENV_MINOR=$MINOR
          HIGHEST_PYENV_VERSION="$VERSION_NAME"
        fi
      fi
    done
  fi
  
  # Also check pyenv versions command output
  if command -v pyenv >/dev/null 2>&1; then
    pyenv versions 2>/dev/null | while IFS= read -r VERSION_LINE; do
      VERSION_NAME=$(echo "$VERSION_LINE" | awk '{print $1}' | tr -d '* ')
      MINOR=$(echo "$VERSION_NAME" | sed -n 's/^3\.\([0-9][0-9]*\)\..*/\1/p')
      if [ -n "$MINOR" ] && [ "$MINOR" -gt "$HIGHEST_PYENV_MINOR" ]; then
        HIGHEST_PYENV_MINOR=$MINOR
        HIGHEST_PYENV_VERSION="$VERSION_NAME"
      fi
    done || true
  fi
  
  if [ -n "$HIGHEST_PYENV_VERSION" ] && [ -d "$HOME/.pyenv/versions/$HIGHEST_PYENV_VERSION" ]; then
    poetry env use "$HOME/.pyenv/versions/$HIGHEST_PYENV_VERSION/bin/python3" && poetry install
  else
    echo "❌ No Python 3.x version found. Please install Python 3.10 or newer."
    exit 1
  fi
else
  echo "❌ No Python 3.x version found. Please install Python 3.10 or newer."
  exit 1
fi

