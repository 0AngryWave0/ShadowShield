import subprocess
from core.config import IPSET_LIST_NAME
from core.state import add_blocked_ip, is_ip_blocked, get_local_ips, remove_blocked_ip, load_blocked_ips
from core.spoofing import remove_spoof

# Initialize
blocked_ips = load_blocked_ips()

def block_ip(ip):
    local_ips = get_local_ips()
    if ip in local_ips:
        return

    if not is_ip_blocked(ip):
        subprocess.run(f"ipset add {IPSET_LIST_NAME} {ip}", shell=True)
        add_blocked_ip(ip)
        print(f"[+] Blocked IP: {ip}")

def unblock_ip(ip):
    if not is_ip_blocked(ip):
        print(f"[!] IP {ip} is not currently blocked.")
        return

    # Remove from ipset (if it exists)
    result = subprocess.run(
        f"ipset del {IPSET_LIST_NAME} {ip}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    remove_spoof(ip)
    remove_blocked_ip(ip)
    print(f"[+] Unblocked IP: {ip}")

def restore_blocked_ips():
    for ip in blocked_ips:
        # Check if already in ipset
        result = subprocess.run(
            f"ipset test {IPSET_LIST_NAME} {ip}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            subprocess.run(f"ipset add {IPSET_LIST_NAME} {ip}", shell=True)


def ensure_iptables_rule():
    rule = f"iptables -t nat -C PREROUTING -m set --match-set {IPSET_LIST_NAME} src -p tcp -j REDIRECT --to-port 4444 || " \
           f"iptables -t nat -A PREROUTING -m set --match-set {IPSET_LIST_NAME} src -p tcp -j REDIRECT --to-port 4444"
    result = subprocess.run(rule, shell=True)
    if result.returncode == 0:
        print("[+] iptables NAT redirection rule verified or inserted.")
    else:
        print("[!] Failed to apply NAT redirection rule. You might need sudo.")
