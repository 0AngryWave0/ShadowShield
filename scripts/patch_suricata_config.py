import re

RULE_PATH = "/opt/shadowshield/rules"
RULE_FILE = "shadowshield.rules"
CONFIG_PATH = "/etc/suricata/suricata.yaml"

with open(CONFIG_PATH, "r") as f:
    content = f.read()

# Patch default-rule-path
content = re.sub(
    r"default-rule-path\s*:\s*.*",
    f"default-rule-path: {RULE_PATH}",
    content
)


# Patch rule-files section to only contain our file
content = re.sub(
    r"rule-files:\s*\n(?:\s*-\s*.*\n)*",
    f"rule-files:\n  - {RULE_FILE}\n",
    content
)

with open(CONFIG_PATH, "w") as f:
    f.write(content)

print(f"[+] Suricata config updated to use rules from {RULE_PATH}/{RULE_FILE}")
