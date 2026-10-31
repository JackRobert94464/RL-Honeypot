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

# FIX: node IDs used by actions, nifr_nodes and nicr_nodes are 1-based: node ID k is list(ntpg.keys())[k-1].
# FIX: the critical node used to be checked as self._state[5] (0-based), which is node ID 6.
DEFAULT_NICR_NODES = [6]

class NetworkHoneypotEnv(py_environment.PyEnvironment):

    def __init__(self, N, M, K, ntpg, fnr, fpr, attack_rate, nicr_nodes=None):
        self.N = N
        self.M = M
        self.K = K
        if nicr_nodes is None:
            nicr_nodes = DEFAULT_NICR_NODES
        elif not isinstance(nicr_nodes, (list, tuple)):
            nicr_nodes = [nicr_nodes]
        self._initial_nicr_nodes = list(nicr_nodes)
        self.nicr_nodes = list(self._initial_nicr_nodes)
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
        self._state = np.zeros(self.K, dtype=np.int32)  # True compromise state (hidden from the defender)
        self._alerted_state = np.zeros(self.K, dtype=np.int32)  # FIX: what the IDS reports; this is now the observation (it used to return the true state, so FNR/FPR had no effect)
        self.current_step = 0
        self.maxSteps = 50
        self._ntpg = ntpg
        self._episode_ended = False
        self.fnr = fnr
        self.fpr = fpr
        self.attack_rate = attack_rate
        print("NTPG:", self._ntpg.keys())
        self.__start_attacker()
        print("Initial attacker node: ", self._current_attacker_node)

    def action_spec(self):
        return self._action_spec

    def action_space(self):
        return self._action_space

    def observation_spec(self):
        return self._observation_spec

    def get_ntpg(self):
        return self._ntpg

    def get_alerted_state(self):
        return self._alerted_state

    def pick_initial_attacker_node(self):
        # chua chay, co bao nhieu lo hong tren 3 node nay thi cong lai lay trung binh epss lam weight
        return random.choices(
            population=[list(self._ntpg.keys())[0], list(self._ntpg.keys())[1], list(self._ntpg.keys())[6]],
            weights=[0.00834, 0.00338, 0.00612],
            k=1
        )[0]

    def __node_id(self, node):
        return list(self._ntpg.keys()).index(node) + 1

    def __start_attacker(self):
        self._current_attacker_node = self.pick_initial_attacker_node()
        start_index = self.__node_id(self._current_attacker_node) - 1
        self._state[start_index] = 1
        # FIX: the initial foothold is only seen if the IDS does not miss it
        if random.random() >= self.fnr:
            self._alerted_state[start_index] = 1

    def __observation(self):
        return np.array([self._alerted_state], dtype=np.int32)

    def _reset(self):
        self.current_step = 0
        self.nicr_nodes = list(self._initial_nicr_nodes)  # FIX: was hardcoded to [5], ignoring the constructor argument
        self.nifr_nodes = []
        self._state = np.zeros(self.K, dtype=np.int32)
        self._alerted_state = np.zeros(self.K, dtype=np.int32)  # FIX: was never reset, so alerts piled up across episodes
        self._episode_ended = False
        self.__start_attacker()
        print("Reset attacker node: ", self._current_attacker_node)
        # os.system('pause')
        return ts.restart(self.__observation())

    def __is_action_valid(self, action):
        if isinstance(action, (list, np.ndarray)):
            action = tuple(sorted(action)) if action.ndim > 1 else (action[0],)
        sorted_action_space = {k: tuple(sorted(v)) for k, v in self.action_space().items()}
        if action not in sorted_action_space.values():
            return False
        return len(action) == self._action_spec.shape[1]

    def __attacker_move_step_fnrfpr(self, fnr, fpr, attack_rate):
        # Returns the node ID the attacker moved into this step, or None if it did not move

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

        if not self._ntpg.get(current_node):
            return None

        # Pick next node based on weighted random choice
        pop = [route[0] for route in self._ntpg.get(current_node)]
        wei = [(route[1] + route[2])/2 for route in self._ntpg.get(current_node)]

        # Adjust weights to reduce the chance of always falling into a honeypot
        adjusted_weights = []
        for node, weight in zip(pop, wei):
            if self.is_honeypot(node):
                adjusted_weights.append(weight * 0.5)  # Reducing the weight for honeypots
            else:
                adjusted_weights.append(weight)
        if sum(adjusted_weights) <= 0:
            adjusted_weights = None  # FIX: all-zero weights: fall back to a uniform choice

        next_node = random.choices(
            population=pop,
            weights=adjusted_weights,
            k=1
        )[0]

        next_node_index = self.__node_id(next_node) - 1

        # Update the alerted state
        # Set cho nay thanh next node 30 05 2024
        if state_type in ['TP', 'FP']:
            self._alerted_state[next_node_index] = 1

        # Update the true state
        if state_type in ['TP', 'FN']:
            self._state[next_node_index] = 1
            self._current_attacker_node = next_node
            return next_node_index + 1

        return None

    # FIX: compares node IDs; it used to compare NTPG keys (IPs) with node IDs, so the honeypot weighting never applied
    def is_honeypot(self, node):
        return self.__node_id(node) in self.nifr_nodes

    def is_last(self):
        if self._episode_ended:
            return True
        return False

    def __update_nifr_nodes(self, action):
        self.nifr_nodes = [int(node_id) for node_id in np.ravel(action)]

    def _step(self, action):

        if self._episode_ended:
            return self.reset()

        # FIX: deploy the honeypots first, then let the attacker move, so the reward belongs to this action
        self.__update_nifr_nodes(action)
        entered_node = self.__attacker_move_step_fnrfpr(self.fnr, self.fpr, self.attack_rate)
        self.current_step += 1

        # FIX: only the node the attacker just entered counts (also fixes the off-by-one 0-based/1-based check); a honeypot placed on an already-compromised node is not a catch
        if entered_node is not None and entered_node in self.nifr_nodes:
            self._episode_ended = True
            return ts.termination(self.__observation(), reward=1)
        if entered_node is not None and entered_node in self.nicr_nodes:
            self._episode_ended = True
            return ts.termination(self.__observation(), reward=-1)
        if self.current_step >= self.maxSteps:
            self._episode_ended = True
            return ts.termination(self.__observation(), reward=-1)

        reward = -0.1
        return ts.transition(self.__observation(), reward=reward)
