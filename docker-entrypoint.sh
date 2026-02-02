#!/bin/bash

# Activate virtualenv
source /opt/shadowshield/.venv/bin/activate
#Clear iptables rules
if [[ "$1" == "reset" ]]; then
    echo "[*] Resetting iptables and ipset..."
    iptables -F
    iptables -t nat -F
    ipset flush blocked_ips 2>/dev/null || true
    shift  # Remove "reset" so main.py gets proper args
fi
# Ensure log files exist
mkdir -p logs rules
touch logs/cowrie.log
touch logs/eve.json
touch rules/shadowshield.rules
# Run the ShadowShield CLI or TUI
exec python3 main.py "$@"
