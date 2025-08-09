#!/bin/bash

# Check for jq
if ! command -v jq &> /dev/null
then
    echo "Error: jq is not installed. Please install it using 'sudo apt-get install jq' or your distribution's package manager." >&2
    return 1
fi

CONFIG_PATH="/mnt/c/Users/frede/.config/ps/python_env.json"

if [ -f "$CONFIG_PATH" ]; then
    PYTHON_ENV=$(jq -r .selected_env "$CONFIG_PATH")
    WSL_PROJECT_DIR=$(jq -r .wsl_project_dir "$CONFIG_PATH")
    export PYTHON_ENV
    export WSL_PROJECT_DIR

    if [[ "$PYTHON_ENV" == "null" || -z "$PYTHON_ENV" ]]; then
        return
    fi

    if [[ "$PYTHON_ENV" == wsl:* ]]; then
        PYTHON_BIN="${PYTHON_ENV#wsl:}"
    else
        PYTHON_BIN="$PYTHON_ENV"
    fi

    PYTHON_VERSION=$("$PYTHON_BIN" --version 2>/dev/null)
    PYTHON_ENV_TYPE="global"

    if [[ "$PYTHON_ENV" == *conda* ]]; then
        PYTHON_ENV_TYPE="conda"
    elif [[ "$PYTHON_ENV" == *venv* || "$PYTHON_ENV" == *bin/python* ]]; then
        PYTHON_ENV_TYPE="venv"
    elif [[ "$PYTHON_ENV" == wsl:* ]]; then
        PYTHON_ENV_TYPE="WSL"
    fi

    export PYTHON_ENV_TYPE
    export PYTHON_VERSION
    export PS1="[($PYTHON_ENV_TYPE | $PYTHON_VERSION)] \u@\h:\w\$ "
fi


