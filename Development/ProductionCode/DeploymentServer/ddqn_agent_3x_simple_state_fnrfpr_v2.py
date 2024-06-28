import os
import numpy as np
import random
from keras.layers import InputLayer, Input, Dense, Concatenate
from keras.models import Sequential, Model
from keras.optimizers import RMSprop, Adam
from collections import deque 
from tensorflow import gather_nd
from keras.losses import mean_squared_error, huber
from math import factorial
import keras
import pandas as pd
import time
import tensorflow as tf
import misc
import math

actionsAppend = []

class DoubleDeepQLearning:
    
    def __init__(self, env, gamma, epsilon, numberEpisodes, nodecount, totalpermutation, fnr, fpr):
        self.env = env
        self.gamma = gamma
        self.epsilon = epsilon
        self.numberEpisodes = numberEpisodes
        self.nodecount = nodecount
        self.totalpermutation = totalpermutation

        self.stateDimension = env.K
        self.actionDimension = factorial(env.K) / (factorial(env.K - env.M) * factorial(env.M))
        self.epssDimension = env.K * env.K
        self.ntpgDimension = env.K * env.K

        self.epssMatrix = misc.ntpg_to_epss_matrix(env.get_ntpg())
        self.connectionMatrix = misc.ntpg_to_connection_matrix(env.get_ntpg())

        self.replayBufferSize = 50
        self.batchReplayBufferSize = 10
        self.updateTargetNetworkPeriod = 50
        self.counterUpdateTargetNetwork = 0
        self.sumRewardsEpisode = []
        self.episodeWon = 0
        self.replayBuffer = deque(maxlen=self.replayBufferSize)
        self.visitCounts = 0
        self.step_counter = 0
        self.step_globalcounter = []
        self.dsp_globalcounter = []
        self.clock_counter = 0
        self.time_taken = []

        self.mainNetwork = self.createNetwork()
        self.targetNetwork = self.createNetwork()
        self.targetNetwork.set_weights(self.mainNetwork.get_weights())
        
        self._fnr = fnr
        self._fpr = fpr
        
        self._modelPath = None
        self.currentTrainingEpisode = 0
        
        epss_matrix = np.array(self.epssMatrix)
        ntpg_matrix = np.array(self.connectionMatrix)
        if len(epss_matrix.shape) > 2:
            epss_matrix = np.stack(epss_matrix)
        if len(ntpg_matrix.shape) > 2:
            ntpg_matrix = np.stack(ntpg_matrix)
        epss_input = np.expand_dims(epss_matrix, axis=-1)
        ntpg_input = np.expand_dims(ntpg_matrix, axis=-1)
        self.epss_input_reshaped = np.array(epss_input).reshape(-1, self.stateDimension, self.stateDimension)
        self.ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, self.stateDimension, self.stateDimension)
        
    def updateTrainingEpisode(self, episode):
        self.currentTrainingEpisode = episode
        
    def retrieveTrainingEpisode(self):
        return self.currentTrainingEpisode
        
    def updateModelPath(self, path):
        self._modelPath = path
        
    def retrieveModelPath(self):
        return self._modelPath
    
    def retrieveTraintimeDict(self):
        return {self.getStepCount(): self.time_taken[-1]}
     
    @keras.saving.register_keras_serializable()
    def ddqn_loss_fn(y_true, y_pred):
        s1, s2 = y_true.shape
        countact = len(actionsAppend)
        num_actions = len(actionsAppend[0])
        indices = np.zeros(shape=(s1 * num_actions, 2))
        indices[:, 0] = np.repeat(np.arange(s1), num_actions)
        indices[:, 1] = np.tile(np.arange(num_actions), s1)
        loss = keras.losses.mean_squared_error(keras.backend.gather(y_true, indices=indices.astype(int)),
                                            keras.backend.gather(y_pred, indices=indices.astype(int)))
        return loss

    def createNetwork(self):
        observable_input = tf.keras.layers.Input(shape=(self.stateDimension,))
        epss_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        ntpg_input = tf.keras.layers.Input(shape=(self.stateDimension, self.stateDimension))
        
        obs = tf.keras.layers.Dense(32, activation='relu')(observable_input)
        epss = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(epss_input)
        epss = tf.keras.layers.BatchNormalization()(epss)
        epss = tf.keras.layers.GlobalAveragePooling1D()(epss)
        ntpg = tf.keras.layers.Conv1D(64, kernel_size=2, activation='relu', padding='same')(ntpg_input)
        ntpg = tf.keras.layers.BatchNormalization()(ntpg)
        ntpg = tf.keras.layers.GlobalAveragePooling1D()(ntpg)
        concatenated = tf.keras.layers.Concatenate()([obs, epss, ntpg])
        x = tf.keras.layers.Dense(256, activation='relu')(concatenated)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        output = tf.keras.layers.Dense(self.actionDimension, activation='softmax')(x)
        model = Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer='adam', metrics=['accuracy'])
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
            if self.step_counter in [250, 500, 750, 1000, 2000, 5000, 10000, 20000, 30000, 50000]:
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
        
    def trainingInferenceSync(self, rt_buffer, rt_action_buffer):
        for i in range(len(rt_buffer) - 1):
            currentState = rt_buffer[i]
            currentAction = rt_action_buffer[i]
            nextState = rt_buffer[i+1]
            
            currentReward = -1 if currentState[7] == 1 else -0.1 if any(currentState[i] == 1 for i, a in enumerate(currentAction) if a == 1) else 0
            currentTerminal = True if currentState[7] == 1 or any(currentState[i] == 1 for i, a in enumerate(currentAction) if a == 1) else False
            
            self.replayBuffer.append((currentState, self.epss_input_reshaped, self.ntpg_input_reshaped, currentAction, currentReward, nextState, currentTerminal))
            self.trainNetwork()
            
            # Save after train
            self.saveModelInference()
            
            currentState = nextState
            
    def trainingInferenceAsync(self, rt_buffer, rt_action_buffer):
        for i in range(len(rt_buffer) - 1):
            currentState = rt_buffer[i]
            currentAction = rt_action_buffer[i]
            nextState = rt_buffer[i+1]
            
            currentReward = -1 if currentState[7] == 1 else -0.1 if any(currentState[i] == 1 for i, a in enumerate(currentAction) if a == 1) else 0
            currentTerminal = True if currentState[7] == 1 or any(currentState[i] == 1 for i, a in enumerate(currentAction) if a == 1) else False
            
            self.replayBuffer.append((currentState, self.epss_input_reshaped, self.ntpg_input_reshaped, currentAction, currentReward, nextState, currentTerminal))
            self.trainNetwork()
            
            # Currently async cant save model yet
            
            currentState = nextState
                       
    def getStepCount(self):
        return self.step_counter
    
    def getGlobalStepCount(self):
        return self.step_globalcounter
    
    def getGlobalDSPCount(self):
        return self.dsp_globalcounter
    
    def getGlobalTimeTaken(self):
        return self.time_taken
    
    def selectAction(self, state, episode):
        randomValue = np.random.random()
        if episode > 20:
            self.epsilon = 0.999 * self.epsilon
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
            state = state.reshape(1, -1)
            
            Qvalues = self.mainNetwork.predict([state, self.epss_input_reshaped, self.ntpg_input_reshaped])
            max_index = np.argmax(Qvalues)
            action_matrix = self.index_to_action(max_index)
            return action_matrix

    def index_to_action(self, index):
        action_matrix = self.env.action_space()[index]
        return action_matrix

    def trainNetwork(self):
        if len(self.replayBuffer) > self.batchReplayBufferSize:
            randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
            currentStateBatch = np.zeros(shape=(self.batchReplayBufferSize, self.nodecount))
            epsBatch = np.zeros(shape=(self.batchReplayBufferSize, self.nodecount, self.nodecount))
            ntpgBatch = np.zeros(shape=(self.batchReplayBufferSize, self.nodecount, self.nodecount))
            nextStateBatch = np.zeros(shape=(self.batchReplayBufferSize, self.nodecount))
            for index, (currentState, epsMatrix, ntpgMatrix, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                currentStateBatch[index, :] = currentState
                epsBatch[index, :, :] = epsMatrix
                ntpgBatch[index, :, :] = ntpgMatrix
                nextStateBatch[index, :] = nextState
            QnextStateTargetNetwork = self.targetNetwork.predict([nextStateBatch, epsBatch, ntpgBatch])
            QcurrentStateMainNetwork = self.mainNetwork.predict([currentStateBatch, epsBatch, ntpgBatch])
            inputNetwork = [currentStateBatch, epsBatch, ntpgBatch]
            outputNetwork = np.zeros(shape=(self.batchReplayBufferSize, int(self.totalpermutation)))
            for index, (currentState, epsMatrix, ntpgMatrix, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                y = reward + self.gamma * np.max(QnextStateTargetNetwork[index])
                actionsAppend.append(action)
                outputNetwork[index] = QcurrentStateMainNetwork[index]
                outputNetwork[index, action] = y
            self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, verbose=0, epochs=2)
            self.counterUpdateTargetNetwork += 1
            if self.counterUpdateTargetNetwork > (self.updateTargetNetworkPeriod - 1):
                self.targetNetwork.set_weights(self.mainNetwork.get_weights())
                self.counterUpdateTargetNetwork = 0

    def selectActionEval(self, state, episode, model):
        if episode < 1:
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action
        randomValue = np.random.random()
        if episode > 20:
            self.epsilon = 0.999 * self.epsilon
        if randomValue < self.epsilon:
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action
        else:
            state = state.reshape(1, -1)
            epss_matrix = np.array(self.epssMatrix)
            ntpg_matrix = np.array(self.connectionMatrix)
            if len(epss_matrix.shape) > 2:
                epss_matrix = np.stack(epss_matrix)
            if len(ntpg_matrix.shape) > 2:
                ntpg_matrix = np.stack(ntpg_matrix)
            epss_input = np.expand_dims(epss_matrix, axis=-1)
            ntpg_input = np.expand_dims(ntpg_matrix, axis=-1)
            epss_input_reshaped = np.array(epss_input).reshape(-1, self.stateDimension, self.stateDimension)
            ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, self.stateDimension, self.stateDimension)
            Qvalues = self.mainNetwork.predict([state, epss_input_reshaped, ntpg_input_reshaped])
            max_index = np.argmax(Qvalues)
            action_matrix = self.index_to_action(max_index)
            return action_matrix
    
    def selectActionInferenceConv1D(self, state, model):
        epss_matrix = np.array(self.epssMatrix)        
        ntpg_matrix = np.array(self.connectionMatrix)
        if len(epss_matrix.shape) > 2:
            epss_matrix = np.stack(epss_matrix)
        if len(ntpg_matrix.shape) > 2:
            ntpg_matrix = np.stack(ntpg_matrix)
        epss_input = np.expand_dims(epss_matrix, axis=-1)
        ntpg_input = np.expand_dims(ntpg_matrix, axis=-1)
        epss_input_reshaped = np.array(epss_input).reshape(-1, len(state), len(state))
        ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, len(state), len(state))
        state = np.array(state, dtype=np.float32).reshape(1, -1)
        Qvalues = model.predict([state, epss_input_reshaped, ntpg_input_reshaped])
        max_index = np.argmax(Qvalues)
        action_matrix = self.index_to_action(max_index)
        return action_matrix
    
    def selectActionInferenceConv1Dv2(self, state, model):
        epss_matrix = np.array(self.epssMatrix)        
        ntpg_matrix = np.array(self.connectionMatrix)
        if len(epss_matrix.shape) > 2:
            epss_matrix = np.stack(epss_matrix)
        if len(ntpg_matrix.shape) > 2:
            ntpg_matrix = np.stack(ntpg_matrix)
        epss_input = np.expand_dims(epss_matrix, axis=-1)
        ntpg_input = np.expand_dims(ntpg_matrix, axis=-1)
        epss_input_reshaped = np.array(epss_input).reshape(-1, len(state), len(state))
        ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, len(state), len(state))
        state = np.array(state, dtype=np.float32).reshape(1, -1)
        Qvalues = model.predict([state, epss_input_reshaped, ntpg_input_reshaped])
        max_index = np.argmax(Qvalues)
        action_matrix = self.index_to_action(max_index)

        # Ensure honeypot position does not align with compromised nodes
        compromised_nodes = [i for i, x in enumerate(state[0]) if x == 1]

        # Determine the subnets of all nodes
        def get_subnet(node):
            return 0 if node in range(0, 2) else 1 if node in range(2, 5) else 2 if node in range(5, 8) else 3

        # Determine the subnets of compromised nodes
        compromised_subnets = {get_subnet(node) for node in compromised_nodes}

        # Adjust action to place honeypot within the same subnet as the compromised nodes
        adjusted_action_matrix = []
        for action in action_matrix:
            if action not in compromised_nodes and get_subnet(action) in compromised_subnets:
                adjusted_action_matrix.append(action)
            else:
                # Find an alternative within the same subnet
                for alt_action in range(len(state[0])):
                    if alt_action not in compromised_nodes and get_subnet(alt_action) == get_subnet(action):
                        adjusted_action_matrix.append(alt_action)
                        break
                else:
                    # If no alternative found, keep the original action
                    adjusted_action_matrix.append(action)
        
        # Ensure the final_action has the same shape and type as the original action_matrix
        final_action = adjusted_action_matrix
        
        return final_action



        
    def saveModel(self):
        if os.name == 'nt':
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.mainNetwork.save(f".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_1to5_conv1D_simpleinput_v2_win_ver{self.getStepCount()}.keras")
            self.updateModelPath(f".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_1to5_conv1D_simpleinput_v2_win_ver{self.getStepCount()}.keras")
        else:
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.mainNetwork.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_1to5_conv1D_simpleinput_v2_linux_ver{self.getStepCount()}.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_1to5_conv1D_simpleinput_v2_linux_ver{self.getStepCount()}.keras")
            
    def saveModelInference(self):
        if os.name == 'nt':
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.mainNetwork.save(f".\\RL_Honeypot_1to5_conv1D_simpleinput_v2_linux_ver49890.keras")
            self.updateModelPath(f".\\RL_Honeypot_1to5_conv1D_simpleinput_v2_linux_ver49890.keras")
        else:
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.mainNetwork.save(f"./RL_Honeypot_1to5_conv1D_simpleinput_v2_linux_ver49890.keras")
            self.updateModelPath(f"./RL_Honeypot_1to5_conv1D_simpleinput_v2_linux_ver49890.keras")
