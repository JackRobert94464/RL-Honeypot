import os
import numpy as np
import random
from keras.layers import Dense, InputLayer
from keras.models import Sequential
from keras.optimizers import RMSprop
from collections import deque
from math import factorial
import keras
import pandas as pd
import time
import tensorflow as tf
from keras import layers

# Define the PPO Agent class
class PPOAgent:
    def __init__(self, env, gamma, epsilon, numberEpisodes, nodecount, totalpermutation, fnr, fpr):
        self.env = env
        self.gamma = gamma
        self.epsilon = epsilon
        self.numberEpisodes = numberEpisodes
        self.nodecount = nodecount
        self.totalpermutation = totalpermutation
        self.stateDimension = env.K
        self.actionDimension = int(factorial(env.K) / (factorial(env.K - env.M) * factorial(env.M)))
        self.sumRewardsEpisode = []
        self.episodeWon = 0
        self.step_counter = 0
        self.clock_counter = 0
        self.time_taken = []
        self._fnr = fnr
        self._fpr = fpr
        self.currentTrainingEpisode = 0
        self.actor_model = self.build_actor_model()
        self.critic_model = self.build_critic_model()
        self._modelPath = None

    def getStepCount(self):
        return self.step_counter

    def updateModelPath(self, path):
        self._modelPath = path

    def retrieveModelPath(self):
        return self._modelPath

    def build_actor_model(self):
        model = Sequential()
        model.add(InputLayer(input_shape=(self.stateDimension,)))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.actionDimension, activation='softmax'))
        print(model.summary())
        return model

    def build_critic_model(self):
        model = Sequential()
        model.add(InputLayer(input_shape=(self.stateDimension,)))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(1))
        print(model.summary())
        return model

    def trainingSingleEpisodes(self):
        currentState = self.env.reset()
        rewardsEpisode = []
        states, actions, rewards, dones = [], [], [], []

        while not self.env.is_last():
            start_time = time.time()
            alerted_observation = self.env.get_alerted_state()
            alerted_observation = np.array(alerted_observation)
            alerted_observation = np.expand_dims(alerted_observation, axis=0)
            action = self.selectAction(alerted_observation)
            nextState = self.env.step(action)
            (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, nextState.reward, self.env.is_last())

            states = currentState.observation
            actions.append(action)
            rewards.append(reward)
            dones.append(terminalState)

            rewardsEpisode.append(reward)
            if reward == 1:
                self.episodeWon += 1
            self.step_counter += 1
            if self.step_counter in [250, 500, 750, 1000, 2000, 5000, 10000, 20000, 30000]:
                break
            self.clock_counter += time.time() - start_time
            if terminalState:
                break
            currentState = nextState

        self.time_taken.append(self.clock_counter)
        self.trainNetwork(states, actions, rewards, dones)

    def selectAction(self, state):
        randomValue = np.random.random()
        if randomValue < self.epsilon:
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action
        else:
            action_probs = self.actor_model.predict(state)[0]
            action_index = np.random.choice(len(action_probs), p=action_probs)
            action_matrix = self.index_to_action(action_index)
            return action_matrix

    def index_to_action(self, index):
        action_matrix = self.env.action_space()[index]
        return action_matrix

    def trainNetwork(self, states, actions, rewards, dones):
        states = np.array(states)
        actions = np.array(actions)
        rewards = np.array(rewards)
        dones = np.array(dones)

        advantages, returns = self.calculate_advantages_and_returns(rewards, dones, states)

        actions_onehot = tf.keras.utils.to_categorical(actions, num_classes=self.actionDimension)
        
        for _ in range(self.updateTargetNetworkPeriod):
            actor_loss, critic_loss = self.compute_loss(states, actions_onehot, advantages, returns)
            self.actor_model.fit(states, actions_onehot, sample_weight=advantages, epochs=1, verbose=0)
            self.critic_model.fit(states, returns, epochs=1, verbose=0)

    def calculate_advantages_and_returns(self, rewards, dones, states):
        values = []
        for state in states:
            values.append(self.critic_model.predict(state[0]).flatten())
        # values = self.critic_model.predict(states).flatten()
        print(f"values: {values}")
        print(f"rewards: {rewards}")
        returns = np.zeros_like(rewards)
        advantages = np.zeros_like(rewards)

        gae = 0
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]

            print(f"rewards: {rewards[t]}")
            print(f"next_value: {next_value}")
            print(f"dones: {dones[t]}")
            print(f"t: {t}")

            delta = rewards[t] + self.gamma * next_value * (1 - dones[t]) - values[t]
            advantages[t] = gae = delta + self.gamma * self.epsilon * (1 - dones[t]) * gae
            returns[t] = advantages[t] + values[t]

        return advantages, returns

    def compute_loss(self, states, actions_onehot, advantages, returns):
        action_probs = self.actor_model.predict(states)
        action_probs_old = tf.stop_gradient(action_probs)

        ratios = tf.reduce_sum(action_probs * actions_onehot, axis=1) / tf.reduce_sum(action_probs_old * actions_onehot, axis=1)
        clipped_ratios = tf.clip_by_value(ratios, 1 - self.epsilon, 1 + self.epsilon)

        surrogate1 = ratios * advantages
        surrogate2 = clipped_ratios * advantages
        actor_loss = -tf.reduce_mean(tf.minimum(surrogate1, surrogate2))

        critic_loss = tf.reduce_mean(tf.square(returns - self.critic_model.predict(states).flatten()))

        return actor_loss, critic_loss

    def updateTrainingEpisode(self, episode):
        self.currentTrainingEpisode = episode

    def retrieveTrainingEpisode(self):
        return self.currentTrainingEpisode

    def saveModel(self):
        if os.name == 'nt':
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_PPO_win_ver{self.getStepCount()}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_PPO_win_ver{self.getStepCount()}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_PPO_win_ver{self.getStepCount()}_actor.keras")
        else:
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_PPO_linux_ver{self.getStepCount()}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_PPO_linux_ver{self.getStepCount()}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_PPO_linux_ver{self.getStepCount()}_actor.keras")
