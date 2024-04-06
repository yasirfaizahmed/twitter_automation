#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


# Define paths
BASE_DIR=$SCRIPT_DIR

# Change directory to the script's directory
cd "$BASE_DIR" || exit


VENV_DIR="$BASE_DIR/.venv"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
PYTHON_EXECUTABLE="$VENV_DIR/bin/python3"
SCRIPT_TO_RUN="$BASE_DIR/examples/collect_tweet_data.py"

# Activate virtual environment
source "$ACTIVATE_SCRIPT"

# Export PYTHONPATH
export PYTHONPATH="$BASE_DIR"

# Export Driver path
export DRIVER_PATH='/usr/bin/chromedriver'

# Export Bot Metadata file
export METADATA='/home/pi/Documents/secrets/bot_metadata.json'


# Run Python script
"$PYTHON_EXECUTABLE" "$SCRIPT_TO_RUN"

# # Deactivate virtual environment (optional)
deactivate