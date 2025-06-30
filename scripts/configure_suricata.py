import os
import re

CONFIG_PATH = "/etc/suricata/suricata.yaml"
LOG_PATH = "/opt/shadowshield/logs/eve.json"

with open(CONFIG_PATH, "r") as f:
    content = f.read()

# Regex to patch the eve.json log path
content = re.sub(r'filename\s*:\s*.*eve\.json', f'filename: {LOG_PATH}', content)


with open(CONFIG_PATH, "w") as f:
    f.write(content)

print(f"Suricata logging path set to {LOG_PATH}")
