#!/bin/bash

# This script is a wrapper for the sshkeys command.
# It activates the virtual environment and then runs the sshkeys command.

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Activate the virtual environment
source "$PROJECT_DIR/.venv/bin/activate"

# Run the sshkeys command with all the arguments passed to the wrapper script
python -m sshkeys "$@"
