import tensorflow as tf
import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
import gym
from gym import spaces
import numpy as np
import os
import random
import itertools

class NetworkHoneypotEnv(py_environment.PyEnvironment):

    def __init__(self, N, M, K, ntpg, fnr, fpr, attack_rate, nicr_nodes):
        self.N = N
        self.M = M
        self.K = K
        self.nicr_nodes = nicr_nodes
        self.nifr_nodes = []
        
        # For node guessing
        # my_list = list(range(1, K+1))
        
        # For subnet guessing (static placeholder, MUST CHANGE, implement subnet retrieval from NTPG)
        my_list = list(range(1, 5))
        
        combinations = list(itertools.combinations(my_list, M))
        self._action_space = dict(enumerate(combinations))
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(1, M), dtype=np.int32, minimum=1, maximum=K, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(1,K), dtype=np.int32, minimum=0, maximum=1, name='observation')
        self._reward_spec = array_spec.BoundedArraySpec(
            shape=(1,K), dtype=np.int32, minimum=-1, maximum=1, name='reward')
        self._state = np.zeros(self.K, dtype=np.int32)
        self._alerted_state = np.zeros(self.K, dtype=np.int32)  # New alerted state array
        self.current_step = 0
        self.maxSteps = 50
        self._ntpg = ntpg
        self._episode_ended = False
        # self._current_attacker_node = list(ntpg.keys())[2]
        # chua chay, co bao nhieu lo hong tren 3 node nay thi cong lai lay trung binh epss lam weight
        print("NTPG:", self._ntpg.keys())
        self._current_attacker_node = self.random_initial_attacker_node()
        print("Initial attacker node: ", self._current_attacker_node)
        # os.system('pause')
        self.fnr = fnr
        self.fpr = fpr
        self.attack_rate = attack_rate
        
    def random_initial_attacker_node(self):
        # Randomly select an initial attacker node from the NTPG keys
        return random.choice(list(self._ntpg.keys()))

    def action_spec(self):
        return self._action_spec
    
    def action_space(self):
        return self._action_space
    
    def observation_spec(self):
        return self._observation_spec
    
    def observation_space(self):
        return self._state
    
    def get_ntpg(self):
        return self._ntpg
    
    def get_htpg(self):
        return self._htpg
    
    def get_alerted_state(self):
        return self._alerted_state
    
    import os
    
    def generate_random_ntpg(self):
        # Generate a new NTPG with the same number of nodes (K)
        new_ntpg = {}
        for i in range(1, self.K + 1):
            connections = []
            for j in range(random.randint(1, self.K // 2)):
                target_node = random.randint(1, self.K)
                weight1 = random.random()
                weight2 = random.random()
                connections.append((target_node, weight1, weight2))
            new_ntpg[i] = connections
        self._ntpg = new_ntpg
        # print("New NTPG: ", new_ntpg)
        # os.system('pause')
        self._current_attacker_node = list(new_ntpg.keys())[2]

    def _reset(self):
        self.current_step = 0
        self.nicr_nodes = [5]
        self.nifr_nodes = []
        self._state = np.zeros(self.K, dtype=np.int32)
        self._episode_ended = False
        self._current_attacker_node = self.random_initial_attacker_node()  # Randomize initial attacker node
        print("Reset attacker node: ", self._current_attacker_node)
        self.generate_random_ntpg()  # Generate a new NTPG for each episode
        # os.system('pause')
        return ts.restart(np.array([self._state], dtype=np.int32))

    def __attacker_move_step_fnrfpr(self, fnr, fpr, attack_rate):
        non_attack_rate = 1 - attack_rate

        # FN, FP, TP, TN rates
        fn_rate = fnr * attack_rate
        fp_rate = fpr * non_attack_rate
        tp_rate = (1 - fnr) * attack_rate
        tn_rate = (1 - fpr) * non_attack_rate

        # Determine the state type (TP, TN, FP, FN) based on the probabilities
        state_type = random.choices(
            population=['TP', 'TN', 'FP', 'FN'],
            weights=[tp_rate, tn_rate, fp_rate, fn_rate],
            k=1
        )[0]

        current_node = self._current_attacker_node
        current_node_index = list(self._ntpg.keys()).index(current_node)

        if self._ntpg.get(current_node):

            self._state[current_node_index] = 1

            # Pick next node based on weighted random choice
            pop = [route[0] for route in self._ntpg.get(current_node)]
            wei = [(route[1] + route[2])/2 for route in self._ntpg.get(current_node)]
            
            # Adjust weights to reduce the chance of always falling into a honeypot
            adjusted_weights = []
            for node, weight in zip(pop, wei):
                if self.is_honeypot(node):  # Assuming a function that checks if a node is a honeypot
                    adjusted_weights.append(weight * 0.5)  # Reducing the weight for honeypots
                else:
                    adjusted_weights.append(weight)
            
            next_node = random.choices(
                population=pop,
                weights=adjusted_weights,
                k=1
            )[0]

            next_node_index = list(self._ntpg.keys()).index(next_node)

            # Update the true state
            if state_type in ['TP', 'FN']:
                self._state[next_node_index] = 1
            # else:
            #    self._state[next_node_index] = 0

            # Update the alerted state
            # Set cho nay thanh next node 30 05 2024
            if state_type in ['TP', 'FP']:
                self._alerted_state[next_node_index] = 1
            # else:
            #    self._alerted_state[next_node_index] = 0

            if state_type in ['TP', 'FN']:
                self._current_attacker_node = next_node

    def is_honeypot(self, node):
        # Placeholder function to check if a node is a honeypot
        # You should implement the actual logic to check if a node is a honeypot
        return node in self.nifr_nodes  # Assuming you have a list of honeypot nodes stored in self._honeypots


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
    
    def __update_nifr_nodes(self, action):
        self.nifr_nodes = list(action)
    
    def _step(self, action):

        if self._episode_ended:
            return self.reset()
        if self.current_step >= self.maxSteps:
            reward = -1
            self._episode_ended = True
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
        if self.__is_nicr_attacked(self.nicr_nodes):
            reward = -1
            self._episode_ended = True
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
        if self.__is_nifr_attacked(self.nifr_nodes):
            reward = 1
            self._episode_ended = True
            return ts.termination(np.array([self._state], dtype=np.int32), reward=1)
        
        self.__update_nifr_nodes(action)
        self.__attacker_move_step_fnrfpr(self.fnr, self.fpr, self.attack_rate)
        self.current_step += 1
        reward = -0.1
        return ts.transition(np.array([self._state], dtype=np.int32), reward=reward)
