EVE_JSON_PATH = "/var/log/suricata/eve.json"
IPSET_LIST_NAME = "blocked_ips"

# Signatures to trigger a block
SRC_KEYWORDS = ["DLL", "EXE", "SSH","ICMP"]
DST_KEYWORDS = ["Dridex"]