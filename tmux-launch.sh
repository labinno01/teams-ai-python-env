#!/bin/bash

source "$(dirname "$0")/wsl-env.sh"

SESSION="teams-ai"
WINDOW1="gemini"
WINDOW2="shell"
START_DIR="~" # Default start directory

# Set project directory if configured
if [[ -n "$WSL_PROJECT_DIR" && "$WSL_PROJECT_DIR" != "null" ]]; then
    START_DIR="~/projets/$WSL_PROJECT_DIR"
fi

# Create new session, setting the working directory for the first window
tmux new-session -d -s "$SESSION" -n "$WINDOW1" -c "$START_DIR" "python3 ~/projets/teams-ai-python-env/scripts/gemini_main.py"

# Create the second window, also setting its working directory
tmux new-window -t "$SESSION" -n "$WINDOW2" -c "$START_DIR"
tmux send-keys -t "$SESSION:$WINDOW2" "echo '🐍 Environnement : $PYTHON_ENV_TYPE'" C-m
tmux send-keys -t "$SESSION:$WINDOW2" "echo '📦 Version     : $PYTHON_VERSION'" C-m

tmux attach-session -t "$SESSION"

