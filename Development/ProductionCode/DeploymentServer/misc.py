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
    return factorial(s1) / (factorial(s1-s2) * factorial(s2))

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

from NetworkHoneypotEnv_base_fnrfprtest_v3 import NetworkHoneypotEnv

def create_environment_from_baseEnv(ntpg, htpg, deception_nodes_amount, fnr, fpr, attack_rate):
    normal_nodes = count_nodes(ntpg)
    first_parameter = calculate_first_parameter(deception_nodes_amount, normal_nodes)
    total_permutations = calculate_permutation(normal_nodes, deception_nodes_amount)
    inference_env = NetworkHoneypotEnv(first_parameter, deception_nodes_amount, normal_nodes, ntpg, htpg, fnr, fpr, attack_rate)
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
        for neighbor, user_epss, root_epss in ntpg[node_i]:
            j = nodes.index(neighbor)
            # Average the user_epss and root_epss values
            avg_epss = (user_epss + root_epss) / 2
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