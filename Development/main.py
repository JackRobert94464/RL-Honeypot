# Import tensorflow and numpy libraries
import tensorflow as tf
import numpy as np

# Define some constants
NUM_STATES = 10 # The number of states in the environment
NUM_ACTIONS = 4 # The number of actions in the environment
GAMMA = 0.9 # The discount factor for future rewards
ALPHA = 0.1 # The learning rate for Q-learning
EPSILON = 0.1 # The exploration rate for epsilon-greedy policy
MAX_ITER = 1000 # The maximum number of iterations for the algorithm

# Create a random target network TPN with 3 layers
TPN = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(1,)), # Change the input shape to (1,)
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(NUM_ACTIONS, activation='linear')
])

# Create a random deployment action graph DAG with NUM_STATES nodes and NUM_ACTIONS edges per node
DAG = np.random.randint(0, 2, size=(NUM_STATES, NUM_ACTIONS))

# Initialize the Q-table with zeros
Q = np.zeros((NUM_STATES, NUM_ACTIONS))

# Define a function to choose an action using epsilon-greedy policy
def choose_action(state):
    if np.random.rand() < EPSILON: # Explore with probability EPSILON
        return np.random.randint(NUM_ACTIONS) # Choose a random action
    else: # Exploit with probability 1 - EPSILON
        return np.argmax(Q[state]) # Choose the action with the highest Q-value

def get_reward(state, action):
  """Gets the reward for taking an action in a state.

  Args:
    state: The current state.
    action: The action to take.

  Returns:
    The reward for taking the action in the current state.
  """

  if state is None:
    return 0.0
  else:
    state_tensor = tf.convert_to_tensor([state])
    state_tensor = tf.expand_dims(state_tensor, axis=0)
    action_tensor = tf.convert_to_tensor([action])
    output_tensor = TPN(state_tensor)
    reward = output_tensor[0][action]
    return reward.numpy()


def get_next_state(state, action):
  """Gets the next state for taking an action in a state.

  Args:
    state: The current state.
    action: The action to take.

  Returns:
    The next state for taking the action in the current state.
  """

  if state is None:
    return None
  elif state >= len(DAG):
    return None
  elif np.any(DAG[state][action]):
    next_state = np.nonzero(DAG[state][action])[0][0]
    return next_state
  else:
    return None


# Initialize the target_policy variable as an empty list
target_policy = []

# Run the algorithm for MAX_ITER iterations
for i in range(MAX_ITER):
    # Choose a random initial state
    state = np.random.randint(NUM_STATES)
    
    # Repeat until reaching a terminal state (a state with no actions)
    while np.sum(DAG[state]) > 0:
        # Choose an action using epsilon-greedy policy
        action = choose_action(state)
        
        # Get the reward and the next state for taking the action in the current state
        reward = get_reward(state, action)
        next_state = get_next_state(state, action)
        
        # Update the Q-table using the Bellman equation
        if next_state is not None:
            Q[state][action] = Q[state][action] + ALPHA * (reward + GAMMA * np.max(Q[next_state]) - Q[state][action])
        else:
            Q[state][action] = 0.0
        
        # Update the target policy by appending the action with the highest Q-value for each state
        target_policy.append(np.argmax(Q[state]))
        
        # Set the current state to be the next state
        state = next_state
    
    # Print some progress information every 100 iterations
    if (i + 1) % 100 == 0:
        print(f"Iteration {i + 1}: Q-table = {Q}, target policy = {target_policy}")
