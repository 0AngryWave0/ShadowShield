# core/monitor.py

import json
import time
from core.config import EVE_JSON_PATH, SRC_KEYWORDS, DST_KEYWORDS
from core.blocker import block_ip
from core.state import is_valid_ip
from core.spoofing import spoof_ip

seen_ips = set()

def read_eve():
    with open(EVE_JSON_PATH, 'r') as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]

def process_alerts():
    logs = read_eve()
    for log in logs:
        if log.get("event_type") != "alert":
            continue

        sig = log["alert"]["signature"]
        src_ip = log.get("src_ip")
        dst_ip = log.get("dest_ip")

        if not is_valid_ip(src_ip):
            continue

        for keyword in SRC_KEYWORDS:
            if keyword in sig:
                block_ip(src_ip)

        for keyword in DST_KEYWORDS:
            if keyword in sig and is_valid_ip(dst_ip):
                block_ip(dst_ip)

        print(f"[DEBUG] Signature: {sig}")
        if any(kw in sig.lower() for kw in ["nmap", "scan"]) and src_ip not in seen_ips:
            print(f"[!] Spoofing {src_ip} for scan: {sig}")
            spoof_ip(src_ip)
            seen_ips.add(src_ip)

def monitor_loop():
    print(f"[*] Starting monitoring loop on: {EVE_JSON_PATH} (CTRL+C to stop)...")
    while True:
        try:
            process_alerts()
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n[!] Stopped monitoring.")
            break
