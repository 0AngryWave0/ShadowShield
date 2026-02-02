#!/bin/bash

COWRIE_CFG="/opt/cowrie/etc/cowrie.cfg"
LOG_PATH="/opt/shadowshield/logs/cowrie.log"

# Enable and redirect JSON logging
if grep -q "\[output_jsonlog\]" "$COWRIE_CFG"; then
    # Section exists: patch it
    sed -i "s|^filename = .*|filename = $LOG_PATH|" "$COWRIE_CFG"
else
    # Add the section at the end
    echo -e "\n[output_jsonlog]\nenabled = true\nfilename = $LOG_PATH" >> "$COWRIE_CFG"
fi

echo "Cowrie logging path set to $LOG_PATH"
