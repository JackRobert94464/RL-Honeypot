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
import misc
import string


# This A2C will be able to adapt to many environments with the train from randomized new maps

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
        self.actionDimension = factorial(env.K) / (factorial(env.K - env.M) * factorial(env.M))
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
        self._modelPath = None
        self.model_filename = model_filename

        self.update_ntpg_matrices()

    def update_ntpg_matrices(self):
        print("NTPG TO UNPACK: ", self.env.get_ntpg())
        
        # Retrieve EPSS and NTPG matrices
        self.epssMatrix = misc.ntpg_to_epss_matrix(self.env.get_ntpg())
        self.connectionMatrix = misc.ntpg_to_connection_matrix(self.env.get_ntpg())

        # Convert matrices to numpy arrays
        epss_matrix = np.array(self.epssMatrix, dtype=np.float32)
        ntpg_matrix = np.array(self.connectionMatrix, dtype=np.float32)

        # Normalize the matrices
        epss_matrix = (epss_matrix - np.min(epss_matrix)) / (np.max(epss_matrix) - np.min(epss_matrix) + 1e-10)
        ntpg_matrix = (ntpg_matrix - np.min(ntpg_matrix)) / (np.max(ntpg_matrix) - np.min(ntpg_matrix) + 1e-10)

        # Merge EPSS and NTPG into a 3D cube for Conv2D
        merged_matrix = np.stack([epss_matrix, ntpg_matrix], axis=-1)

        # Handle varying network sizes through padding
        max_size = 42  # Required size for the model
        padded_matrix = np.zeros((max_size, max_size, 2), dtype=np.float32)
        padded_matrix[:epss_matrix.shape[0], :epss_matrix.shape[1], :] = merged_matrix

        # Repeat and stack the observable state into 3D
        observable_state = self.env.observation_space()  # np.array(observable_spec, dtype=np.float32)
        print("observable_state: ", observable_state)
        
        # Normalize the observable state
        observable_state = (observable_state - np.min(observable_state)) / (np.max(observable_state) - np.min(observable_state) + 1e-10)
        
        # Reshape observable state to match the dimensions of the padded matrix
        observable_state_expanded = np.tile(observable_state[:, np.newaxis], (1, max_size))
        observable_state_expanded = np.expand_dims(observable_state_expanded, axis=-1)

        # Pad the observable state to match the required size
        padded_observable_state = np.zeros((max_size, max_size, 1), dtype=np.float32)
        padded_observable_state[:observable_state_expanded.shape[0], :observable_state_expanded.shape[1], :] = observable_state_expanded

        # Stack observable state with the EPSS and NTPG matrices
        self.merged_matrix_input = np.concatenate([padded_matrix, padded_observable_state], axis=-1)
        self.merged_matrix_input = np.expand_dims(self.merged_matrix_input, axis=0)

    def getStepCount(self):
        return self.step_counter
    
    def updateModelPath(self, path):
        self._modelPath = path

    def retrieveModelPath(self):
        return self._modelPath
    
    def retrieveTraintimeDict(self):
        return {self.getStepCount(): self.time_taken[-1]}
        
    def build_actor_model(self):
        # Define input layer for merged input matrix
        merged_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension, 3))

        # Process merged EPSS, NTPG, and observable state matrix
        merged = tf.keras.layers.Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same')(merged_input)
        merged = tf.keras.layers.BatchNormalization()(merged)
        merged = tf.keras.layers.GlobalAveragePooling2D()(merged)

        # Interpreting the concatenated data
        x = tf.keras.layers.Dense(256, activation='tanh')(merged)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='tanh')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='tanh')(x)
        x = tf.keras.layers.BatchNormalization()(x)

        # Model output
        output = tf.keras.layers.Dense(self.actionDimension, activation='softmax')(x)

        # Create model
        model = tf.keras.Model(inputs=merged_input, outputs=output)

        return model

    
    def build_critic_model(self):
        # Define input layer for merged input matrix
        merged_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension, 3))

        # Process merged EPSS, NTPG, and observable state matrix
        merged = tf.keras.layers.Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same')(merged_input)
        merged = tf.keras.layers.BatchNormalization()(merged)
        merged = tf.keras.layers.GlobalAveragePooling2D()(merged)

        # Interpreting the concatenated data
        x = tf.keras.layers.Dense(256, activation='relu')(merged)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)

        # Model output
        output = tf.keras.layers.Dense(1)(x)

        # Create model
        model = tf.keras.Model(inputs=merged_input, outputs=output)

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
            self.step_counter += 1
            if self.step_counter in [250, 500, 750, 1000, 2000, 5000, 10000, 20000, 30000]:
                break
            self.clock_counter += time.time() - start_time
            if terminalState:
                break
            if not terminalState:
                continue
            self.replayBuffer.append((currentState.observation, action, reward, nextStateObservation, terminalState))
            self.trainNetwork()
            self.visitCounts += 1
            currentState = nextState
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
            # Ensure the input is a list containing all inputs to the model
            inputs = self.merged_matrix_input
            
            # Get action probabilities from the actor model
            action_probs = self.actor_model.predict(inputs)[0]
            
            # Select action based on the probabilities
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
            # Ensure the input is a list containing all inputs to the model
            inputs = self.merged_matrix_input
            
            # Get action probabilities from the model
            action_probs = model.predict(inputs)[0]
            
            # Select action based on the probabilities
            action_index = np.random.choice(len(action_probs), p=action_probs)
            action_matrix = self.index_to_action(action_index)
            return action_matrix
        
    def selectActionInference(self, state, model):
        # Ensure the input is a list containing all inputs to the model
        inputs = self.merged_matrix_input
        
        # Get action probabilities from the model
        action_probs = model.predict(inputs)[0]
        
        # Select action based on the probabilities
        action_index = np.random.choice(len(action_probs), p=action_probs)
        action_matrix = self.index_to_action(action_index)
        return action_matrix


    def index_to_action(self, index):
        action_space = self.env.action_space()
        valid_index = index % len(action_space)  # Wrap the index within the bounds of the action space
        action_matrix = action_space[valid_index]
        return action_matrix

    def trainNetwork(self):
        if len(self.replayBuffer) > self.batchReplayBufferSize:
            randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
            for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                advantage = self.calculate_advantage(currentState, reward, nextState)
                action_probs_old = self.actor_model.predict(currentState, self.epss_input_reshaped, self.ntpg_input_reshaped)[0]
                value_old = self.critic_model.predict(currentState, self.epss_input_reshaped, self.ntpg_input_reshaped)
                actor_loss, critic_loss = self.compute_loss(currentState, action, advantage, action_probs_old, value_old)
                self.actor_model.fit(currentState, action_probs_old, sample_weight=advantage, epochs=10, verbose=0)
                self.critic_model.fit(currentState, reward, epochs=10, verbose=0)
                
    def calculate_advantage(self, state, reward, next_state):
        state = state.reshape(1, -1)
        value = self.critic_model.predict(state, self.epss_input_reshaped, self.ntpg_input_reshaped)
        next_value = self.critic_model.predict(next_state, self.epss_input_reshaped, self.ntpg_input_reshaped)
        td_error = reward + self.gamma * next_value - value
        return td_error

    def compute_loss(self, state, action, advantage, action_probs_old, value_old):
        state = state.reshape(1, -1)
        action_probs = self.actor_model.predict(state, self.epss_input_reshaped, self.ntpg_input_reshaped)
        action_onehot = np.zeros_like(action_probs_old)
        action_onehot[action] = 1
        ratio = action_probs / (action_probs_old + 1e-5)
        clipped_ratio = np.clip(ratio, 1 - self.epsilon, 1 + self.epsilon)
        actor_loss = -np.minimum(ratio * advantage, clipped_ratio * advantage)
        critic_loss = keras.losses.mean_squared_error(value_old, advantage)
        return actor_loss, critic_loss

    def updateTrainingEpisode(self, episode):
        self.currentTrainingEpisode = episode
        
    def retrieveTrainingEpisode(self):
        return self.currentTrainingEpisode

    def saveModel(self):
        random_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if os.name == 'nt':
            os.makedirs(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}/{self.model_filename}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}/{self.model_filename}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}/{self.model_filename}_actor.keras")
        else:
            os.makedirs(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}/", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}/{self.model_filename}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}/{self.model_filename}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/A2C_ADAPTIVE/{random_token}/{self.model_filename}_actor.keras")
