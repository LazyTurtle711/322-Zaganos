#!/bin/bash

# Python script to run at boot
SCRIPT_PATH="/home/wro/wro/bin/python"
PYTHON_FILE="/home/wro/code/görve1.py"

# Run the script with sudo
sudo "$SCRIPT_PATH" "$PYTHON_FILE"