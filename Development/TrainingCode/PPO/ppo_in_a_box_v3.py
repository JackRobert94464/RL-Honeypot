import tensorflow as tf
import numpy as np
import tensorflow_probability as tfp
from tf_agents.agents.ppo import ppo_agent
from tf_agents.networks import actor_distribution_network, value_network
from tf_agents.environments import tf_py_environment
from tf_agents.trajectories import trajectory
from tf_agents.policies import policy_saver
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.utils import common
from tf_agents.specs import array_spec, tensor_spec
from tf_agents.environments import py_environment
from tf_agents.trajectories import time_step as ts
from tf_agents.drivers import dynamic_step_driver
from tf_agents.metrics import tf_metrics
from tf_agents.eval import metric_utils
import itertools
import random
import os

class NetworkHoneypotEnv(py_environment.PyEnvironment):

    def __init__(self, N, M, K, ntpg, htpg, fnr, fpr, attack_rate):
        self.N = N
        self.M = M
        self.K = K
        self.nicr_nodes = [5]
        self.nifr_nodes = []
        my_list = list(range(1, K+1))
        combinations = list(itertools.combinations(my_list, M))
        self._action_space = dict(enumerate(combinations))
        self._action_spec = tensor_spec.BoundedTensorSpec(
            shape=(M,), dtype=tf.int32, minimum=1, maximum=K, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(K,), dtype=np.int32, minimum=0, maximum=1, name='observation')
        self._state = np.zeros(self.K, dtype=np.int32)
        self._alerted_state = np.zeros(self.K, dtype=np.int32)
        self.current_step = 0
        self.maxSteps = 50
        self._ntpg = ntpg
        self._htpg = htpg
        self._episode_ended = False
        self._current_attacker_node = list(ntpg.keys())[2]
        self.fnr = fnr
        self.fpr = fpr
        self.attack_rate = attack_rate

    def action_spec(self):
        return self._action_spec
    
    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self.current_step = 0
        self.nicr_nodes = [5]
        self.nifr_nodes = []
        self._state = np.zeros(self.K, dtype=np.int32)
        self._episode_ended = False
        self._current_attacker_node = list(self._ntpg.keys())[2]
        return ts.restart(np.array(self._state, dtype=np.int32))
    
    def _step(self, action):
        if self._episode_ended:
            return self.reset()
        if self.current_step >= self.maxSteps:
            reward = -1
            self._episode_ended = True
            return ts.termination(np.array(self._state, dtype=np.int32), reward=reward)
        if self.__is_nicr_attacked(self.nicr_nodes):
            reward = -1
            self._episode_ended = True
            return ts.termination(np.array(self._state, dtype=np.int32), reward=reward)
        if self.__is_nifr_attacked(self.nifr_nodes):
            reward = 1
            self._episode_ended = True
            return ts.termination(np.array(self._state, dtype=np.int32), reward=1)
        
        self.__update_nifr_nodes(action)
        self.__attacker_move_step_fnrfpr(self.fnr, self.fpr, self.attack_rate)
        self.current_step += 1
        reward = -0.1
        return ts.transition(np.array(self._state, dtype=np.int32), reward=reward)
    
    def __is_action_valid(self, action):
        if isinstance(action, (list, np.ndarray)):
            action = tuple(sorted(action)) if action.ndim > 1 else (action[0],)
        sorted_action_space = {k: tuple(sorted(v)) for k, v in self.action_space().items()}
        if action not in sorted_action_space.values():
            return False
        return len(action) == self._action_spec.shape[0]

    def __attacker_move_step_fnrfpr(self, fnr, fpr, attack_rate):
        non_attack_rate = 1 - attack_rate
        fn_rate = fnr * attack_rate
        fp_rate = fpr * non_attack_rate
        tp_rate = (1 - fnr) * attack_rate
        tn_rate = (1 - fpr) * non_attack_rate

        pop = [route[0] for route in self._ntpg.get(current_node)]
        wei = [(route[1] + route[2])/2 for route in self._ntpg.get(current_node)]
        next_node = random.choices(
            population=pop,
            weights=wei,
            k=1
        )[0]

        current_node_index = list(self._ntpg.keys()).index(current_node)

        state_type = random.choices(
            population=['TP', 'TN', 'FP', 'FN'],
            weights=[tp_rate, tn_rate, fp_rate, fn_rate],
            k=1
        )[0]

        current_node = self._current_attacker_node
        current_node_index = list(self._ntpg.keys()).index(current_node)
        
        if self._ntpg.get(current_node):
            if state_type in ['TP', 'FN']:
                self._state[current_node_index] = 1
            else:
                self._state[current_node_index] = 0

            if state_type in ['TP', 'FP']:
                self._alerted_state[current_node_index] = 1
            else:
                self._alerted_state[current_node_index] = 0

            if state_type in ['TP', 'FN']:
                
                
                self._current_attacker_node = next_node

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
        return self._episode_ended
    
    def __update_nifr_nodes(self, action):
        self.nifr_nodes = list(action)

import misc

if os.name == 'nt':  # If the operating system is Windows
    ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg.csv")
    htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg.csv")
else:  # For other operating systems like Linux
    ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg.csv")
    htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg.csv")

normal_nodes = misc.count_nodes(ntpg)
deception_nodes = misc.get_deception_nodes()
first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

def create_tf_environment(N, M, K, ntpg, htpg, fnr, fpr, attack_rate):
    py_env = NetworkHoneypotEnv(N, M, K, ntpg, htpg, fnr, fpr, attack_rate)
    return tf_py_environment.TFPyEnvironment(py_env)

N = first_parameter
M = deception_nodes
K = normal_nodes
fnr = 0.16
fpr = 0.1
attack_rate = 0.7

tf_env = create_tf_environment(N, M, K, ntpg, htpg, fnr, fpr, attack_rate)

actor_net = actor_distribution_network.ActorDistributionNetwork(
    tf_env.observation_spec(),
    tf_env.action_spec(),
    fc_layer_params=(100,)
)

value_net = value_network.ValueNetwork(
    tf_env.observation_spec(),
    fc_layer_params=(100,)
)

optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=1e-3)

train_step_counter = tf.Variable(0)

agent = ppo_agent.PPOAgent(
    tf_env.time_step_spec(),
    tf_env.action_spec(),
    optimizer,
    actor_net=actor_net,
    value_net=value_net,
    num_epochs=10,
    train_step_counter=train_step_counter
)

agent.initialize()

replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=tf_env.batch_size,
    max_length=10000
)

collect_driver = dynamic_step_driver.DynamicStepDriver(
    tf_env,
    agent.collect_policy,
    observers=[replay_buffer.add_batch],
    num_steps=200
)

collect_driver.run()

dataset = replay_buffer.as_dataset(
    num_parallel_calls=3,
    sample_batch_size=64,
    num_steps=2
).prefetch(3)

iterator = iter(dataset)

num_iterations = 10000

for _ in range(num_iterations):
    collect_driver.run()
    experience, _ = next(iterator)
    train_loss = agent.train(experience).loss

    if train_step_counter.numpy() % 1000 == 0:
        print(f'Step: {train_step_counter.numpy()}, Loss: {train_loss}')

policy_dir = 'ppo_policy'
tf.saved_model.save(agent.policy, policy_dir)

print("Training completed and policy saved.")
