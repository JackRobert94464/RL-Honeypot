import random

def simulate_errors(state, fnr, fpr):
  """
  Simulates False Negative and False Positive Rates on a binary observation state.

  Args:
      state: A binary list representing the observed state (attacked nodes = 1, healthy = 0).
      fnr: Float value between 0 and 1 representing False Negative Rate.
      fpr: Float value between 0 and 1 representing False Positive Rate.

  Returns:
      A modified binary list with simulated errors based on FNR and FPR.
  """
  modified_state = state.copy()
  
  # False Negatives (Missed Attacks)
  for i in range(len(modified_state)):
    if modified_state[i] == 1 and random.random() < fnr:
      modified_state[i] = 0  # Change attacked node to healthy

  # False Positives (Identified Healthy Nodes as Attacked)
  for i in range(len(modified_state)):
    if modified_state[i] == 0 and random.random() < fpr:
      modified_state[i] = 1  # Change healthy node to attacked

  return modified_state

# Example usage
state = [0, 1, 0, 0, 0, 1]
fnr = 0.2  # False Negative Rate of 10%
fpr = 0.15 # False Positive Rate of 5%
modified_state = simulate_errors(state, fnr, fpr)

print(f"Original State: {state}")
print(f"Modified State (FNR: {fnr}, FPR: {fpr}): {modified_state}")
