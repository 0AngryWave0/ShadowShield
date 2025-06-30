#!/bin/bash

# Activate virtualenv
source /opt/shadowshield/.venv/bin/activate

# Ensure log files exist
mkdir -p logs rules
touch logs/cowrie.log
touch logs/eve.json
touch rules/shadowshield.rules
# Run the ShadowShield CLI or TUI
exec python3 main.py "$@"
