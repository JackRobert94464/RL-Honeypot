import gym
from gym import spaces
import numpy as np

# Define some constants
N = 10 # Number of nodes on the DMZ machine
P = 0.8 # Probability of attacker moving to a neighboring node
Q = 0.2 # Probability of attacker attacking a node

class NetworkHoneypotEnv(gym.Env):
    """A custom environment for the network honeypot problem"""
    def __init__(self):
        super(NetworkHoneypotEnv, self).__init__()
        # Define the state space as a vector of N values
        # 0 means normal node, 1 means secret resource node,
        # 2 means deception node, 3 means occupied by attacker
        self.state_space = spaces.Box(low=0, high=3, shape=(N,), dtype=np.int)
        # Define the action space as a vector of N values
        # 0 means do nothing, 1 means create deception node on that node
        self.action_space = spaces.Box(low=0, high=1, shape=(N,), dtype=np.int)
        # Initialize the state randomly
        self.state = self.reset()
        # Choose a random node as secret resource node
        self.secret_node = np.random.randint(N)

    def reset(self):
        """Reset the state to a random initial state"""
        # Choose a random node as occupied by attacker
        attacker_node = np.random.randint(N)
        # Initialize all nodes as normal nodes except attacker node
        state = np.zeros(N, dtype=np.int)
        state[attacker_node] = 3
        return state

    def step(self, action):
        """Take an action and return the next state, reward, done and info"""
        assert self.action_space.contains(action), "Invalid action"
        # Initialize reward and done flag
        reward = 0
        done = False
        # Get the current attacker node
        attacker_node = np.argmax(self.state == 3)
        # Apply the agent's action
        if action[attacker_node] == 1:
            # If the agent creates deception node on attacker node,
            # update the state and reward accordingly
            self.state[attacker_node] = 2
            reward = 1
        else:
            # If the agent does not create deception node on attacker node,
            # update the state based on attacker's behavior
            next_attacker_node = self._get_next_attacker_node(attacker_node)
            if next_attacker_node == self.secret_node:
                # If the attacker moves to or attacks secret resource node,
                # update the state and reward accordingly and end episode
                self.state[attacker_node] = 0
                self.state[next_attacker_node] = 3
                reward = -10
                done = True
            elif next_attacker_node != attacker_node:
                # If the attacker moves to or attacks a different node,
                # update the state and reward accordingly
                self.state[attacker_node] = 0
                self.state[next_attacker_node] = 3
                if self.state[next_attacker_node] == 0:
                    # If the attacker moves to or attacks a normal node,
                    # reward is -1
                    reward = -1
                elif self.state[next_attacker_node] == 2:
                    # If the attacker moves to or attacks a deception node,
                    # reward is +1
                    reward = 1
        
        # Return the next state, reward, done flag and additional info
        return self.state, reward, done, {}

    def _get_next_attacker_node(self, attacker_node):
        """Get the next node that the attacker will move to or attack"""
        # Get the neighboring nodes of the attacker node
        neighbors = [attacker_node - 1, attacker_node + 1]
        # Wrap around the boundaries
        neighbors = [n % N for n in neighbors]
        # Choose a random neighboring node with probability P
        next_node = np.random.choice(neighbors, p=[P/2, P/2])
        # Choose the same node with probability 1 - P
        next_node = np.random.choice([attacker_node, next_node], p=[1 - P, P])
        # Simulate a random attack with probability Q
        if np.random.random() < Q:
            # Choose a random node to attack
            next_node = np.random.randint(N)
        return next_node
