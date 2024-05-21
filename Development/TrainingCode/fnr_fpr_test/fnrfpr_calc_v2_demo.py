import numpy as np
import random
import os


def simulate_error_v2(true_state, alerted_state, fn_rate, fp_rate):
    if alerted_state == 0:
        
        print("here, alerted_state is 0 mean no alert has been raised yet")
        
        # If the alert has not been raised yet
        if true_state == 0:
            # If the true state is 0 (not compromised)
            # There is a chance of generating a false positive
            if random.random() < fp_rate:
                
                print("Chance of generating a false positive hit, sounding alert on this node")
                
                return 1
            else:
                
                print("No false positive hit, no alert on this node")
                
                return 0
        else:
            # If the true state is 1 (compromised)
            # There is a chance of not detecting it (false negative)
            if random.random() < fn_rate:
                
                print("Chance of generating a false negative hit, no alert on this node")
                
                return 0
            else:
                
                print("No false negative hit, sounding alert on this node")
                
                return 1
    else:
        # If the alert has already been raised (alerted_state = 1)
        # It will never go back to 0, regardless of the true state
        
        print("Alert has already been raised on this node, no change in alert status")
        
        return 1


def simulate_alert_training(true_state, previous_alerted_state, fnr, fpr):
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
    
    alerted_nodes = previous_alerted_state  # Initialize alerted_nodes with previous_alerted_state

    for index in range(len(true_state)):
        
        print("Working on index:", index)

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
        
        alerted_nodes[index] = simulate_error_v2(true_state[index], alerted_nodes[index], fn_rate, fp_rate)
        
        os.system("pause")


    alerted_nodes = np.array(alerted_nodes)

    return alerted_nodes



'''
# Example usage
true_state = [0, 0, 1, 1, 0, 1]
alerted_state = [0, 1, 0, 0, 0, 1]
fnr = 0.3  # Example False Negative Rate
fpr = 0.2  # Example False Positive Rate

modified_state = simulate_alert_training(true_state, alerted_state, fnr, fpr)
print("True State:    ", np.array(true_state))
print("Modified State:", modified_state)
'''




