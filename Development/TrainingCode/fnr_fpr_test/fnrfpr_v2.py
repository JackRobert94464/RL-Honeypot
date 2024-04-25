import random
import numpy as np

def simulate_alert_training(true_state, fnr, fpr):
    """
    Simulates alerts raised during training on nodes by introducing False Negative and False Positive Rates.

    Args:
        true_state: A binary list representing the true state of nodes (attacked nodes = 1, healthy = 0).
        fnr: Float value between 0 and 1 representing False Negative Rate.
        fpr: Float value between 0 and 1 representing False Positive Rate.

    Returns:
        A binary list representing nodes with raised alerts.
    """
    attacked_nodes = true_state
    alerted_nodes = [0] * len(attacked_nodes)

    # Simulate alerts based on attacked nodes and false negatives
    for i in range(len(attacked_nodes)):
        if attacked_nodes[i] == 1 and random.random() >= fnr:
            alerted_nodes[i] = 1  # True Positive
        elif attacked_nodes[i] == 0 and random.random() < fpr:
            alerted_nodes[i] = 1  # False Positive

    return alerted_nodes

def simulate_attacks_and_alerts(num_nodes, attack_probability, alert_probability, fnr, fpr):
    """
    Simulates attacks and alerts on nodes, including false negatives and positives.

    Args:
        num_nodes: Total number of nodes.
        attack_probability: Probability of a node being attacked.
        alert_probability: Probability of an alert being raised.
        fnr: False Negative Rate.
        fpr: False Positive Rate.

    Returns:
        A tuple containing binary lists representing attacked nodes and raised alerts.
    """
    attacked_nodes = [1 if random.random() < attack_probability else 0 for _ in range(num_nodes)]
    alerted_nodes = [0] * num_nodes

    # Simulate alerts based on attacked nodes and false negatives
    for i in range(num_nodes):
        if attacked_nodes[i] == 1 and random.random() >= fnr:
            alerted_nodes[i] = 1  # True Positive
        elif attacked_nodes[i] == 0 and random.random() < fpr:
            alerted_nodes[i] = 1  # False Positive

    return attacked_nodes, alerted_nodes

def place_honeypots(alerted_nodes, num_honeypots):
    """
    Places honeypots based on alerted nodes.

    Args:
        alerted_nodes: A binary list representing nodes with raised alerts.
        num_honeypots: Number of honeypots to be placed.

    Returns:
        A binary list representing the placement of honeypots.
    """
    # Your machine learning model comes here to decide where to place the honeypots based on alerted nodes
    # For simplicity, we're placing them randomly here
    honeypot_positions = random.sample([i for i, x in enumerate(alerted_nodes) if x == 1], num_honeypots)
    honeypots = [1 if i in honeypot_positions else 0 for i in range(len(alerted_nodes))]

    return honeypots

# Example usage
'''
num_nodes = 10
attack_probability = 0.3  # Probability of a node being attacked
alert_probability = 0.2   # Probability of an alert being raised
fnr = 0.1                 # False Negative Rate
fpr = 0.05                # False Positive Rate
num_honeypots = 2         # Number of honeypots to be placed

attacked_nodes, alerted_nodes = simulate_attacks_and_alerts(num_nodes, attack_probability, alert_probability, fnr, fpr)
honeypots = place_honeypots(alerted_nodes, num_honeypots)

print(f"Attacked Nodes: {attacked_nodes}")
print(f"Alerted Nodes: {alerted_nodes}")
print(f"Honeypots Placement: {honeypots}")
'''

