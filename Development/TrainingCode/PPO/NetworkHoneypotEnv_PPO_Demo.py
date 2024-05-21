import tensorflow as tf
import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
import gym
from gym import spaces
import itertools
import random

class NetworkHoneypotEnv(gym.Env):

    def __init__(self, N, M, K, ntpg, htpg):
        super(NetworkHoneypotEnv, self).__init__()
        self.N = N
        self.M = M
        self.K = K
        self.nicr_nodes = [5]
        self.nifr_nodes = []
        my_list = list(range(1, K+1))
        combinations = list(itertools.combinations(my_list, M))
        self._action_space = dict(enumerate(combinations))
        self.action_space = spaces.Discrete(len(combinations))
        self.observation_space = spaces.Box(low=0, high=1, shape=(K,), dtype=np.int32)
        self._state = np.zeros(self.K, dtype=np.int32)
        self.current_step = 0
        self.maxSteps = 50
        self._ntpg = ntpg
        self._htpg = htpg
        self._episode_ended = False
        self._current_attacker_node = list(ntpg.keys())[2]

    def reset(self):
        self.current_step = 0
        self.nicr_nodes = [5]
        self.nifr_nodes = []
        self._state = np.zeros(self.K, dtype=np.int32)
        self._episode_ended = False
        self._current_attacker_node = list(self._ntpg.keys())[2]
        return self._state

    def __is_action_valid(self, action):
        if isinstance(action, (list, np.ndarray)):
            action = tuple(sorted(action)) if action.ndim > 1 else (action[0],)
        sorted_action_space = {k: tuple(sorted(v)) for k, v in self._action_space.items()}
        if action not in sorted_action_space.values():
            return False
        return len(action) == self.M

    def __attacker_move_step(self):
        current_node = self._current_attacker_node
        current_node_index = list(self._ntpg.keys()).index(current_node)
        if self._ntpg.get(current_node):
            self._state[current_node_index] = 1
            pop = [route[0] for route in self._ntpg.get(current_node)]
            wei = [(route[1] + route[2]) / 2 for route in self._ntpg.get(current_node)]
            next_node = random.choices(
                population=pop,
                weights=wei,
                k=1
            )[0]
            print(f"Attacker moving from node {current_node} to node {next_node}")
            self._current_attacker_node = next_node
        else:
            print(f"No valid routes from node {current_node}")

    def __update_nifr_nodes(self, action):
        self.nifr_nodes = list(action)
        print(f"NIFR nodes: {self.nifr_nodes}")

    def __is_nicr_attacked(self, nicr_nodes):
        for i in nicr_nodes:
            if i < len(self._state) and self._state[i] == 1:
                self._episode_ended = True
                return True
        return False

    def __is_nifr_attacked(self, nifr_nodes):
        for i in nifr_nodes:
            if i < len(self._state) and self._state[i] == 1:
                self._episode_ended = True
                return True
        return False

    def step(self, action):
        if self._episode_ended:
            return self.reset(), 0, False, {}

        if self.current_step >= self.maxSteps:
            reward = -1
            self._episode_ended = True
            return self._state, reward, True, {}

        # Update the state based on the attacker's move
        self.__attacker_move_step()

        # Check if NICR nodes are attacked
        if self.__is_nicr_attacked(self.nicr_nodes):
            reward = -1
            self._episode_ended = True
            return self._state, reward, True, {}

        # Update NIFR nodes and check if they are attacked
        self.__update_nifr_nodes(self._action_space[action])
        if self.__is_nifr_attacked(self.nifr_nodes):
            reward = 1
            self._episode_ended = True
            return self._state, reward, True, {}

        # Continue with other steps
        self.current_step += 1
        reward = -0.1
        return self._state, reward, False, {}


'''

'''
# Example usage

import os
import misc

if os.name == 'nt':  # If the operating system is Windows
        ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg.csv")
        htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg.csv")
else:  # For other operating systems like Linux
        ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg.csv")
        htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg.csv")

env = NetworkHoneypotEnv(N=5, M=3, K=10, ntpg=ntpg, htpg=htpg)
obs = env.reset()
print(f"Initial Observation: {obs}")

action = env.action_space.sample()
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")
obs, reward, done, info = env.step(action)
print(f"Next Observation: {obs}, Reward: {reward}, Done: {done}")