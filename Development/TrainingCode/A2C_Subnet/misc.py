import pandas as pd
from math import factorial
import random
import os
import tensorflow as tf

    
def create_dictionary_ntpg(filename):
    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(filename)

    # Create an empty dictionary
    ntpg = {}

    # Iterate through each row in the dataframe
    for index, row in df.iterrows():
        source = row["source"]
        target = row["target"]
        user_prob = row["user_prob"]
        root_prob = row["root_prob"]
    
        # If the source is not already a key in the dictionary, add it as a key with an empty list as the value
        if source not in ntpg:
            ntpg[source] = []
        
        # Append a tuple containing the target, user_prob, and root_prob to the list associated with the source key
        ntpg[source].append((target, user_prob, root_prob))

        # Print the dictionary
        # print(ntpg)

    return ntpg

def create_dictionary_htpg(filename):
    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(filename)

    # Create an empty dictionary
    htpg = {}

    # Define a function to process each row
    def process_row(row):
        source = row["source"]
        service = row["service"]
        cve = row["cve"]
        exploit_prob = float(row["exploit_prob"])  # Convert exploit_prob to float
        target = row["target"]
        privilege = row["privilege"]
        return (service, cve, exploit_prob, (target, privilege))

    # Iterate through each row in the dataframe
    for index, row in df.iterrows():
        source = row["source"]
        
        # Process the row using the defined function
        service, cve, exploit_prob, target_info = process_row(row)
        
        # If the source is not already a key in the dictionary, add it as a key with an empty list as the value
        if source not in htpg:
            htpg[source] = []
        
        # Append a tuple containing the service, cve, exploit_prob, and target_info to the list associated with the source key
        htpg[source].append((service, cve, exploit_prob, target_info))

    # Print the dictionary
    # print(htpg)

    return htpg

def get_deception_nodes():
    num_deception_nodes = int(input("How many deception nodes available for deployment? "))
    return num_deception_nodes

def count_nodes(ntpg):
    num_nodes = len(ntpg.keys())
    return num_nodes

def random_deception_amount(ntpg):
    num_nodes = len(ntpg.keys())
    deception_amount = random.randint(1, num_nodes)
    return deception_amount

def calculate_first_parameter(num_deception_nodes, num_nodes):
        first_parameter = num_deception_nodes + num_nodes
        return first_parameter

# matrix stuff
# actually permutation without repetition
# P(n,r) = n! / (n-r)!
# with n as normal nodes and r as deception nodes
# WARNING ABOVE IS LOGIC FAULT
# 06/04/2024
# đặt 2 fake resource vào 7 node -> cần chọn 2 trong 7 node để đặt -> tính tổ hợp chập 2 của 7: C(7,2) = 21
# => Tinh to hop C(K,M) = k!/((k-m)!*m!) = 7!/(5!*2!) = 21

# self.actionDimension = factorial(env.K) / (factorial(env.K - env.M) * factorial(env.M))

def calculate_permutation(s1, s2):
    return factorial(s1) / (factorial(abs(s1-s2)) * factorial(s2))

# create_dict = Miscellaneous()
# create_dict.create_dictionary()
# create_dict.create_dictionary_htpg()


def load_tpg_data(ntpg_dir, htpg_dir):
    if os.name == 'nt':
        ntpg_path = f"{ntpg_dir}"
        htpg_path = f"{htpg_dir}"
    else:
        ntpg_path = f"{ntpg_dir}"
        htpg_path = f"{htpg_dir}"
    ntpg = create_dictionary_ntpg(ntpg_path)
    htpg = create_dictionary_htpg(htpg_path)
    return ntpg, htpg

def load_ntpg_data(ntpg_dir):
    if os.name == 'nt':
        ntpg_path = f"{ntpg_dir}"
    else:
        ntpg_path = f"{ntpg_dir}"
    ntpg = create_dictionary_ntpg(ntpg_path)
    return ntpg

from NetworkHoneypotEnv_AdaptiveTraining_AC import NetworkHoneypotEnv
from pymongo import MongoClient

def create_environment_from_baseEnv(ntpg, deception_nodes_amount, fnr, fpr, attack_rate, nicr_nodes):
    normal_nodes = count_nodes(ntpg)
    first_parameter = calculate_first_parameter(deception_nodes_amount, normal_nodes)
    total_permutations = calculate_permutation(normal_nodes, deception_nodes_amount)
    inference_env = NetworkHoneypotEnv(first_parameter, deception_nodes_amount, normal_nodes, ntpg, fnr, fpr, attack_rate, [nicr_nodes])
    return inference_env

def load_trained_model(model_path, loss_fn):
    trained_model = tf.keras.models.load_model(model_path, custom_objects={'loss': loss_fn})
    return trained_model

def ntpg_to_epss_matrix(ntpg):
    """
    Converts a Node Threat Penetration Graph (_ntpg) dictionary to a K*K epss matrix.

    Args:
        ntpg: A dictionary representing the Node Threat Penetration Graph.

    Returns:
        A K*K numpy matrix representing the epss scores between nodes.
    """
    nodes = list(ntpg.keys())
    K = len(nodes)
    epss_matrix = [[0 for _ in range(K)] for _ in range(K)]

    for i, node_i in enumerate(nodes):
        for neighbor, epss, _ in ntpg[node_i]:
            j = nodes.index(neighbor)
            avg_epss = epss
            epss_matrix[i][j] = avg_epss

    # Fill the lower triangle (symmetric matrix)
    for i in range(K):
        for j in range(i + 1, K):
            epss_matrix[j][i] = epss_matrix[i][j]

    return epss_matrix

def ntpg_to_connection_matrix(ntpg):
    """
    Converts a Node Threat Penetration Graph (_ntpg) dictionary to a K*K connection matrix.

    Args:
        ntpg: A dictionary representing the Node Threat Penetration Graph.

    Returns:
        A K*K numpy matrix representing the connections between nodes (1 for connection, 0 for no connection).
    """
    nodes = list(ntpg.keys())
    K = len(nodes)
    connection_matrix = [[0 for _ in range(K)] for _ in range(K)]

    for node_i, neighbors in ntpg.items():
        i = nodes.index(node_i)
        for neighbor, _, _ in neighbors:
            j = nodes.index(neighbor)
            connection_matrix[i][j] = 1  # Mark connection (one-way)

    return connection_matrix

def load_data_from_mongoDB():
    client = MongoClient('mongodb://localhost:27017/')
    db = client["network_topology"]
    collection = db["nodes"], db["switch"]
    
    data = collection.find_one()  # Assuming you want to load one document

    ntpg = {}
    nodes = data['nodes']
    switches = data['switch']

    # Create a mapping of switch names to their connections
    switch_connections = {switch['switch_name']: switch['switch_connections'] for switch in switches}

    for node in nodes:
        node_name = node['node_name']
        node_epss = node['node_EPSS']
        node_subnet = node['node_subnet']
        node_connections = node['node_connections']
        
        if node_name not in ntpg:
            ntpg[node_name] = []

        for connection in node_connections:
            connected_to = connection['connected_to']
            connected_switch = next((sw for sw in switches if sw['switch_name'] == connected_to), None)
            if connected_switch:
                for sw_connection in connected_switch['switch_connections']:
                    connected_node = next((n for n in nodes if n['node_subnet'] == sw_connection['connected_to']), None)
                    if connected_node:
                        ntpg[node_name].append((connected_node['node_name'], node_epss, connected_node['node_subnet']))

    return ntpg

from collections import defaultdict
from bson import ObjectId

def load_data_from_mongo_test01(mongoIP, mongoPort):
    
    client = MongoClient(f'mongodb://{mongoIP}:{mongoPort}/')
    db = client["network_topology"]
    collection_nodes = db["nodes"]
    collection_switches = db["switch"]
    
    # Retrieve all data from MongoDB
    nodes_data = list(collection_nodes.find())
    switches_data = list(collection_switches.find())
    
    # Combine the data into a single dictionary
    mongo_data = {
        'nodes': nodes_data,
        'switch': switches_data
    }
    
    # Initialize the NTPG dictionary
    ntpg = defaultdict(list)

    # Create a lookup for switches and their connections
    switch_connections = {}
    for switch in mongo_data['switch']:
        switch_name = switch['switch_name']
        switch_connections[switch_name] = [conn['connected_to'] for conn in switch['switch_connections']]

    # Create a lookup for nodes by their connected switch
    nodes_by_switch = defaultdict(list)
    node_data = mongo_data['nodes']

    for node in node_data:
        nodes_by_switch[node['node_subnet']].append(node)

    # Traverse through nodes and determine connectivity
    for node in node_data:
        node_name = node['node_name']
        current_switch = node['node_subnet']

        # Gather all nodes connected within the current switch
        connected_switches = switch_connections.get(current_switch, [])
        directly_connected_nodes = nodes_by_switch[current_switch]

        # Nodes connected to other switches, if switches are interconnected
        for connected_switch in connected_switches:
            directly_connected_nodes += nodes_by_switch.get(connected_switch, [])

        for connected_node in directly_connected_nodes:
            # Avoid self-loop and only add if the node isn't blocked from accessing the other node
            if connected_node['node_name'] != node_name and node_name not in connected_node['blocked_from']:
                # Add to NTPG: (connected_node_name, EPSS, subnet)
                ntpg[node_name].append(
                    (connected_node['node_name'], (node['node_EPSS'] + connected_node['node_EPSS']) / 2, connected_node['node_subnet'])
                )

    return dict(ntpg)