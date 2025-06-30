# main.py

import argparse
import subprocess
import sys
import os
import time
from rich.console import Console
from rich.table import Table
from core.monitor import read_eve, process_alerts, monitor_loop
from core.state import blocked_ips
from core.blocker import ensure_iptables_rule, unblock_ip, restore_blocked_ips
from tui.cowrie_logs import CowrieLogViewer
from core.services import (
    start_suricata,
    stop_suricata,
    is_suricata_running,
    start_portspoof,
    stop_portspoof,
    is_portspoof_running,
    enable_drop_rule,
    disable_drop_rule,
    is_drop_rule_enabled,
    start_cowrie,
    stop_cowrie,
    is_cowrie_running
)
from tui.dashboard import ShadowShield

console = Console()

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

def setup_ipset():
    def run_cmd(cmd):
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode, result.stdout.decode().strip(), result.stderr.decode().strip()

    code, _, _ = run_cmd("ipset list blocked_ips")
    if code != 0:
        print("[*] Creating ipset 'blocked_ips'...")
        code, _, err = run_cmd("ipset create blocked_ips hash:ip")
        if code != 0:
            print(f"[!] Failed to create ipset: {err}")
            return
        time.sleep(0.5)

    recheck_code, _, _ = run_cmd("ipset list blocked_ips")
    if recheck_code != 0:
        print("[!] ipset still not available after creation. Aborting iptables setup.")
        return

def list_blocked():
    table = Table(title="Blocked IPs")
    table.add_column("IP", style="yellow")

    for ip in blocked_ips:
        table.add_row(ip)

    console.print(table)

def launch_dashboard():
    app = ShadowShield()
    app.run()

def show_service_status():
    status_table = Table(title="Service Status")
    status_table.add_column("Service")
    status_table.add_column("Status", style="bold")

    status_table.add_row("Suricata", "🟢 Running" if is_suricata_running() else "🔴 Stopped")
    status_table.add_row("Portspoof", "🟢 Running" if is_portspoof_running() else "🔴 Stopped")
    status_table.add_row("DROP Rule", "🟢 Enabled" if is_drop_rule_enabled() else "🔴 Disabled")
    status_table.add_row("HoneyPot", "🟢 Enabled" if is_cowrie_running() else "🔴 Disabled")
    console.print(status_table)

def main():
    parser = argparse.ArgumentParser(description="🔥 ShadowShield Firewall CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("monitor", help="Run Suricata monitor loop")
    subparsers.add_parser("show-alerts", help="Show latest Suricata alerts")
    subparsers.add_parser("blocked", help="Show blocked IPs")

    unblock = subparsers.add_parser("unblock", help="Unblock an IP address")
    unblock.add_argument("ip", help="IP address to unblock")

    subparsers.add_parser("start-suricata", help="Start Suricata service")
    subparsers.add_parser("stop-suricata", help="Stop Suricata service")
    subparsers.add_parser("start-portspoof", help="Start Portspoof service")
    subparsers.add_parser("stop-portspoof", help="Stop Portspoof service")
    subparsers.add_parser("enable-drop", help="Enable iptables DROP rule for blocked IPs")
    subparsers.add_parser("disable-drop", help="Disable iptables DROP rule for blocked IPs")
    subparsers.add_parser("start-honeypot", help="Start Honeypot service")
    subparsers.add_parser("stop-honeypot", help="Stop Honeypot service")
    subparsers.add_parser("honeypot-logs", help="View honeypot logs")


    args = parser.parse_args()

    if not args.command:
        show_service_status()
        parser.print_help()
        sys.exit(0)

    if args.command == "monitor":
        if os.geteuid() != 0:
            print("⚠️  You need to run this as root (sudo) to block IPs.")
            exit(1)
        setup_ipset()
        ensure_iptables_rule()
        restore_blocked_ips()
        monitor_loop()
    elif args.command == "show-alerts":
        show_alerts()
    elif args.command == "blocked":
        list_blocked()
    elif args.command == "unblock":
        unblock_ip(args.ip)
    elif args.command == "start-suricata":
        start_suricata()
    elif args.command == "stop-suricata":
        stop_suricata()
    elif args.command == "start-portspoof":
        start_portspoof()
    elif args.command == "stop-portspoof":
        stop_portspoof()
    elif args.command == "enable-drop":
        enable_drop_rule()
    elif args.command == "disable-drop":
        disable_drop_rule()
    elif args.command == "start-honeypot":
        start_cowrie()
    elif args.command == "stop-honeypot":
        stop_cowrie()
    elif args.command == "honeypot-logs":
        CowrieLogViewer().run()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
