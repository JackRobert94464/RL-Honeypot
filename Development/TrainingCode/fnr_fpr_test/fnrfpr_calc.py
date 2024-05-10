import random
import numpy as np

# Create a function to simulate the error
# This one is more accurate
def simulate_error_v1(value, fn_rate, fp_rate, tp_rate, tn_rate):
    if value == 0:
        # For true negatives
        tn_prob = tn_rate / (tn_rate + fp_rate)
        fp_prob = fp_rate / (tn_rate + fp_rate)
        return np.random.choice([0, 1], p=[tn_prob, fp_prob])
    else:
        # For true positives
        tp_prob = tp_rate / (tp_rate + fn_rate)
        fn_prob = fn_rate / (tp_rate + fn_rate)
        return np.random.choice([1, 0], p=[tp_prob, fn_prob])
    



'''
next_node = random.choices(
                population=pop, # the list to pick stuff out from in this case the ip of the next possible nodes
                weights=wei, # AVG OF BOTH ROOT AND USER
                k=1 # number of sample to pick from population
            )[0]
'''



def simulate_error_v2(value, fn_rate, fp_rate, tp_rate, tn_rate):
    return random.choices(population=[0, 1], weights=[tn_rate + fp_rate, fn_rate + tp_rate], k=1)[0]


def simulate_alert_training(true_state, fnr, fpr):
    """
    Simulates alerts raised during training on nodes by introducing False Negative and False Positive Rates.

    Args:
        true_state: A binary list representing the true state of nodes (attacked nodes = 1, healthy = 0).
        fnr: Float value between 0 and 1 representing False Negative Rate.
        fpr: Float value between 0 and 1 representing False Positive Rate.
        epss_score: A list of float values between 0 and 1 representing the Exploit Prediction Scoring System (EPSS) scores.

    Returns:
        A binary list representing nodes with raised alerts.
    """
    
    attacked_nodes = true_state
    alerted_nodes = []

    index = 0

    for value in attacked_nodes:

        # attack_rate = epss_score[index]
        # non_attack_rate = 1 - epss_score[index]

        # 10/5/2024 - Attack rate is a static probability of whether the attacker "will" attack or not
        # EPSS is the probability that a vulnerability will be exploited

        attack_rate = 0.7
        non_attack_rate = 1 - attack_rate

        # FN, FP, TP, TN rates
        fn_rate = fnr * attack_rate
        fp_rate = fpr * non_attack_rate
        tp_rate = (1 - fnr) * attack_rate
        tn_rate = (1 - fpr) * non_attack_rate

        # alerted_nodes.append(simulate_error(value, fn_rate, fp_rate, tp_rate, tn_rate))
        alerted_nodes.append(simulate_error_v2(value, fn_rate, fp_rate, tp_rate, tn_rate))

        index += 1

    alerted_nodes = np.array(alerted_nodes)

    return alerted_nodes


'''

'''

# Example usage
# Input array
input_array = np.array([0, 0, 1, 0, 0, 1, 0])

print("Input array:", input_array)
print("Output array with simulated errors:", simulate_alert_training(input_array, 0.05, 0.02))