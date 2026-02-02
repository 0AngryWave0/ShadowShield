import subprocess

def iptables_rule_exists(table: str, chain: str, match: str) -> bool:
    cmd = f"iptables -t {table} -S {chain}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    rules = result.stdout.decode().splitlines()
    return any(match in rule for rule in rules)

def spoof_ip(ip: str, portspoof_port: int = 4444):
    """
    Redirect all TCP traffic from this IP to Portspoof via PREROUTING.
    """
    prerouting_rule = f"-A PREROUTING -s {ip} -p tcp --dport 1:65535 -j REDIRECT --to-port {portspoof_port}"
    
    if not iptables_rule_exists("nat", "PREROUTING", prerouting_rule):
        subprocess.run(
            f"iptables -t nat -A PREROUTING -s {ip} -p tcp --dport 1:65535 -j REDIRECT --to-port {portspoof_port}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[+] Spoofing rule inserted for {ip}")
    else:
        print(f"[=] Spoofing rule already exists for {ip}")

    print(f"[✓] Spoofing active for IP: {ip} → Port {portspoof_port}")


def remove_spoof(ip: str, portspoof_port: int = 4444):
    """
    Remove Portspoof redirect rule from PREROUTING for the given IP.
    """
    rule_match = f"-A PREROUTING -s {ip} -p tcp --dport 1:65535 -j REDIRECT --to-port {portspoof_port}"

    # Check if the rule exists and delete it
    result = subprocess.run("iptables -t nat -S PREROUTING", shell=True, stdout=subprocess.PIPE)
    rules = result.stdout.decode().splitlines()

    for rule in rules:
        if rule_match in rule:
            delete_cmd = rule.replace("-A", "-D")
            subprocess.run(f"iptables -t nat {delete_cmd}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[-] Removed spoofing rule for {ip}")
            break
    else:
        print(f"[!] No spoofing rule found for {ip}")

    subprocess.run(
        f"iptables -D INPUT -p tcp --dport {portspoof_port} -j ACCEPT",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
