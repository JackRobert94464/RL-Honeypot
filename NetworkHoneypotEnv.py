import gym
from gym import spaces
import numpy as np

N = 10
M = 3  # Number of deception nodes (m)
K = N - M  # Number of normal nodes (k)
P = 0.8
Q = 0.2

class NetworkHoneypotEnv(gym.Env):  # Inherit from gym.Env
    def __init__(self):
        super(NetworkHoneypotEnv, self).__init__()
        self.state_space = spaces.MultiBinary(N)
        self.action_space = spaces.MultiBinary(M)
        self.state = self.reset()
        self.secret_node = np.random.randint(N)

    def reset(self):
        attacker_node = np.random.randint(N)
        state = np.zeros(N, dtype=int)  # Corrected line
        state[attacker_node] = 1
        return state

    def step(self, action):
        assert len(action) == M, "Invalid action shape"
        reward = 0
        done = False
        attacker_node = np.argmax(self.state == 1)

        self.state[:M] = action  # Deploy deception nodes

        next_attacker_node, current_attacker_node = self._get_next_attacker_node(attacker_node)

        if next_attacker_node == self.secret_node:
            self.state[attacker_node] = 0
            self.state[next_attacker_node] = 1
            reward = -10
            done = True
        elif next_attacker_node != attacker_node:
            self.state[attacker_node] = 0
            self.state[next_attacker_node] = 1
            if self.state[next_attacker_node] == 0:
                reward = -1
            elif self.state[next_attacker_node] == 2:
                reward = 1

        return self.state, reward, done, {}

    def _get_next_attacker_node(self, attacker_node):
        neighbors = [attacker_node - 1, attacker_node + 1]
        neighbors = [n % N for n in neighbors]
        next_node = np.random.choice(neighbors, p=[0.5, 0.5])
        next_node = np.random.choice([attacker_node, next_node], p=[1 - P, P])

        if np.random.random() < Q:
            next_node = np.random.randint(N)
        return next_node, attacker_node

