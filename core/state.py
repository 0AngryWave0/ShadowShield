import socket
import psutil
import ipaddress
import json
import os

BLOCKLIST_FILE = "blocked.json"

def load_blocked_ips():
    if os.path.exists(BLOCKLIST_FILE):
        with open(BLOCKLIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_blocked_ips(ips):
    with open(BLOCKLIST_FILE, "w") as f:
        json.dump(list(ips), f)

# Initialize
blocked_ips = load_blocked_ips()

def add_blocked_ip(ip):
    blocked_ips.add(ip)
    save_blocked_ips(blocked_ips)

def remove_blocked_ip(ip):
    blocked_ips.discard(ip)
    save_blocked_ips(blocked_ips)

def is_ip_blocked(ip):
    return ip in blocked_ips

def get_local_ips():
    """Get all local IPs for this machine (loopback, LAN, etc.)"""
    local_ips = {"127.0.0.1", "localhost"}

    # Get hostname IP
    try:
        local_ips.add(socket.gethostbyname(socket.gethostname()))
    except:
        pass

    # Get all network interface IPs
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    local_ips.add(addr.address)
    except:
        pass

    return local_ips

def is_valid_ip(ip):
    try:
        return ipaddress.ip_address(ip).version == 4
    except:
        return False