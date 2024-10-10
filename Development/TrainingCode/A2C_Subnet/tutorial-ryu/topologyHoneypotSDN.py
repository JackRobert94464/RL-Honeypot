# Access to mininet individual machines shell
# https://stackoverflow.com/questions/60364650/how-to-open-each-mininet-node-in-terminator/60420439#60420439

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.net import Mininet
from mininet.util import dumpNodeConnections, dumpNetConnections, dumpPorts
from mininet.log import setLogLevel
import pymongo
import os
import subprocess
import time
import socket
from mininet.cli import CLI
import threading
import json
import inspect




# MongoDB setup
def connect_to_mongo():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["network_topology"]
    collection = db["nodes"], db["switch"]
    return collection

# Extract topology from Mininet and insert into MongoDB
def extract_topology_to_mongo(net, collection):
  nodes_collection, switches_collection = collection
  topo_dict = {"nodes": [], "switch": []}

  for host in net.hosts:
    host_name = host.name
    if host.name.startswith('h4'):
      print(f"Skipping honeypot host {host.name} as it has no IP.")
      continue
    host_ip = host.IP()

    # Get the switch that the host is connected to (i.e., its subnet)
    for intf in host.intfList():
      if intf.link:
        switch = intf.link.intf1.node if intf.link.intf1.node != host else intf.link.intf2.node
        subnet_name = switch.name if isinstance(switch, OVSSwitch) else switch.name
        break

    # Placeholder for EPSS score (future functionality)
    epss_score = 0.5  # You can replace this later with the actual EPSS data

    # Determine connections to other nodes
    connections = []
    for intf in host.intfList():
      if intf.link:
        connected_node = intf.link.intf1.node if intf.link.intf1.node != host else intf.link.intf2.node
        if connected_node != host:
          connections.append({"connected_to": connected_node.name})

    # Determine blocked_from nodes
    blocked_from = []
    # Check if the connected node is blocked using iptables
    for node in net.hosts + net.switches:
      if node != host and node.intf() is not None:
        result = host.cmd(f'iptables -L OUTPUT -v -n | grep {node.IP()}')
        if 'DROP' in result or 'REJECT' in result:
          blocked_from.append(node.name)
        else:
          print(f"Node {host_name} is not blocked from {node.name}")

    topo_dict["nodes"].append({
      "node_name": host_name,
      "node_EPSS": epss_score,
      "node_ipv4": host_ip,
      "node_connections": connections,
      "node_subnet": subnet_name,
      "blocked_from": blocked_from
    })

  for switch in net.switches:
    switch_name = switch.name

    # Placeholder for EPSS score (future functionality)
    epss_score = 0.5  # You can replace this later with the actual EPSS data

    # Determine connections to other switches
    connections = []
    for intf in switch.intfList():
      if intf.link:
        connected_node = intf.link.intf1.node if intf.link.intf1.node != switch else intf.link.intf2.node
        if connected_node != switch and isinstance(connected_node, OVSSwitch):
          connections.append({"connected_to": connected_node.name})

    topo_dict["switch"].append({
      "switch_name": switch_name,
      "switch_EPSS": epss_score,
      "switch_connections": connections
    })

  # Insert the data into MongoDB
  nodes_collection.insert_many(topo_dict["nodes"])
  switches_collection.insert_many(topo_dict["switch"])
  print(f"Inserted topology into MongoDB: {topo_dict}")

def update_blocked_from_in_mongo(net):
    collection = connect_to_mongo()
    nodes_collection, _ = collection
    for host in net.hosts:
        blocked_from = []
        for node in net.hosts + net.switches:
            if node != host and node.intf() is not None:
                result = host.cmd(f'iptables -L OUTPUT -v -n | grep {node.IP()}')
                if 'DROP' in result or 'REJECT' in result:
                    blocked_from.append(node.name)
        nodes_collection.update_one(
            {"node_name": host.name},
            {"$set": {"blocked_from": blocked_from}}
        )
    print("Updated MongoDB with blocked_from information.")

# Placeholder function for CVE check (future integration)
def check_cves_for_host(host):
    # Trivy sugeested
    # In the future, use a CVE retrieval tool (like an open-source vulnerability scanner)
    # to retrieve and print CVEs for the given host.
    # Example: os.system(f"some_cve_tool {host.IP()}")
    print(f"Checking CVEs for host {host.name} with IP {host.IP()}...")
    cve_names = ["CVE-2021-12345", "CVE-2022-67890"]  # Example CVE list
    print(f"Found CVEs for {host.name}: {cve_names}")
    return cve_names
  


def deploy_honeypots(net, deployment_targets):
  for i, target_subnet in enumerate(deployment_targets):
    honeypot_host = net.get(f'h4{i+1}')  # h41, h42
    target_switch = net.get(f's{target_subnet}')  # s1, s2, etc.

    # Check if the honeypot already has an interface connected to the target switch
    existing_links = [link for link in net.links if honeypot_host in [link.intf1.node, link.intf2.node]]
    if any(target_switch in [link.intf1.node, link.intf2.node] for link in existing_links):
      print(f"Honeypot {honeypot_host.name} is already connected to subnet {target_switch.name}")
      continue

    # Add link between honeypot and target switch
    print(f"Deploying honeypot {honeypot_host.name} to subnet {target_switch.name}")
    net.addLink(honeypot_host, target_switch, cls=TCLink, bw=50, delay='30ms', loss=5)


# Honeypot server to return false information
def honeypot_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 8080))  # Bind to port 8080
        s.listen()
        print("Honeypot server started, waiting for connections...")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connection from {addr}")
                conn.sendall(b"Welcome to the admin console.\n")
                conn.sendall(b"Here's the sensitive data you were looking for...\n")
                conn.sendall(b"admin_password=12345\n")
                conn.close()

# Run this on honeypot hosts in Mininet
def start_honeypot_servers(net):
    honeypots = ['h41', 'h42']
    for honeypot in honeypots:
        host = net.get(honeypot)
        host.cmd('python3 -c "{}" &'.format(inspect.getsource(honeypot_server)))  # Start the server in the background



def manage_honeypot_visibility(net, compromised_hosts, honeypot_hosts):
    for host in net.hosts:
        if host.name in compromised_hosts or host.name in honeypot_hosts:  # Allow compromised hosts and honeypots
            host.cmd(f'iptables -A OUTPUT -d {host.IP()} -j ACCEPT')
        else:  # Block others from seeing honeypot
            host.cmd(f'iptables -A OUTPUT -d {host.IP()} -j DROP')

def listen_to_evaluator_and_deploy(net):
    evaluator_host = '127.0.0.1'
    evaluator_port = 10980

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((evaluator_host, evaluator_port))
        server_socket.listen(5)
        print(f"Listening for evaluator commands on {evaluator_host}:{evaluator_port}...")

        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                print(f"Connected by {addr}")
                data = client_socket.recv(1024)
                if not data:
                    break
                evaluator_data = json.loads(data.decode('utf-8'))

                deployment_targets = evaluator_data['deployment_targets']
                deploy_honeypots(net, deployment_targets)
                print(f"Deployment data: {evaluator_data}")

                # Manage honeypot visibility
                compromised_hosts = [host for host, compromised in zip(net.hosts, evaluator_data['network_state']) if compromised]
                honeypot_hosts = [net.get(f'h4{i+1}') for i in range(len(deployment_targets))]
                manage_honeypot_visibility(net, compromised_hosts, honeypot_hosts)

                # Update MongoDB with blocked_from information
                collection = connect_to_mongo()
                nodes_collection, _ = collection
                for host in net.hosts:
                    blocked_from = []
                    for node in net.hosts + net.switches:
                        if node != host and node.intf() is not None:
                            result = host.cmd(f'iptables -L OUTPUT -v -n | grep {node.IP()}')
                            if 'DROP' in result or 'REJECT' in result:
                                blocked_from.append(node.name)
                    nodes_collection.update_one(
                        {"node_name": host.name},
                        {"$set": {"blocked_from": blocked_from}}
                    )
                print("Updated MongoDB with blocked_from information.")


class TutorialTopology( Topo ):
  
    def build( self ):
        # add a host to the network
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        
        h3 = self.addHost( 'h3' )
        h4 = self.addHost( 'h4' )
        h5 = self.addHost( 'h5' )

        h6 = self.addHost( 'h6' )
        h7 = self.addHost( 'h7' )
        h8 = self.addHost( 'h8' )
        
        h9 = self.addHost( 'h9' )
        h10 = self.addHost( 'h10' )
        
        # add a switch to the network
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        
        # add a center switch that will forward to snort/ryu
        s111 = self.addSwitch( 's111' )
        
        # add a hacker host
        h1337 = self.addHost( 'h1337' )
        
        # add controller
        # c1 = RemoteController( 'c1', ip='127.0.0.1', port=6633 )
        c2 = RemoteController( 'c2', ip='127.0.0.1', port=6653 )
        
        # cmap = { 's1': c1, 's2': c1, 's3': c1, 's4': c1, 's111': c2 }
        cmap = { 's1': c2, 's2': c2, 's3': c2, 's4': c2, 's111': c2}
        
        
        # HONEYPOT FIELDS
        # add honeypot host
        h41 = self.addHost('h41', ip='10.0.0.41/24')
        h42 = self.addHost('h42', ip='10.0.0.42/24')

        # add a link between the host `h1-h5` and the `s1` switch
        self.addLink( h1, s1 )
        self.addLink( h2, s1 )
        
        self.addLink( h3, s2 )
        self.addLink( h4, s2 )
        self.addLink( h5, s2 )
        
        # add a link between the host `h6-h10` switch and the `s2` switch
        
        self.addLink( h6, s3 )
        self.addLink( h7, s3 )
        self.addLink( h8, s3 )
        
        self.addLink( h9, s4 )
        self.addLink( h10, s4 )
        
        # add a link between the `s1` switch and the `s2` switch
        # self.addLink( s1, s2 )
        self.addLink( s1, s111, cls=TCLink, bw=50, delay='30ms', loss=10)
        self.addLink( s2, s111, cls=TCLink, bw=50, delay='30ms', loss=10)
        self.addLink( s3, s111, cls=TCLink, bw=50, delay='30ms', loss=10)
        self.addLink( s4, s111, cls=TCLink, bw=50, delay='30ms', loss=10)
        
        # add a link between the `sr` switch and the `hatk` host
        self.addLink( s111, h1337, cls=TCLink, bw=50, delay='30ms', loss=10)
        
        # add bandwidth to the links
        # add a link between s1 and h1 with a max bandwidth of 100Mbps
        # self.addLink(h1, s1, cls=TCLink, bw=100)
        
        # add a link between s1 and h2 with a minimum delay of 75ms
        # self.addLink(h2, s1, cls=TCLink, delay='75ms')
        
        # add a link between s1 and h3 with 5% packet loss
        # self.addLink(h3, s1, cls=TCLink, loss=5)
        # the topologies accessible to the mn tool's `--topo` flag
        # note: if using the Dockerfile, this must be the same as in the Dockerfile
        # topos = { 'tutorialTopology': ( lambda: TutorialTopology() ) }



# Function to run a command in a screen session and log output
def run_command_in_screen(session_name, command):
    process = subprocess.Popen(
        ['screen', '-dmS', session_name, 'bash', '-c', f'source /path/to/venv/bin/activate && {command}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if stdout:
        print(f"{session_name} stdout: {stdout.decode()}")
    if stderr:
        print(f"{session_name} stderr: {stderr.decode()}")
    return process

# Check if port is up before moving on
def is_port_open(host, port):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    return result == 0

def initNetTopo(topo):
    "Create and test a simple network"
    # the topologies accessible to the mn tool's `--topo` flag
    # note: if using the Dockerfile, this must be the same as in the Dockerfile
    
    
    controller = RemoteController( 'c2', ip='127.0.0.1', port=6653 )
    net = Mininet(topo, controller=controller)
    net.start()
  
    # Get MongoDB collection
    collection = connect_to_mongo()

    # Extract topology information and insert into MongoDB
    extract_topology_to_mongo(net, collection)

    # Placeholder CVE check
    for host in net.hosts:
      if host.name.startswith('h4'):
        print(f"Skipping honeypot host {host.name} as it has no IP.")
        continue
      else:
        check_cves_for_host(host)

    print("Finished extracting topology and checking CVEs.")
    

    # Output to console
    # Get pid of all the hosts
    for host in net.hosts:
      print(host.name, host.pid)
    print(controller.name, controller.pid)


    print( "Dumping networks connections" )
    dumpNodeConnections(net.hosts)
    dumpNodeConnections(net.switches)
    dumpNetConnections(net)
    dumpPorts(net.switches)

    # print( "Testing network connectivity" )
    # net.pingAll()

    print("Starting Snort on all four subnets...")

    snort_commands = [
      "tmux new-session -d -s snort1 'sudo snort -i s111-eth1 -A unsock -l /tmp -v -c /etc/snort/rules/honeypotsdn.rules'",
      "tmux new-session -d -s snort2 'sudo snort -i s111-eth2 -A unsock -l /tmp -v -c /etc/snort/rules/honeypotsdn.rules'",
      "tmux new-session -d -s snort3 'sudo snort -i s111-eth3 -A unsock -l /tmp -v -c /etc/snort/rules/honeypotsdn.rules'",
      "tmux new-session -d -s snort4 'sudo snort -i s111-eth4 -A unsock -l /tmp -v -c /etc/snort/rules/honeypotsdn.rules'"
    ]

    for cmd in snort_commands:
      controller.cmd(cmd)

    # Check if Snort is running on each interface
    snort_interfaces = ["s111-eth1", "s111-eth2", "s111-eth3", "s111-eth4"]
    for intf in snort_interfaces:
      while True:
        result = controller.cmd(f"ps aux | grep 'snort -i {intf}' | grep -v grep")
        if result:
          print(f"Snort is running on {intf}")
          print("Please wait a few seconds for Snort to start...")
          time.sleep(15)
          break
        else:
          print(f"Waiting for Snort to start on {intf}...")
          time.sleep(5)

    print("Snort is running on all four subnets. 🐖🐖🐖🐖")
    
      
    # Running evaluation server on bare metal host in a screen session
    print("Start evaluation server on bare metal host with command:")
    print("python3 evaluator.py")
  
    print("Checking if evaluator at port 9800 is up...")
    while not is_port_open('127.0.0.1', 9800):
      print("Evaluator Server is not up yet. Waiting...")
      time.sleep(5)
    print("Evaluator Server 👤💻 is up. Proceeding...")

    # Running inference server on bare metal host in a screen session
    print("If there is a problem running the inference server, make sure to activate the virtual environment first.")
    # inference_process = subprocess.Popen(['screen', '-dmS', 'inference_server', 'python3', '../inference_v6_adaptive.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # time.sleep(20)
    print(f"Please start inference server on bare metal host manually 🧠.")
    print(f"python3 ../inference_v6_adaptive.py if you are inside tutorial-ryu.")
    
    print("Checking if evaluator at port 35025 is up...")
    while not is_port_open('127.0.0.1', 35025):
      print("Inference Server is not up yet. Waiting...")
      time.sleep(5)
    print("Inference Server 🧠 is up. Proceeding...")
    
    print("Use Ctrl+A+D to detach from the screen session.")

    # Init important service to indicate compromise on all nodes.
    for host in net.hosts:
      if not host.name.startswith('h4'):
        host.cmd('cd /home/ubuntu/RL-Honeypot-linux/Development/TrainingCode/A2C_Subnet/tutorial-ryu')
        host.cmd('python3 important_admin_database_server.py &')
    print("Finished initializing important healthcheck service. Hit port 15000 to imitate compromise. 🎯")
    
    
    # Start the evaluator listener in a separate thread
    listener_thread = threading.Thread(target=listen_to_evaluator_and_deploy, args=(net,))
    listener_thread.daemon = True
    listener_thread.start()
    print("Started evaluator listener thread. You can send command to net via port 10980 🎧")
    
    
    CLI(net)

    try:
      while True:
        pass
    except KeyboardInterrupt:
        # Drop the network_topology database from MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        client.drop_database("network_topology")
        print("Dropped network_topology database from MongoDB.")

        # Kill the screen sessions for evaluation and inference servers
        # subprocess.run(['screen', '-S', 'eval_server', '-X', 'quit'])
        # subprocess.run(['screen', '-S', 'inference_server', '-X', 'quit'])
        # print("Terminated evaluation and inference servers.")

        # Terminate ryu-manager controller
        # subprocess.run(['sudo', 'mn', '-c'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Terminated ryu-manager controller. 🐲⚔️")
        print("Exiting...")

        net.stop()

if __name__ == '__main__':
    # Start ryu-manager controller in a screen session
    print("Start ryu-manager controller to control the switch first.")
    
    print("Run the following command:")
    print("sudo ryu-manager --ofp-tcp-listen-port 6653 ./controller_switch_snort.py")
    
    print("Checking if ryu-manager at port 6653 is up...")
    while not is_port_open('127.0.0.1', 6653):
      print("ryu-manager is not up yet. Waiting...")
      time.sleep(5)
    
    print(f"Successfully started ryu-manager controller to control the switch 🐲.")

    topo = TutorialTopology()

    # Tell mininet to print useful information
    setLogLevel('info')
    initNetTopo(topo)
    


