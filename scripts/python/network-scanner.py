#!/usr/bin/env python3
"""
Network Scanner – Portfolio Edition
Scans local network, detects live hosts + open ports, exports JSON/CSV, compares baseline.

Usage:
    python3 network-scanner.py --range 192.168.1.0/24
    python3 network-scanner.py --baseline scan.json
"""

import argparse
import json
import csv
import socket
import threading
import time
from datetime import datetime
from typing import List, Dict, Set
import netifaces
from scapy.all import ARP, Ether, srp

# -------------------------------
# Configuration
# -------------------------------
DEFAULT_PORTS = [22, 80, 443, 3306, 8080, 8443]
TIMEOUT = 1.0
THREADS = 100

# -------------------------------
# Helper: Get local network range
# -------------------------------
def get_local_network() -> str:
    """Auto-detect local subnet (e.g., 192.168.1.0/24)"""
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                mask = addr['netmask']
                if not ip.startswith('127.') and mask:
                    # Simple CIDR calc
                    import ipaddress
                    network = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
                    return str(network)
    return "192.168.1.0/24"  # fallback

# -------------------------------
# Step 1: Discover live hosts (ARP ping)
# -------------------------------
def discover_hosts(network: str) -> List[str]:
    print(f"[+] Scanning network: {network}")
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    answered, _ = srp(packet, timeout=2, verbose=0)
    return sorted([recv.psrc for _, recv in answered])

# -------------------------------
# Step 2: Port scan (multi-threaded)
# -------------------------------
def scan_port(ip: str, port: int, open_ports: Set[int]):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.add(port)
        sock.close()
    except:
        pass

def scan_host_ports(ip: str, ports: List[int]) -> Dict:
    open_ports = set()
    threads = []
    for port in ports:
        t = threading.Thread(target=scan_port, args=(ip, port, open_ports))
        threads.append(t)
        t.start()
        if len(threads) >= THREADS:
            for t in threads:
                t.join()
            threads = []
    for t in threads:
        t.join()
    return {
        "ip": ip,
        "open_ports": sorted(list(open_ports)),
        "scanned_at": datetime.now().isoformat()
    }

# -------------------------------
# Step 3: Export results
# -------------------------------
def save_json(results: List[Dict], path: str):
    with open(path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] JSON saved: {path}")

def save_csv(results: List[Dict], path: str):
    if not results:
        return
    keys = results[0].keys()
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"[+] CSV saved: {path}")

# -------------------------------
# Step 4: Compare with baseline
# -------------------------------
def compare_with_baseline(current: List[Dict], baseline_path: str) -> List[Dict]:
    if not baseline_path:
        return []
    try:
        with open(baseline_path) as f:
            old = json.load(f)
    except:
        print(f"[!] Could not load baseline: {baseline_path}")
        return []

    old_map = {h['ip']: set(h['open_ports']) for h in old}
    changes = []
    for host in current:
        ip = host['ip']
        new_ports = set(host['open_ports'])
        old_ports = old_map.get(ip, set())
        added = new_ports - old_ports
        removed = old_ports - new_ports
        if added or removed:
            changes.append({
                "ip": ip,
                "added_ports": sorted(added),
                "removed_ports": sorted(removed),
                "detected_at": host['scanned_at']
            })
    return changes

# -------------------------------
# Main
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="Network Scanner – Live Hosts + Open Ports")
    parser.add_argument('--range', type=str, help="CIDR range (e.g., 192.168.1.0/24)")
    parser.add_argument('--ports', type=str, help="Comma-separated ports (default: 22,80,443,...)")
    parser.add_argument('--output', type=str, default="scan", help="Output prefix (scan.json, scan.csv)")
    parser.add_argument('--baseline', type=str, help="Compare with previous scan.json")
    args = parser.parse_args()

    # Resolve network
    network = args.range or get_local_network()
    ports = [int(p.strip()) for p in (args.ports or ",".join(map(str, DEFAULT_PORTS))).split(",") if p.strip()]

    # Discover hosts
    live_hosts = discover_hosts(network)
    if not live_hosts:
        print("[!] No live hosts found.")
        return

    print(f"[+] Found {len(live_hosts)} live hosts. Scanning ports...")

    # Scan ports
    results = []
    for ip in live_hosts:
        print(f"    Scanning {ip}...")
        result = scan_host_ports(ip, ports)
        results.append(result)

    # Export
    json_path = f"{args.output}.json"
    csv_path = f"{args.output}.csv"
    save_json(results, json_path)
    save_csv(results, csv_path)

    # Compare
    changes = compare_with_baseline(results, args.baseline)
    if changes:
        change_path = f"{args.output}_changes.json"
        save_json(changes, change_path)
        print(f"[!] {len(changes)} hosts changed! See {change_path}")
    else:
        print("[+] No changes detected.")

    print(f"\nScan complete! Results in {json_path} and {csv_path}")

if __name__ == "__main__":
    main()