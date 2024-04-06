#!/bin/bash

# add below line in crontable to run daily at 10:30 using command 'crontab -e'
# 30 22  * * * /home/pi/Documents/python_codes/twitter_automation/automation/ramdan_progress_bar/ramazan_progress_bar.py



# Get the directory of the script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


# Define paths
BASE_DIR=$SCRIPT_DIR/../../

# Change directory to the script's directory
cd "$BASE_DIR" || exit


VENV_DIR="$BASE_DIR/.venv"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
PYTHON_EXECUTABLE="$VENV_DIR/bin/python3"
SCRIPT_TO_RUN="$BASE_DIR/automation/ramdan_progress_bar/ramazan_progress_bar.py"

# Activate virtual environment
source "$ACTIVATE_SCRIPT"

# Export PYTHONPATH
export PYTHONPATH="$BASE_DIR"

# Export Driver path
export DRIVER_PATH='/usr/bin/chromedriver'

# Export Bot Metadata file
export METADATA='/home/pi/Documents/secrets/bot_metadata.json'

# checkout to pi branch
git checkout -f pi

# Run Python script
"$PYTHON_EXECUTABLE" "$SCRIPT_TO_RUN"

# # Deactivate virtual environment (optional)
deactivate
