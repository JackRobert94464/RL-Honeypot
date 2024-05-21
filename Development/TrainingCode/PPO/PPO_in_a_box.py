import os
import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np
import itertools
import gymnasium as gym
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
import random
import scipy
import misc

class NetworkHoneypotEnv(py_environment.PyEnvironment):
    def __init__(self, N, M, K, ntpg, htpg):
        self.N = N
        self.M = M
        self.K = K
        self.nicr_nodes = [5]
        self.nifr_nodes = []
        my_list = list(range(1, K + 1))
        combinations = list(itertools.combinations(my_list, M))
        self._action_space = dict(enumerate(combinations))
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(M,), dtype=np.int32, minimum=1, maximum=K, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(K,), dtype=np.int32, minimum=0, maximum=1, name='observation')
        self._reward_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.float32, minimum=-1.0, maximum=1.0, name='reward')
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

    def observation_space(self):
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
        return ts.restart(np.array(self._state, dtype=np.int32))

    def __is_action_valid(self, action):
        if isinstance(action, (list, np.ndarray)):
            action = tuple(sorted(action)) if action.ndim > 1 else (action[0],)
        sorted_action_space = {k: tuple(sorted(v)) for k, v in self.action_space().items()}
        if action not in sorted_action_space.values():
            return False
        return len(action) == self._action_spec.shape[0]

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
            self._current_attacker_node = next_node

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
            return self._reset()

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
            return ts.termination(np.array(self._state, dtype=np.int32), reward=reward)

        self.__update_nifr_nodes(action)
        self.__attacker_move_step()
        self.current_step += 1
        reward = -0.1
        return ts.transition(np.array(self._state, dtype=np.int32), reward=reward)

# PPO Implementation
class Buffer:
    def __init__(self, observation_dimensions, action_dimensions, size, gamma=0.99, lam=0.95):
        self.observation_buffer = np.zeros((size, observation_dimensions), dtype=np.float32)
        self.action_buffer = np.zeros((size, action_dimensions), dtype=np.int32)
        self.advantage_buffer = np.zeros(size, dtype=np.float32)
        self.reward_buffer = np.zeros(size, dtype=np.float32)
        self.return_buffer = np.zeros(size, dtype=np.float32)
        self.value_buffer = np.zeros(size, dtype=np.float32)
        self.logprobability_buffer = np.zeros(size, dtype=np.float32)
        self.gamma, self.lam = gamma, lam
        self.pointer, self.trajectory_start_index = 0, 0

    def store(self, observation, action, reward, value, logprobability):
        self.observation_buffer[self.pointer] = observation
        self.action_buffer[self.pointer] = action
        self.reward_buffer[self.pointer] = reward
        self.value_buffer[self.pointer] = value
        self.logprobability_buffer[self.pointer] = logprobability
        self.pointer += 1

    def finish_trajectory(self, last_value=0):
        path_slice = slice(self.trajectory_start_index, self.pointer)
        rewards = np.append(self.reward_buffer[path_slice], last_value)
        values = np.append(self.value_buffer[path_slice], last_value)

        deltas = rewards[:-1] + self.gamma * values[1:] - values[:-1]

        self.advantage_buffer[path_slice] = discounted_cumulative_sums(deltas, self.gamma * self.lam)
        self.return_buffer[path_slice] = discounted_cumulative_sums(rewards, self.gamma)[:-1]

        self.trajectory_start_index = self.pointer

    def get(self):
        self.pointer, self.trajectory_start_index = 0, 0
        advantage_mean, advantage_std = np.mean(self.advantage_buffer), np.std(self.advantage_buffer)
        self.advantage_buffer = (self.advantage_buffer - advantage_mean) / advantage_std
        return (
            self.observation_buffer,
            self.action_buffer,
            self.advantage_buffer,
            self.return_buffer,
            self.logprobability_buffer,
        )

def discounted_cumulative_sums(x, discount):
    return scipy.signal.lfilter([1], [1, float(-discount)], x[::-1], axis=0)[::-1]

def mlp(x, sizes, activation=tf.nn.relu, output_activation=None):
    for size in sizes[:-1]:
        x = layers.Dense(units=size, activation=activation)(x)
    return layers.Dense(units=sizes[-1], activation=output_activation)(x)

def logprobabilities(logits, a, num_actions):
    logprobabilities_all = tf.nn.log_softmax(logits)
    action_one_hot = tf.one_hot(a, num_actions)

    # Ensure the number of actions aligns between the two tensors
    num_actions = tf.shape(action_one_hot)[-1]

    action_one_hot_flat = tf.reshape(action_one_hot, (-1, num_actions))
    logprobabilities_all_flat = tf.reshape(logprobabilities_all, (-1, num_actions))

    # Reshape to a common shape
    common_shape = tf.stack([tf.shape(action_one_hot_flat)[0], num_actions])

    return tf.reduce_sum(action_one_hot_flat * logprobabilities_all_flat, axis=1)



def get_action(observation):
    logits = logprobability_function(observation)
    action = tf.random.categorical(logits, 1)[:, 0]
    return action

# Load the TPG data
if os.name == 'nt':  # If the operating system is Windows
    ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_big.csv")
    htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_big.csv")
else:  # For other operating systems like Linux
    ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg.csv")
    htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg.csv")

normal_nodes = misc.count_nodes(ntpg)
print("Normal nodes:", normal_nodes)

seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)
env = NetworkHoneypotEnv(N=10, M=3, K=20, ntpg=ntpg, htpg=htpg)  # replace with your ntpg and htpg data
observation_dimensions = env.observation_spec().shape[0]
num_actions = len(env.action_space())

steps_per_epoch = 4000
epochs = 30
gamma = 0.99
clip_ratio = 0.2
policy_learning_rate = 3e-4
value_function_learning_rate = 1e-3
train_policy_iterations = 80
train_value_iterations = 80
lam = 0.97
target_kl = 0.01
hidden_sizes = (64, 64)
render = False

buffer = Buffer(observation_dimensions, env.action_spec().shape[0], steps_per_epoch)
observation_input = keras.Input(shape=(observation_dimensions,), dtype=tf.float32)
logits = mlp(observation_input, list(hidden_sizes) + [num_actions], activation=tf.tanh, output_activation=None)
actions = tf.random.categorical(logits, 1)
get_action_model = keras.Model(inputs=observation_input, outputs=actions)

logprobability_function = keras.Model(inputs=observation_input, outputs=logits)

value_function = keras.Sequential([
    keras.Input(shape=(observation_dimensions,)),
    layers.Dense(64, activation='tanh'),
    layers.Dense(64, activation='tanh'),
    layers.Dense(1)
])

policy_optimizer = tf.keras.optimizers.Adam(learning_rate=policy_learning_rate)
value_optimizer = tf.keras.optimizers.Adam(learning_rate=value_function_learning_rate)

for epoch in range(epochs):
    time_step = env.reset()
    observation = time_step.observation
    for t in range(steps_per_epoch):
        action = get_action(observation[None, :])
        time_step = env.step(action)
        next_observation = time_step.observation
        reward = time_step.reward
        done = time_step.is_last()
        value_t = value_function(observation[None, :])[0, 0]
        logprobability_t = logprobability_function(observation[None, :])[0, 0]

        buffer.store(observation, action, reward, value_t.numpy().item(), logprobability_t.numpy().item())

        observation = next_observation

        terminal = done or (t == steps_per_epoch - 1)
        if terminal:
            last_value = 0 if done else value_function(observation[None, :])[0, 0]
            buffer.finish_trajectory(last_value)
            time_step = env.reset()
            observation = time_step.observation

    observation_buffer, action_buffer, advantage_buffer, return_buffer, logprobability_buffer = buffer.get()

    dataset = tf.data.Dataset.from_tensor_slices((observation_buffer, action_buffer, advantage_buffer, return_buffer, logprobability_buffer))
    dataset = dataset.shuffle(steps_per_epoch).batch(64)

    for epoch in range(train_policy_iterations):
        for batch in dataset:
            with tf.GradientTape() as tape:
                observation_batch, action_batch, advantage_batch, return_batch, logprobability_batch = batch
                logits_batch = logprobability_function(observation_batch)
                new_logprobabilities_batch = logprobabilities(logits_batch, action_batch, num_actions)

                ratio = tf.exp(new_logprobabilities_batch - logprobability_batch)
                min_advantage = tf.where(advantage_batch > 0, (1 + clip_ratio) * advantage_batch, (1 - clip_ratio) * advantage_batch)
                policy_loss = -tf.reduce_mean(tf.minimum(ratio * advantage_batch, min_advantage))

            policy_grads = tape.gradient(policy_loss, logprobability_function.trainable_variables)
            policy_optimizer.apply_gradients(zip(policy_grads, logprobability_function.trainable_variables))

            kl = tf.reduce_mean(logprobability_batch - new_logprobabilities_batch)
            if kl > 1.5 * target_kl:
                break


    for _ in range(train_value_iterations):
        for batch in dataset:
            with tf.GradientTape() as tape:
                observation_batch, action_batch, advantage_batch, return_batch, logprobability_batch = batch
                value_t = value_function(observation_batch)
                value_loss = tf.reduce_mean((return_batch - value_t) ** 2)

            value_grads = tape.gradient(value_loss, value_function.trainable_variables)
            value_optimizer.apply_gradients(zip(value_grads, value_function.trainable_variables))
