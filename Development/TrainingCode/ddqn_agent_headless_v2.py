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

# import FNR FPR simulation code

from fnr_fpr_test.fnrfpr_calc_v2 import simulate_alert_training

actionsAppend = []

class DoubleDeepQLearning:
    
    def __init__(self, env, gamma, epsilon, numberEpisodes, nodecount, totalpermutation, fnr, fpr):
        keras.backend.clear_session()
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
        
    def updateTrainingEpisode(self, episode):
        self.currentTrainingEpisode = episode
        
    def retrieveTrainingEpisode(self):
        return self.currentTrainingEpisode
    
    def updateModelPath(self, path):
        self._modelPath = path
        
    def retrieveModelPath(self):
        return self._modelPath
    
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
        model = Sequential()
        model.add(InputLayer(input_shape=self.stateDimension))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.actionDimension, activation='softmax'))
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics=['accuracy'])
        return model
    
    def trainingEpisodes(self):
        step_visualization = []
        steps = []
        ntpg = self.env.get_ntpg()
        htpg = self.env.get_htpg()
        your_nodes_list = list(ntpg.keys())
        your_edges_list = [(node, edge[0]) for node in ntpg for edge in ntpg[node]]
        data = pd.DataFrame(columns=['attacker_node', 'nifr_nodes', 'nicr_nodes' , 'nodes', 'edges', 'episode'])
        
        for episode in range(self.numberEpisodes):
            currentState = self.env.reset()
            rewardsEpisode = []
            step_count = 0

            while not self.env.is_last():
                start_time = time.time()
                action = self.selectAction(currentState.observation.reshape(1, -1), episode)
                nextState = self.env.step(action)
                steps.append({'attacker_node': self.env._current_attacker_node, 
                              'nifr_nodes': [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nifr_nodes], 
                              'nicr_nodes': [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nicr_nodes],})
                (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, nextState.reward, self.env.is_last())
                rewardsEpisode.append(reward)
                if reward == 1:
                    self.episodeWon += 1
                step_count += 1
                self.clock_counter += time.time() - start_time

                if terminalState:
                    break
                    
                if not terminalState:
                    continue

                self.replayBuffer.append((currentState.observation, action, reward, nextStateObservation, terminalState))
                self.trainNetwork()
                self.visitCounts += 1
                currentState = nextState

            self.step_counter += step_count

            if episode % 2 == 0:
                self.step_globalcounter.append(self.getStepCount())
                dsp = self.episodeWon / (episode+1)
                self.time_taken.append(self.clock_counter)
                self.dsp_globalcounter.append(dsp)

        self.sumRewardsEpisode.append(np.sum(rewardsEpisode)) 

    def trainingSingleEpisodes(self):
        currentState = self.env.reset()
        rewardsEpisode = []
        step_count = 0
        
        #Initialize alerted observation (Defender's view of the network through Network Monitoring System)
        alerted_initial = [0] * len(currentState.observation.reshape(1, -1)[0])
        
        while not self.env.is_last():
            start_time = time.time()

            alerted_observation = simulate_alert_training(currentState.observation.reshape(1, -1)[0], alerted_initial, self._fnr, self._fpr)
            alerted_initial = alerted_observation
            

            alerted_observation = np.array(alerted_observation)
            alerted_observation = np.expand_dims(alerted_observation, axis=0)

            action = self.selectAction(alerted_observation, self.retrieveTrainingEpisode())

            nextState = self.env.step(action)
            
            (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, nextState.reward, self.env.is_last())

            rewardsEpisode.append(reward)
            if reward == 1:
                self.episodeWon += 1
            step_count += 1
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
        
        self.step_counter += step_count

    def getStepCount(self):
        return self.step_counter
    
    def getGlobalStepCount(self):
        return self.step_globalcounter
    
    def getGlobalDSPCount(self):
        return self.dsp_globalcounter
    
    def getGlobalTimeTaken(self):
        return self.time_taken
    
    def retrieveTraintimeDict(self):
        return {self.getStepCount(): self.time_taken[-1]}
    
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
            Qvalues = self.mainNetwork.predict(state)
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
            nextStateBatch = np.zeros(shape=(self.batchReplayBufferSize, self.nodecount))      
            for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                currentStateBatch[index, :] = currentState
                nextStateBatch[index, :] = nextState
             
            QnextStateTargetNetwork = self.targetNetwork.predict(nextStateBatch)
            QcurrentStateMainNetwork = self.mainNetwork.predict(currentStateBatch)
             
            inputNetwork = currentStateBatch
            outputNetwork = np.zeros(shape=(self.batchReplayBufferSize, int(self.totalpermutation)))
             
            for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                if terminated:
                    y = reward                  
                else:
                    y = reward + self.gamma * np.max(QnextStateTargetNetwork[index])
                 
                actionsAppend.append(action)
                
                if action[0] >= self.totalpermutation:
                    print(f"Warning: Invalid action {action} for index {index}. Skipping this sample.")
                    continue

                outputNetwork[index] = QcurrentStateMainNetwork[index]
                outputNetwork[index, action] = y
             
            self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, verbose=1, epochs=100)
             
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
            Qvalues = model.predict(state)
            max_index = np.argmax(Qvalues)
            action_matrix = self.index_to_action(max_index)
            return action_matrix
        
    def saveModel(self):
        if os.name == 'nt':
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.mainNetwork.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_1to5_obsdense_decoy_win_ver{self.getStepCount()}.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_1to5_obsdense_decoy_win_ver{self.getStepCount()}.keras")
            
        else:
            os.makedirs("./TrainedModel/weighted_random_attacker", exist_ok=True)
            self.mainNetwork.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_1to5_obsdense_decoy_linux_ver{self.getStepCount()}.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_1to5_obsdense_decoy_linux_ver{self.getStepCount()}.keras")
