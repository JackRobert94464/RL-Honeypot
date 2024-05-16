import tensorflow as tf
import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
import random
import itertools

class NetworkHoneypotEnv(py_environment.PyEnvironment):

    def __init__(self, N, M, K, ntpg, htpg):
        self.N = N
        self.M = M
        self.K = K
        self.nicr_nodes = [5]
        self.nifr_nodes = []

        my_list = list(range(1, K+1))
        combinations = list(itertools.combinations(my_list, M))
        self._action_space = dict(enumerate(combinations))

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(1, M), dtype=np.int32, minimum=1, maximum=K, name='action')

        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(1,K), dtype=np.int32, minimum=0, maximum=1, name='observation')

        self._reward_spec = array_spec.BoundedArraySpec(
            shape=(1,K), dtype=np.int32, minimum=-1, maximum=1, name='reward')

        self._state = np.zeros(self.K, dtype=np.int32)

        self.current_step = 0
        self.maxSteps = 50

        self._ntpg = ntpg
        self._htpg = htpg

        self._episode_ended = False

        self._current_attacker_node = list(ntpg.keys())[2]

    def action_spec(self):
        return self._action_spec
    
    def action_space(self):
        return self._action_space
    
    def observation_spec(self):
        return self._observation_spec
    
    def get_ntpg(self):
        return self._ntpg
    
    def get_htpg(self):
        return self._htpg

    def _reset(self):
        self.current_step = 0
        self.nicr_nodes = [5]
        self.nifr_nodes = []
        self._state = np.zeros(self.K, dtype=np.int32)
        self._episode_ended = False
        self._current_attacker_node = list(self._ntpg.keys())[2]

        return ts.restart(np.array([self._state], dtype=np.int32))
    
    def __is_action_valid(self, action):
        if isinstance(action, (list, np.ndarray)):
            action = tuple(sorted(action)) if action.ndim > 1 else (action[0],)

        sorted_action_space = {k: tuple(sorted(v)) for k, v in self.action_space().items()}
        if action not in sorted_action_space.values():
            return False

        return len(action) == self._action_spec.shape[1]

    def __attacker_move_step(self):
        current_node = self._current_attacker_node
        current_node_index = list(self._ntpg.keys()).index(current_node)

        if self._ntpg.get(current_node):
            self._state[current_node_index] = 1

            pop=[route[0] for route in self._ntpg.get(current_node)]
            wei=[(route[1] + route[2])/2 for route in self._ntpg.get(current_node)]

            next_node = random.choices(
                population=pop,
                weights=wei,
                k=1
            )[0]

            self._current_attacker_node = next_node

        else:
            print("No more possible routes, exit the loop. State vector after the attack:", self._state)

        self.__update_nifr_nodes(self.nifr_nodes)

    def __update_nifr_nodes(self, action):
        self.nifr_nodes = list(action)
        
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
    
    def is_last(self):
        if self._episode_ended:
            return True
        
        return False

    def _step(self, action):
        if self._episode_ended:
            return self.reset()
        
        if self.current_step >= self.maxSteps:
            reward = -1
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
            self._episode_ended = True
        
        if self.__is_nicr_attacked(self.nicr_nodes):
            reward = -1
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
            self._episode_ended = True
            
        if self.__is_nifr_attacked(self.nifr_nodes):
            reward = 1
            return ts.termination(np.array([self._state], dtype=np.int32), reward=1)
            self._episode_ended = True
        
        if self.__is_action_valid(action):
            self.__update_nifr_nodes(action)
            self.__attacker_move_step()
            self.current_step += 1

            reward = -0.1
            return ts.transition(np.array([self._state], dtype=np.int32), reward=reward)
        
