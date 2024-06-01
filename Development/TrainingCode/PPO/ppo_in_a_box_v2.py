import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
import gym
import os
import misc
import itertools
from gym import spaces
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

    def step(self, action):
        if self._episode_ended:
            return self.reset(), 0, False, {}

        if self.current_step >= self.maxSteps:
            reward = -1
            self._episode_ended = True
            return self._state, reward, True, {}

        self.__attacker_move_step()

        if self.__is_nicr_attacked(self.nicr_nodes):
            reward = -1
            self._episode_ended = True
            return self._state, reward, True, {}

        self.__update_nifr_nodes(self._action_space[action])
        if self.__is_nifr_attacked(self.nifr_nodes):
            reward = 1
            self._episode_ended = True
            return self._state, reward, True, {}

        self.current_step += 1
        reward = -0.1
        return self._state, reward, False, {}

# Environment parameters
N = 10  # Number of network nodes
M = 2   # Number of honeypot nodes to deploy
K = 10  # Total number of nodes


if os.name == 'nt':  # If the operating system is Windows
        ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg.csv")
        htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg.csv")
else:  # For other operating systems like Linux
        ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg.csv")
        htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg.csv")

# Create the environment
env = NetworkHoneypotEnv(N, M, K, ntpg, htpg)

# Set hyperparameters
EPISODES = 10000
LOSS_CLIPPING = 0.2
EPOCHS = 10
NOISE = 1.0
GAMMA = 0.99
BUFFER_SIZE = 2048
BATCH_SIZE = 256
NUM_ACTIONS = env.action_space.n
NUM_STATE = env.observation_space.shape[0]
HIDDEN_SIZE = 128
NUM_LAYERS = 2
ENTROPY_LOSS = 5e-3
LR = 1e-4

# Define custom loss layer
class PPOLoss(layers.Layer):
    def __init__(self, entropy_loss=ENTROPY_LOSS, loss_clipping=LOSS_CLIPPING):
        super().__init__()
        self.entropy_loss = entropy_loss
        self.loss_clipping = loss_clipping

    def call(self, inputs):
        y_true, y_pred, advantage, old_prediction = inputs

        prob = tf.reduce_sum(y_true * y_pred, axis=-1, keepdims=True)
        old_prob = tf.reduce_sum(y_true * old_prediction, axis=-1, keepdims=True)
        r = prob / (old_prob + 1e-10)
        clipped_r = tf.clip_by_value(r, 1 - self.loss_clipping, 1 + self.loss_clipping)
        
        advantage = tf.cast(advantage, y_pred.dtype)
        surrogate_loss = tf.minimum(r * advantage, clipped_r * advantage)
        entropy_bonus = self.entropy_loss * -(prob * tf.math.log(prob + 1e-10))
        loss = -tf.reduce_mean(surrogate_loss + entropy_bonus)
        
        return loss

# Create dummy tensors
DUMMY_ACTION, DUMMY_VALUE = np.zeros((1, NUM_ACTIONS)), np.zeros((1, 1))

# Define models
class Agent:
    def __init__(self):
        self.critic = self.build_critic()
        self.actor = self.build_actor()

        self.env = env
        self.episode = 0
        self.observation = self.env.reset()
        self.val = False
        self.reward = []
        self.reward_over_time = []
        self.name = self.get_name()
        self.summary_writer = tf.summary.create_file_writer(self.name)
        self.gradient_steps = 0

    def get_name(self):
        name = 'AllRuns/discrete/NetworkHoneypotEnv'
        return name

    def build_actor(self):
        state_input = keras.Input(shape=(NUM_STATE,))
        advantage = keras.Input(shape=(1,))
        old_prediction = keras.Input(shape=(NUM_ACTIONS,))

        x = layers.Dense(HIDDEN_SIZE, activation='tanh')(state_input)
        for _ in range(NUM_LAYERS - 1):
            x = layers.Dense(HIDDEN_SIZE, activation='tanh')(x)

        out_actions = layers.Dense(NUM_ACTIONS, activation='softmax', name='output')(x)

        model = keras.Model(inputs=[state_input, advantage, old_prediction], outputs=[out_actions])
        loss_layer = PPOLoss()
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=LR),
                    loss=lambda y_true, y_pred: loss_layer([y_true, y_pred, advantage, old_prediction]))

        return model


    def build_critic(self):
        state_input = keras.Input(shape=(NUM_STATE,))
        x = layers.Dense(HIDDEN_SIZE, activation='tanh')(state_input)
        for _ in range(NUM_LAYERS - 1):
            x = layers.Dense(HIDDEN_SIZE, activation='tanh')(x)

        out_value = layers.Dense(1)(x)

        model = keras.Model(inputs=[state_input], outputs=[out_value])
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=LR), loss='mse')

        return model

    def reset_env(self):
        self.episode += 1
        self.val = (self.episode % 100 == 0)
        self.observation = self.env.reset()
        self.reward = []

    def get_action(self):
        p = self.actor.predict([self.observation.reshape(1, NUM_STATE), DUMMY_VALUE, DUMMY_ACTION])
        if not self.val:
            action = np.random.choice(NUM_ACTIONS, p=np.nan_to_num(p[0]))
        else:
            action = np.argmax(p[0])
        action_matrix = tf.one_hot(action, NUM_ACTIONS)
        return action, action_matrix, p

    def transform_reward(self):
        if self.val:
            with self.summary_writer.as_default():
                tf.summary.scalar('Val episode reward', np.array(self.reward).sum(), self.episode)
        else:
            with self.summary_writer.as_default():
                tf.summary.scalar('Episode reward', np.array(self.reward).sum(), self.episode)
        for j in range(len(self.reward) - 2, -1, -1):
            self.reward[j] += self.reward[j + 1] * GAMMA

    def get_batch(self):
        batch = [[], [], [], []]

        tmp_batch = [[], [], []]
        while len(batch[0]) < BUFFER_SIZE:
            action, action_matrix, predicted_action = self.get_action()
            observation, reward, done, info = self.env.step(action)
            self.reward.append(reward)

            tmp_batch[0].append(self.observation)
            tmp_batch[1].append(action_matrix)
            tmp_batch[2].append(predicted_action)
            self.observation = observation

            if done:
                self.transform_reward()
                if not self.val:
                    for i in range(len(tmp_batch[0])):
                        obs, action, pred = tmp_batch[0][i], tmp_batch[1][i], tmp_batch[2][i]
                        r = self.reward[i]
                        batch[0].append(obs)
                        batch[1].append(action)
                        batch[2].append(pred)
                        batch[3].append(r)
                tmp_batch = [[], [], []]
                self.reset_env()

        obs, action, pred, reward = np.array(batch[0]), np.array(batch[1]), np.array(batch[2]), np.reshape(np.array(batch[3]), (len(batch[3]), 1))
        pred = np.reshape(pred, (pred.shape[0], pred.shape[2]))
        return obs, action, pred, reward

    def run(self):
        while self.episode < EPISODES:
            obs, action, pred, reward = self.get_batch()
            obs, action, pred, reward = obs[:BUFFER_SIZE], action[:BUFFER_SIZE], pred[:BUFFER_SIZE], reward[:BUFFER_SIZE]
            old_prediction = pred
            pred_values = self.critic.predict(obs)

            advantage = reward - pred_values
            
            print("obs: ", obs)
            print("action: ", action)
            print("old_prediction: ", old_prediction)
            print("advantage: ", advantage)
            print("obs type: ", type(obs))
            print("action type: ", type(action))
            print("old_prediction type: ", type(old_prediction))
            print("advantage type: ", type(advantage))

            actor_loss = self.actor.train_on_batch([obs, advantage, old_prediction], [action])
            critic_loss = self.critic.train_on_batch([obs], [reward])
            with self.summary_writer.as_default():
                tf.summary.scalar('Actor loss', actor_loss, self.gradient_steps)
                tf.summary.scalar('Critic loss', critic_loss, self.gradient_steps)

            self.gradient_steps += 1


if __name__ == '__main__':
   ag = Agent()
   ag.run()