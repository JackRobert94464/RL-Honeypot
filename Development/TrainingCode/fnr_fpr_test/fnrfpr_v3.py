import numpy as np

# Given rates
fn_rate = 0.04
fp_rate = 0.004
tp_rate = 0.76
tn_rate = 0.196

# Attack rates
attack_rate = 0.1 # = epss score
non_attack_rate = 0.9 # = 1 - epss score

# Input array
input_array = np.array([0, 0, 1, 0, 0, 1, 0])

# Create a function to simulate the error
def simulate_error(value):
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

for i in range(50):

    # Apply the simulation to the input array
    output_array = np.array([simulate_error(value) for value in input_array])

    print("Input array:", input_array)
    print("Output array with simulated errors:", output_array)