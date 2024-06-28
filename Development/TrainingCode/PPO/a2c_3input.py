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



        self.epssMatrix = misc.ntpg_to_epss_matrix(env.get_ntpg())
        self.connectionMatrix = misc.ntpg_to_connection_matrix(env.get_ntpg())

        # Convert the matrices to numpy arrays
        epss_matrix = np.array(self.epssMatrix)
        # print("EPSS MATRIX:", epss_matrix)
        
        ntpg_matrix = np.array(self.connectionMatrix)
        # print("NTPG MATRIX:", ntpg_matrix)
        

        # Check if the matrices have a nested list structure
        if len(epss_matrix.shape) > 2:
            epss_matrix = np.stack(epss_matrix)
        if len(ntpg_matrix.shape) > 2:
            ntpg_matrix = np.stack(ntpg_matrix)

        # Expand the dimensions of the state to match the batch size of the other inputs
        # state = np.repeat(state, epss_matrix.shape[0], axis=0)
        # print("STATE:", state)
        

        # Make sure the shapes of the inputs match
        epss_input = np.expand_dims(epss_matrix, axis=-1)
        # print("EPSS INPUT:", epss_input)

        ntpg_input = np.expand_dims(ntpg_matrix, axis=-1)
        # print("NTPG INPUT:", ntpg_input)

        self.epss_input_reshaped = np.array(epss_input).reshape(-1, self.stateDimension, self.stateDimension)
        self.ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, self.stateDimension, self.stateDimension)


    def getStepCount(self):
        return self.step_counter
    
    def updateModelPath(self, path):
        self._modelPath = path

    def retrieveModelPath(self):
        return self._modelPath
    
    def retrieveTraintimeDict(self):
        return {self.getStepCount(): self.time_taken[-1]}
        
    def build_actor_model(self):
        # Define input layers for each type of input data
        observable_input = tf.keras.layers.Input(shape=(self.stateDimension))
        epss_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        ntpg_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        
        # First interpretation model
        obs = tf.keras.layers.Dense(32, activation='relu')(observable_input)

        # Branch 2: Process EPSS matrix
        epss = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(epss_input)
        epss = tf.keras.layers.BatchNormalization()(epss)
        epss = tf.keras.layers.GlobalAveragePooling1D()(epss)

        # Branch 3: Process ntpg penetration graph
        ntpg = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(ntpg_input)
        ntpg = tf.keras.layers.BatchNormalization()(ntpg)
        ntpg = tf.keras.layers.GlobalAveragePooling1D()(ntpg)

        # Concatenate the outputs of all branches
        concatenated = tf.keras.layers.Concatenate()([obs, epss, ntpg])

        
        # Giu nguyen cac lop nay de cho cac model sau nay
        # Interpreting the concatenated data
        x = tf.keras.layers.Dense(256, activation='relu')(concatenated)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)

        # model output
        output = tf.keras.layers.Dense(self.actionDimension, activation='softmax')(x)

        # Create model
        model = keras.Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)

        return model

    
    def build_critic_model(self):
        # model = Sequential()
        # model.add(InputLayer(input_shape=self.stateDimension))
        # model.add(Dense(64, activation='relu'))
        # model.add(Dense(64, activation='relu'))
        # model.add(Dense(1))

        # Define input layers for each type of input data
        observable_input = tf.keras.layers.Input(shape=(self.stateDimension))
        epss_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        ntpg_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        
        # First interpretation model
        obs = tf.keras.layers.Dense(32, activation='relu')(observable_input)

        # Branch 2: Process EPSS matrix
        epss = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(epss_input)
        epss = tf.keras.layers.BatchNormalization()(epss)
        epss = tf.keras.layers.GlobalAveragePooling1D()(epss)

        # Branch 3: Process ntpg penetration graph
        ntpg = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(ntpg_input)
        ntpg = tf.keras.layers.BatchNormalization()(ntpg)
        ntpg = tf.keras.layers.GlobalAveragePooling1D()(ntpg)

        # Concatenate the outputs of all branches
        concatenated = tf.keras.layers.Concatenate()([obs, epss, ntpg])

        
        # Giu nguyen cac lop nay de cho cac model sau nay
        # Interpreting the concatenated data
        x = tf.keras.layers.Dense(256, activation='relu')(concatenated)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)

        # model output
        output = tf.keras.layers.Dense(1)(x)

        # Create model
        model = keras.Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)


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
            inputs = [state, self.epss_input_reshaped, self.ntpg_input_reshaped]
            
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
            inputs = [state, self.epss_input_reshaped, self.ntpg_input_reshaped]
            
            # Get action probabilities from the model
            action_probs = model.predict(inputs)[0]
            
            # Select action based on the probabilities
            action_index = np.random.choice(len(action_probs), p=action_probs)
            action_matrix = self.index_to_action(action_index)
            return action_matrix


    def index_to_action(self, index):
        action_matrix = self.env.action_space()[index]
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
            os.makedirs(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}/RL_Honeypot_actorcrit_win_ver{self.getStepCount()}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}/RL_Honeypot_actorcrit_win_ver{self.getStepCount()}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}/RL_Honeypot_actorcrit_win_ver{self.getStepCount()}_actor.keras")
        else:
            os.makedirs(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}/", exist_ok=True)
            self.actor_model.save(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}/RL_Honeypot_actorcrit_linux_ver{self.getStepCount()}_actor.keras")
            self.critic_model.save(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}/RL_Honeypot_actorcrit_linux_ver{self.getStepCount()}_critic.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/A2C_3_INPUT/{random_token}/RL_Honeypot_actorcrit_linux_ver{self.getStepCount()}_actor.keras")
