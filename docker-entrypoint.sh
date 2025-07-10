#!/bin/bash

# Activate virtualenv
source /opt/shadowshield/.venv/bin/activate
#Clear iptables rules
iptables -F
iptables -t nat -F
# Ensure log files exist
mkdir -p logs rules
touch logs/cowrie.log
touch logs/eve.json
touch rules/shadowshield.rules
# Run the ShadowShield CLI or TUI
exec python3 main.py "$@"
