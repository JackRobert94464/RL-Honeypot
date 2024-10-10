import socket
import json
import subprocess
import pymongo
from mininet.net import Mininet
from mininet.node import OVSSwitch

# Function to retrieve topology data from MongoDB
def retrieve_topo_from_mongoDB():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["network_topology"]
    collection = db["nodes"]
    # Create a dictionary mapping IP addresses to node names
    topo_dict = {node["node_ipv4"]: node["node_name"] for node in collection.find({}, {"_id": 0, "node_ipv4": 1, "node_name": 1})}
    return topo_dict

topo_dict = retrieve_topo_from_mongoDB()
print("Topology data retrieved from MongoDB:", topo_dict)

# Function to send data using curl
def communicate_curl(dst, port, prefix, data):
    print(f"Sending data to {dst}:{port}")
    curl_command = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(data)}' http://{dst}:{port}/{prefix}"
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    return result.stdout



# Function to send response back to Mininet
def send_response_to_mininet(response_data):
    mininet_host = '127.0.0.1'
    mininet_port = 10980
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((mininet_host, mininet_port))
        s.sendall(json.dumps(response_data).encode('utf-8'))
        print(f"Sent response to Mininet: {response_data}")

# Server to receive snort-ryu controller input and process it
def start_server(ip_address='0.0.0.0', port=9800):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip_address, port))
        server_socket.listen(1)
        print(f"Server listening on {ip_address}:{port}")

        # Initialize buffer to track compromised nodes, preserving state
        compromised_nodes = [0] * len(topo_dict)

        # Precompute IP to index mapping for efficiency
        ip_to_index = {ip: idx for idx, ip in enumerate(topo_dict.keys())}

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"Connection from {client_address}")
                data = client_socket.recv(100000)
                if data:
                    try:
                        json_data = data.decode('utf-8', "ignore")
                        cleaned_data = json_data.replace('\\u0000', '')
                        print("Cleaned data:", cleaned_data)

                        data_dict = json.loads(cleaned_data)

                        if data_dict.get("alertmsg") == "Node compromised":
                            for content in data_dict.get("content", []):
                                if "ipv4" in content:
                                    # Extract src_ip and dst_ip from the content string
                                    try:
                                        src_ip = content.split("src='")[1].split("'")[0]
                                        dst_ip = content.split("dst='")[1].split("'")[0]
                                    except IndexError:
                                        print("Failed to parse IP addresses from content.")
                                        continue

                                    # Get indices of src and dst
                                    src_idx = ip_to_index.get(src_ip)
                                    dst_idx = ip_to_index.get(dst_ip)

                                    if src_idx is None or dst_idx is None:
                                        print(f"Unknown IPs: src_ip={src_ip}, dst_ip={dst_ip}")
                                        continue

                                    # If src is h1337 (10.0.0.12), mark dst as compromised (entrypoint)
                                    if src_ip == "10.0.0.12":
                                        if compromised_nodes[dst_idx] == 0:
                                            compromised_nodes[dst_idx] = 1
                                            print(f"Entrypoint detected at node {topo_dict[dst_ip]} (IP: {dst_ip}), marking as compromised.")
                                    else:
                                        # If src is already compromised, mark dst as compromised
                                        if compromised_nodes[src_idx] == 1:
                                            if compromised_nodes[dst_idx] == 0:
                                                compromised_nodes[dst_idx] = 1
                                                print(f"Compromise detected: node {topo_dict[src_ip]} (IP: {src_ip}) attacked node {topo_dict[dst_ip]} (IP: {dst_ip}), marking {topo_dict[dst_ip]} as compromised.")
                                        else:
                                            # Optionally, log that src is not compromised
                                            print(f"Attack from {topo_dict[src_ip]} (IP: {src_ip}) which is not marked as compromised.")

                            # Create a JSON payload with the network state
                            payload = {
                                'network_state': compromised_nodes,
                                'num_honeypots': 2  # Set the number of honeypots, temporary value
                            }
                            # Send the payload to localhost at port number 35025
                            response = communicate_curl('localhost', 35025, 'predict', payload)
                            response_dict = json.loads(response)
                            deployment_targets = response_dict.get("deployment_targets", [])

                            # Send response back to Mininet
                            send_response_to_mininet(response_dict)

                        else:
                            print("Data received, but no node compromise detected")

                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON data: {e}")
                    except UnicodeDecodeError as e:
                        print(f"Failed to decode data to UTF-8: {e}")

if __name__ == "__main__":
    start_server()