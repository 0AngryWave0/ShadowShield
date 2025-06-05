EVE_JSON_PATH = "/var/log/suricata/eve.json"
IPSET_LIST_NAME = "blocked_ips"
COWRIE_CMD = "/home/gogonu/cowrie/bin/cowrie"
COWRIE_ENV = "/home/gogonu/cowrie/cowrie-env/bin/activate"
USER="gogonu"

# Signatures to trigger a block
SRC_KEYWORDS = ["DLL", "EXE", "SSH","ICMP"]
DST_KEYWORDS = ["Dridex"]