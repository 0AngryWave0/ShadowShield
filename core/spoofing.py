import subprocess

def spoof_ip(ip: str, portspoof_port: int = 4444):
    """
    Redirect all TCP traffic from the given IP to the local Portspoof service.
    """
    rule = (
        f"iptables -t nat -A PREROUTING -s {ip} -p tcp --dport 1:65535 "
        f"-j REDIRECT --to-port {portspoof_port}"
    )
    subprocess.run(rule, shell=True)
    print(f"[+] Spoofed IP {ip} (redirected all TCP to portspoof on port {portspoof_port})")

def remove_spoof(ip: str, portspoof_port: int = 4444):
    """
    Remove spoofing rule for the given IP (cleanup).
    """
    rule = (
        f"iptables -t nat -D PREROUTING -s {ip} -p tcp --dport 1:65535 "
        f"-j REDIRECT --to-port {portspoof_port}"
    )
    subprocess.run(rule, shell=True)
    print(f"[-] Removed spoofing for IP {ip}")
