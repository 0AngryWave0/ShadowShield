import subprocess

def rule_exists(rule_snippet: str) -> bool:
    """
    Check if a rule snippet exists in the current iptables configuration.
    Note: Only works with a clear, identifiable string.
    """
    check = subprocess.run(f"iptables-save | grep -- \"{rule_snippet}\"", shell=True, stdout=subprocess.DEVNULL)
    return check.returncode == 0

def spoof_ip(ip: str, portspoof_port: int = 4444):
    """
    Redirect all TCP traffic from this IP to Portspoof.
    """
    rules = [
        (
            f"iptables -t nat -A PREROUTING -s {ip} -p tcp --dport 1:65535 -j REDIRECT --to-port {portspoof_port}",
            f"-A PREROUTING -s {ip} -p tcp -m tcp --dport 1:65535 -j REDIRECT --to-ports {portspoof_port}"
        ),
        (
            f"iptables -A INPUT -p tcp --dport {portspoof_port} -j ACCEPT",
            f"-A INPUT -p tcp -m tcp --dport {portspoof_port} -j ACCEPT"
        )
    ]

    for full_cmd, grep_snippet in rules:
        if not rule_exists(grep_snippet):
            subprocess.run(full_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"[+] Spoofing activated for IP: {ip} (-> {portspoof_port})")


def remove_spoof(ip: str, portspoof_port: int = 4444):
    """
    Remove Portspoof redirect rules for the given IP.
    """
    rules = [
        f"iptables -t nat -D PREROUTING -s {ip} -p tcp --dport 1:65535 -j REDIRECT --to-port {portspoof_port}",
        f"iptables -D INPUT -p tcp --dport {portspoof_port} -j ACCEPT"
    ]
    for rule in rules:
        subprocess.run(rule, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"[-] Spoofing removed for IP: {ip}")
