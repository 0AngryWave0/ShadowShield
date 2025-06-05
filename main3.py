# run.py

import argparse
from rich.console import Console
from rich.table import Table
from core.monitor import read_eve, process_alerts, monitor_loop
from core.state import blocked_ips
from core.blocker import ensure_iptables_rule, unblock_ip
from tui.dashboard import ShadowShield
import sys
import subprocess
import os
import time

console = Console()

def setup_ipset_and_iptables():
    def run_cmd(cmd):
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode, result.stdout.decode().strip(), result.stderr.decode().strip()

    # 1. Check if ipset exists
    code, _, _ = run_cmd("ipset list blocked_ips")
    if code != 0:
        print("[*] Creating ipset 'blocked_ips'...")
        code, _, err = run_cmd("ipset create blocked_ips hash:ip")
        if code != 0:
            print(f"[!] Failed to create ipset: {err}")
            return
        # Important: wait a bit for kernel to register the set
        time.sleep(0.5)

    # Double-check to avoid race condition
    recheck_code, _, _ = run_cmd("ipset list blocked_ips")
    if recheck_code != 0:
        print("[!] ipset still not available after creation. Aborting iptables setup.")
        return

    # 2. Check if iptables NAT redirection rule exists
    code, _, _ = run_cmd("iptables -t nat -C PREROUTING -p tcp -m set --match-set blocked_ips src -j REDIRECT --to-port 4444")
    if code != 0:
        print("[+] Adding iptables redirect rule for portspoof...")
        code, _, err = run_cmd("iptables -t nat -A PREROUTING -p tcp -m set --match-set blocked_ips src -j REDIRECT --to-port 4444")
        if code != 0:
            print(f"[!] Failed to apply NAT redirection rule: {err}")
    else:
        print("[=] iptables redirect rule already exists.")


def show_alerts():
    logs = read_eve()
    alerts = [l for l in logs if l.get("event_type") == "alert"][-10:]

    table = Table(title="Latest Suricata Alerts")
    table.add_column("Signature", style="bold red")
    table.add_column("Src IP", style="cyan")
    table.add_column("Dst IP", style="green")

    for a in alerts:
        sig = a["alert"]["signature"]
        src = a.get("src_ip", "-")
        dst = a.get("dest_ip", "-")
        table.add_row(sig, src, dst)

    console.print(table)

def list_blocked():
    table = Table(title="Blocked IPs")
    table.add_column("IP", style="yellow")

    for ip in blocked_ips:
        table.add_row(ip)

    console.print(table)

def launch_dashboard():
    app = ShadowShield()
    app.run()

def main():
    parser = argparse.ArgumentParser(description="🔥 ShadowShield Firewall CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("monitor", help="Run Suricata monitor loop")
    subparsers.add_parser("dashboard", help="Run terminal dashboard")
    subparsers.add_parser("show-alerts", help="Show latest Suricata alerts")
    subparsers.add_parser("blocked", help="Show blocked IPs")

    unblock = subparsers.add_parser("unblock", help="Unblock an IP address")
    unblock.add_argument("ip", help="IP address to unblock")

    args = parser.parse_args()

    if args.command == "monitor":
        if os.geteuid() != 0:
            print("⚠️  You need to run this as root (sudo) to block IPs.")
            exit(1)
        ensure_iptables_rule()
        setup_ipset_and_iptables()
        monitor_loop()
    elif args.command == "dashboard":
        launch_dashboard()
    elif args.command == "show-alerts":
        show_alerts()
    elif args.command == "blocked":
        list_blocked()
    elif args.command == "unblock":
        unblock_ip(args.ip)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
