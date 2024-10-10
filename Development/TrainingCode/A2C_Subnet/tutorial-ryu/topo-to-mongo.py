import re
import pymongo
from ipaddress import ip_address

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["network_topology"]
collection = db["topology"]

# Sample Mininet dump
mininet_dump = """
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 h9 h10 h32 h1337 
*** Adding switches:
s1 s2 s3 s4 s111 
*** Adding links:
(h1, s1) (h2, s1) (h3, s2) (h4, s2) (h5, s2) (h6, s3) (h7, s3) (h8, s3) (h9, s4) (h10, s4) (s1, s111) (s2, s111) (s3, s111) (s4, s111) (s111, h32) (s111, h1337)
"""

# Parse Mininet dump
hosts = re.findall(r'\b(h\d+)\b', mininet_dump)
switches = re.findall(r'\b(s\d+)\b', mininet_dump)
links = re.findall(r'\((h\d+), (s\d+)\)', mininet_dump)

# Set IP addresses for each host
ip_base = ip_address("10.0.0.1")
host_ips = {host: str(ip_base + i) for i, host in enumerate(hosts)}

# Generate topology data
topology_data = {
    "nodes": []
}

# Create a dictionary to store connections for each node
connections = {node: [] for node in hosts + switches}

# Populate the connections dictionary
for host, switch in links:
    connections[host].append(switch)
    connections[switch].append(host)

# Add switch-to-switch connections
switch_links = re.findall(r'\((s\d+), (s\d+)\)', mininet_dump)
for switch1, switch2 in switch_links:
    connections[switch1].append(switch2)
    connections[switch2].append(switch1)

# Generate node data with connections
for node in hosts + switches:
    node_data = {
        "node_name": node,
        "node_EPSS": None,  # Placeholder, as EPSS scores are computed after CVE collection
        "node_ipv4": host_ips.get(node, None),
        "node_connections": [{"connected_to": connected_node} for connected_node in connections[node]],
        "node_subnet": None  # Placeholder, as subnet information is not provided
    }
    topology_data["nodes"].append(node_data)

# Insert into MongoDB
collection.replace_one({}, topology_data, upsert=True)

print("Topology data successfully updated to MongoDB.")

# Placeholder for future CVE retrieval
def check_cve_for_host(hostname):
    # Future plan to use an open-source tool like `cve-search` or any public API
    # to retrieve CVEs for the host. For now, it's just a placeholder.
    cve_names = ["CVE-2021-12345", "CVE-2022-6789"]  # Example output
    print(f"Host {hostname} CVEs: {', '.join(cve_names)}")
    return cve_names

# Example usage of the placeholder function
for host in hosts:
    check_cve_for_host(host)
