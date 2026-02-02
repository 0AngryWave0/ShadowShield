EVE_JSON_PATH = "/opt/shadowshield/logs/eve.json"  
IPSET_LIST_NAME = "blocked_ips"

COWRIE_CMD = "/opt/cowrie/bin/cowrie"              
COWRIE_ENV = "/opt/cowrie/cowrie-env/bin/activate" 
USER = "root"                                       

# Signatures to trigger a block
SRC_KEYWORDS = ["DLL", "EXE", "SSH", "ICMP"]
DST_KEYWORDS = ["Dridex"]
