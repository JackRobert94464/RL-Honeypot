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
import string

# Define the PPO Agent class
class PPOAgent:
    def __init__(self, model_filename, env, gamma, epsilon, numberEpisodes, nodecount, totalpermutation, fnr, fpr):
        self.env = env
        self.gamma = gamma
        self.epsilon = epsilon
        self.numberEpisodes = numberEpisodes
        self.nodecount = nodecount
        self.totalpermutation = totalpermutation
        self.stateDimension = env.K
        self.actionDimension = len(env.action_space())  # FIX: was a float from '/', and Dense needs an int
        self.replayBufferSize = 300
        self.batchReplayBufferSize = 100
        self.updateTargetNetworkPeriod = 10
        self.counterUpdateTargetNetwork = 0
        self.sumRewardsEpisode = []
        self.episodeWon = 0
        self.replayBuffer = deque(maxlen=self.replayBufferSize)
        self.visitCounts = 0
        self.step_counter = 0
        self.clock_counter = 0
        self.time_taken = []
        self._fnr = fnr
        self._fpr = fpr
        self.currentTrainingEpisode = 0
        self.actor_model = self.build_actor_model()
        self.critic_model = self.build_critic_model()
        self.actor_optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
        self.critic_optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
        self._modelPath = None
        self.model_filename = model_filename

    def getStepCount(self):
        return self.step_counter
    
    def updateModelPath(self, path):
        self._modelPath = path

    def retrieveModelPath(self):
        return self._modelPath
    
    def retrieveTraintimeDict(self):
        return {self.getStepCount(): self.time_taken[-1]}
        
    def build_actor_model(self):
        model = Sequential()
        model.add(InputLayer(input_shape=self.stateDimension))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.actionDimension, activation='softmax'))
        return model
    
    def build_critic_model(self):
        model = Sequential()
        model.add(InputLayer(input_shape=self.stateDimension))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(1))
        return model

    def trainingSingleEpisodes(self):
        currentState = self.env.reset()
        rewardsEpisode = []
        while not self.env.is_last():
            start_time = time.time()
            alerted_observation = self.env.get_alerted_state()
            alerted_observation = np.array(alerted_observation)
            alerted_observation = np.expand_dims(alerted_observation, axis=0)
            action = self.selectAction(alerted_observation, self.retrieveTrainingEpisode())
            nextState = self.env.step(action)
            (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, nextState.reward, self.env.is_last())
            rewardsEpisode.append(reward)
            if reward == 1:
                self.episodeWon += 1
            # FIX: learn from every transition. The old 'if terminalState: break / if not terminalState: continue'
            # left the loop before this point on every step, so the networks never trained.
            self.trainNetwork(currentState.observation, action, reward, nextStateObservation, terminalState)
            self.visitCounts += 1
            currentState = nextState
            self.step_counter += 1
            self.clock_counter += time.time() - start_time
            if self.step_counter in [250, 500, 750, 1000, 2000, 5000, 10000, 20000, 30000]:
                break
            if terminalState:
                break
        self.time_taken.append(self.clock_counter)
        
    def selectAction(self, state, episode):
        randomValue = np.random.random()
        if episode < 3:
            action_space_values = list(self.env.action_space().values())        
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action
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
        
    def selectActionEval(self, state, episode, model):
        randomValue = np.random.random()
        if episode < 3:
            action_space_values = list(self.env.action_space().values())        
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action
        if randomValue < self.epsilon:
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action
        else:
            action_probs = model.predict(state)[0]
            action_index = np.random.choice(len(action_probs), p=action_probs)
            action_matrix = self.index_to_action(action_index)
            return action_matrix

    def index_to_action(self, index):
        action_matrix = self.env.action_space()[index]
        return action_matrix

    def action_to_index(self, action):
        if not hasattr(self, '_action_index'):
            self._action_index = {tuple(v): k for k, v in self.env.action_space().items()}
        return self._action_index[tuple(int(x) for x in np.ravel(action))]

    def model_inputs(self, observation):
        return np.array(observation, dtype=np.float32).reshape(1, -1)
    # FIX: one-step advantage actor-critic update on the transition just taken. The old version fitted the actor to its
    # own previous probabilities and the critic to the raw reward (and indexed the action by node IDs), so it could not learn.
    def trainNetwork(self, currentState, action, reward, nextState, terminated):
        inputs = self.model_inputs(currentState)
        next_value = 0.0 if terminated else float(self.critic_model(self.model_inputs(nextState), training=False)[0, 0])
        target = float(reward) + self.gamma * next_value
        action_index = self.action_to_index(action)
        with tf.GradientTape() as actor_tape, tf.GradientTape() as critic_tape:
            # training=False keeps BatchNormalization on its moving statistics; on a batch of one it would zero the activations
            value = self.critic_model(inputs, training=False)[0, 0]
            probs = self.actor_model(inputs, training=False)[0]
            advantage = target - value
            critic_loss = tf.square(advantage)
            actor_loss = -tf.math.log(probs[action_index] + 1e-8) * tf.stop_gradient(advantage)
        critic_grads = critic_tape.gradient(critic_loss, self.critic_model.trainable_variables)
        actor_grads = actor_tape.gradient(actor_loss, self.actor_model.trainable_variables)
        self.critic_optimizer.apply_gradients(zip(critic_grads, self.critic_model.trainable_variables))
        self.actor_optimizer.apply_gradients(zip(actor_grads, self.actor_model.trainable_variables))

    def updateTrainingEpisode(self, episode):
        self.currentTrainingEpisode = episode
        
    def retrieveTrainingEpisode(self):
        return self.currentTrainingEpisode

    def saveModel(self):
        random_token = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))
        if os.name == 'nt':
            os.makedirs(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}/{self.model_filename}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}/{self.model_filename}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}/{self.model_filename}_actor.keras")
        else:
            os.makedirs(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}/{self.model_filename}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}/{self.model_filename}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/A2C_1_INPUT/{random_token}/{self.model_filename}_actor.keras")
