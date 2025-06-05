import subprocess
import os
from core.config import COWRIE_ENV, COWRIE_CMD, USER
def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode, result.stdout.decode().strip(), result.stderr.decode().strip()

# --------------------------
# Suricata Service
# --------------------------
def start_suricata():
    return run_cmd("sudo systemctl start suricata")

def stop_suricata():
    return run_cmd("sudo systemctl stop suricata")

def is_suricata_running():
    _, out, _ = run_cmd("systemctl is-active suricata")
    return out.strip() == "active"

# --------------------------
# Portspoof Service
# --------------------------
def start_portspoof():
    return run_cmd("sudo systemctl start portspoof")

def stop_portspoof():
    return run_cmd("sudo systemctl stop portspoof")

def is_portspoof_running():
    _, out, _ = run_cmd("systemctl is-active portspoof")
    return out.strip() == "active"

# --------------------------
# DROP Rule (iptables)
# --------------------------
def enable_drop_rule():
    return run_cmd("sudo iptables -C INPUT -m set --match-set blocked_ips src -j DROP || sudo iptables -I INPUT -m set --match-set blocked_ips src -j DROP")

def disable_drop_rule():
    return run_cmd("sudo iptables -D INPUT -m set --match-set blocked_ips src -j DROP")

def is_drop_rule_enabled():
    code, out, _ = run_cmd("sudo iptables -L INPUT -n")
    return "match-set blocked_ips src" in out

# --------------------------
# Cowrie Honeypot Service
# --------------------------
def cowrie_cmd(cmd):
    full_cmd = f"source {COWRIE_ENV} && {COWRIE_CMD} {cmd}"
    return run_cmd(f"bash -c '{full_cmd}'")

def start_cowrie():
    return subprocess.run([
        "sudo", "-u", USER, "bash", "-c",
        f"source {COWRIE_ENV} && {COWRIE_CMD} start"
    ])

def stop_cowrie():
    return subprocess.run([
        "sudo", "-u", USER, "bash", "-c",
        f"source {COWRIE_ENV} && {COWRIE_CMD} stop"
    ])


def is_cowrie_running():
    result = subprocess.run([
        "sudo", "-u", USER, "bash", "-c",
        f"source {COWRIE_ENV} && {COWRIE_CMD} status"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out = result.stdout.decode().lower()
    return "is running" in out and "not running" not in out
