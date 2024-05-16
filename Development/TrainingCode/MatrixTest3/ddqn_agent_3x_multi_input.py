# print("------------------------------------------------------------------------------------------------------------------------")   
# print("------------------------------------------------------------------------------------------------------------------------")
# print("------------------------------------------------------------------------------------------------------------------------")
# print("------------------------------------------------------------------------------------------------------------------------")
# print("---------------------------------------  TRAINING THE AGENT BASED ON THE ENV -------------------------------------------")
# print("------------------------------------------------------------------------------------------------------------------------")   
# print("------------------------------------------------------------------------------------------------------------------------")
# print("------------------------------------------------------------------------------------------------------------------------")
# print("------------------------------------------------------------------------------------------------------------------------")


import os



####################################################################################
# This is the code for the DQN agent
# I will use the same code from the TF-Agents tutorial
####################################################################################

# import the necessary libraries
import numpy as np
import random

from keras.layers import InputLayer
from keras.models import Sequential
from keras.layers import Input, Dense, Concatenate
from keras.models import Model

# Trying different optimizers
from keras.optimizers import RMSprop
from keras.optimizers import Adam

from collections import deque 
from tensorflow import gather_nd

# Trying different loss function
from keras.losses import mean_squared_error 
from keras.losses import huber

from math import factorial

import keras
 

import pandas as pd
import time

import random

import tensorflow as tf



# Import the neural network
# import ddqn_network_test_3

# Import the input matrices creating function
from . import test_3_field_01_epss_matrix
from . import test_3_field_02_ntpg_matrix


import math


# Outline the difference from cartpole:
# Policy
# - The policy is a function that maps states to actions.
# - The policy is represented by a neural network that takes the state as input and outputs the action.
# - The policy is trained by the agent to maximize the total reward.
# - Here, we use a neural network with two hidden layers of 100 units each and ReLU activation.
# - The final layer is a dense layer with 2 units, one for each possible action in the deception network environment.

# hình như thầy bảo cố định lại 1 cái môi trường HTPG NTPG
# 14/11/2023 - đã cố định một môi trường HTPG-NTPG

actionsAppend = []


class DoubleDeepQLearning:
    
    ###########################################################################
    #   START - __init__ function
    ###########################################################################
    # INPUTS: 
    # env - Training network environment
    # gamma - discount rate
    # epsilon - parameter for epsilon-greedy approach
    # numberEpisodes - total number of simulation episodes
    
      
    def __init__(self,env,gamma,epsilon,numberEpisodes,nodecount,totalpermutation):
        self.env=env
        self.gamma=gamma
        self.epsilon=epsilon
        self.numberEpisodes=numberEpisodes

        # self.n = "total number of nodes"
        # self.m = "number of deception resource available"
        # self.k = "number of normal nodes"

        # normal node count
        self.nodecount = nodecount

        # matrix stuff
        # actually permutation without repetition
        # P(n,r) = n! / (n-r)!
        # with n as normal nodes and r as deception nodes
        self.totalpermutation = totalpermutation

        # print(env)

        
        # -------------------------- Define the dimensions --------------------------
        
        # state dimension 
        self.stateDimension = env.K
        # print("STATE DIMENSION --- AGENT TRAINING",self.stateDimension)
        # action dimension k!/(k-m)! (07/12/2023 - different permutation problem)
        # WARNING ABOVE IS LOGIC FAULT
        # 06/04/2024
        # đặt 2 fake resource vào 7 node -> cần chọn 2 trong 7 node để đặt -> tính tổ hợp chập 2 của 7: C(7,2) = 21
        # => Tinh to hop C(K,M) = k!/((k-m)!*m!) = 7!/(5!*2!) = 21

        self.actionDimension = factorial(env.K) / (factorial(env.K - env.M) * factorial(env.M))
        
        self.epssDimension = env.K * env.K
        
        self.ntpgDimension = env.K * env.K
        
        # -------------------------- Define the dimensions --------------------------
        
        
        # -------------------------- The Input Matrices --------------------------
        
        self.epssMatrix = test_3_field_01_epss_matrix.ntpg_to_epss_matrix(env.get_ntpg())
        self.connectionMatrix = test_3_field_02_ntpg_matrix.ntpg_to_connection_matrix(env.get_ntpg())
        
        # -------------------------- The Input Matrices --------------------------
        
        
        
        
        
        # print("ACTION DIMENSION --- AGENT TRAINING",self.actionDimension)
        # this is the maximum size of the replay buffer
        self.replayBufferSize=300
        # this is the size of the training batch that is randomly sampled from the replay buffer
        self.batchReplayBufferSize=100

        # number of training episodes it takes to update the target network parameters
        # that is, every updateTargetNetworkPeriod we update the target network parameters
        self.updateTargetNetworkPeriod=10

        # this is the counter for updating the target network 
        # if this counter exceeds (updateTargetNetworkPeriod-1) we update the network 
        # parameters and reset the counter to zero, this process is repeated until the end of the training process
        self.counterUpdateTargetNetwork=0


        # this sum is used to store the sum of rewards obtained during each training episode
        self.sumRewardsEpisode=[]
        
        # number of episode won
        # TODO: replace this later
        self.episodeWon = 0

        # replay buffer
        self.replayBuffer=deque(maxlen=self.replayBufferSize)

        # initialize visit(s,a)
        self.visitCounts = 0
        
        # initialize step counter
        # Counter for the number of steps each episode takes
        self.step_counter = 0
        
        # Create a list to store step count every 50 episodes
        self.step_globalcounter = []

        # Create a list to store dsp every 50 episodes
        self.dsp_globalcounter = []
        
        # Clock Counter for time taken
        self.clock_counter = 0
        
        # Create a list to store time taken for training
        self.time_taken = []

        # this list is used in the cost function to select certain entries of the 
        # predicted and true sample matrices in order to form the loss
        # self.actionsAppend=[]
        
        '''
        Legacy
        
        # this is the main network
        # create network
        self.mainNetwork=self.createNetwork()

        # this is the target network
        # create network
        self.targetNetwork=self.createNetwork()
        '''
        
        self.mainNetwork = self.createNetwork()
        
        self.targetNetwork = self.createNetwork()
        

        
        
        # copy the initial weights to targetNetwork
        self.targetNetwork.set_weights(self.mainNetwork.get_weights())
        
     
    ###########################################################################
    #   END - __init__ function
    ###########################################################################
        
    
     
     
     ###########################################################################
    # START - function for defining the loss (cost) function
    # FIX THIS ASAP
    # Status: FIX THIS ASAP
    # INPUTS: 
    #
    # y_true - matrix of dimension (self.batchReplayBufferSize,2) - this is the target 
    # y_pred - matrix of dimension (self.batchReplayBufferSize,2) - this is predicted by the network
    # 
    # - this function will select certain row entries from y_true and y_pred to form the output 
    # the selection is performed on the basis of the action indices in the list  self.actionsAppend
    # - this function is used in createNetwork(self) to create the network
    #
    # OUTPUT: 
    #    
    # - loss - watch out here, this is a vector of (self.batchReplayBufferSize,1), 
    # with each entry being the squared error between the entries of y_true and y_pred
    # later on, the tensor flow will compute the scalar out of this vector (mean squared error)
    ###########################################################################    
    
    @keras.saving.register_keras_serializable()
    def ddqn_loss_fn(y_true, y_pred):
        # print("LOSS FUNCTION - Y_TRUE:", y_true)
        s1, s2 = y_true.shape
        # print("LOSS FUNCTION - S1 AND S2:", s1, s2)
        # print("LOSS FUNCTION - ACTIONS APPEND:", actionsAppend)

        # count the amount of actions in actionsAppend
        countact = len(actionsAppend)
        # print("LOSS FUNCTION - COUNTACT:", countact)


        # Calculate the number of actions
        num_actions = len(actionsAppend[0])

        # Reshape indices to have shape (batch_size * num_actions, 2)
        indices = np.zeros(shape=(s1 * num_actions, 2))
        indices[:, 0] = np.repeat(np.arange(s1), num_actions)
        indices[:, 1] = np.tile(np.arange(num_actions), s1)


        loss = keras.losses.mean_squared_error(keras.backend.gather(y_true, indices=indices.astype(int)),
                                            keras.backend.gather(y_pred, indices=indices.astype(int)))
        return loss

    ###########################################################################
    #   END - of function my_loss_fn
    ###########################################################################    


    ###########################################################################
    #   START - createNetwork function
    ###########################################################################

    # https://datascience.stackexchange.com/questions/97518/valueerror-data-cardinality-is-ambiguous-in-model-ensemble-with-2-different-i
    # https://datascience.stackexchange.com/questions/32455/which-convolution-should-i-use-conv2d-or-conv1d

    def createNetwork(self):
        # Define input layers for each type of input data
        observable_input = Input(shape=(self.stateDimension,1))
        epss_input = Input(shape=(self.stateDimension, self.stateDimension))
        ntpg_input = Input(shape=(self.stateDimension, self.stateDimension))

        # Branch 1: Process observable matrix
        
        observable_features = int(math.sqrt(self.stateDimension))
        
        
        # TODO: Branch 1 will use LSTM for memorizing the observable matrix
        # Branch 1: Process observable matrix (using LSTM)
        observable_branch_lstm = keras.layers.LSTM(observable_features, activation='relu')(observable_input)
        
        # First interpretation model
        observable_branch_1 = Dense(observable_features, activation='relu')(observable_branch_lstm)
        
        # Second interpretation model
        observable_branch_21 = Dense(observable_features, activation='relu')(observable_branch_lstm)
        observable_branch_22 = Dense(observable_features * 2, activation='relu')(observable_branch_21)
        observable_branch_23 = Dense(observable_features, activation='relu')(observable_branch_22)
        
        # Merge the two interpretation models
        observable_concatenated = Concatenate()([observable_branch_1, observable_branch_23])
        
        # output
        observable_output = Dense(self.stateDimension, activation='relu')(observable_concatenated)


        

        # Branch 2: Process EPSS matrix
        epss_conv_1 = keras.layers.Conv1D(1, kernel_size=4, activation='softmax', padding='same')(epss_input)
        epss_pool_1 = tf.keras.layers.MaxPooling1D(pool_size=1)(epss_conv_1)
        epss_conv_2 = keras.layers.Conv1D(1, kernel_size=4, activation='softmax', padding='same')(epss_pool_1)
        epss_pool_2 = tf.keras.layers.MaxPooling1D(pool_size=1)(epss_conv_2)
        epss_flatten = keras.layers.Flatten()(epss_pool_2)


        # Branch 3: Process ntpg penetration graph
        ntpg_conv_1 = keras.layers.Conv1D(1, kernel_size=4, activation='softmax', padding='same')(ntpg_input)
        ntpg_pool_1 = tf.keras.layers.MaxPooling1D(pool_size=1)(ntpg_conv_1)
        ntpg_conv_2 = keras.layers.Conv1D(1, kernel_size=4, activation='softmax', padding='same')(ntpg_pool_1)
        ntpg_pool_2 = tf.keras.layers.MaxPooling1D(pool_size=1)(ntpg_conv_2)
        ntpg_flatten = keras.layers.Flatten()(ntpg_pool_2)


        # Concatenate the outputs of all branches
        concatenated = Concatenate()([observable_output, epss_flatten, ntpg_flatten])

        
        # Giu nguyen cac lop nay de cho cac model sau nay
        # Interpreting the concatenated data
        hidden_1 = Dense(self.stateDimension * self.stateDimension, activation='relu')(concatenated)
        hidden_2 = Dense(self.stateDimension * self.stateDimension, activation='relu')(hidden_1)
        hidden_3 = Dense(self.stateDimension, activation='relu')(hidden_2)
        output = Dense(self.actionDimension, activation='softmax')(hidden_3)

        # Create model
        model = Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)

        # Compile model
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics=['accuracy'])
        print("Created network:", model.summary())
        # os.system("pause")
        return model

    ###########################################################################
    #   END - createNetwork function
    ###########################################################################

    ###########################################################################
    #   START - trainingEpisodes function
    #   Status: Faulty Logic (552) - something wrong about the loop (fixed)
    ###########################################################################
    
    def trainingEpisodes(self):

        # Create a list to store step for visualization
        step_visualization = []

        # Create a temporary list to hold the step
        steps = []

        # import ntpg
        ntpg = self.env.get_ntpg()
        htpg = self.env.get_htpg()

        # Extract nodes from the ntpg dictionary
        your_nodes_list = list(ntpg.keys())

        # Extract edges from the ntpg dictionary
        your_edges_list = [(node, edge[0]) for node in ntpg for edge in ntpg[node]]

        # Create a DataFrame to store the data
        data = pd.DataFrame(columns=['attacker_node', 'nifr_nodes', 'nicr_nodes' , 'nodes', 'edges', 'episode'])

        # iterate over the episodes
        for episode in range(self.numberEpisodes):
            
            # reset the environment
            currentState=self.env.reset()

            # list that store rewards in each episode to keep track of convergence
            rewardsEpisode=[]
            
            # reset the step count for the new episode
            step_count = 0

            print("------------------------------------------------------------------------------------------------------------------------")
            print("Simulating episode number: ",episode)
            print("------------------------------------------------------------------------------------------------------------------------")


            while not self.env.is_last():
                          
                # Start the timer
                start_time = time.time()

                print("Current state: ", currentState.observation)
                print("Current state reward: ", currentState.reward)
                # os.system("pause")
                    
                
                action = self.selectAction(currentState.observation.reshape(1, -1), episode)
                print("Action selected: ",action)

                nextState = self.env.step(action)
                steps.append({'attacker_node': self.env._current_attacker_node, 
                              'nifr_nodes': [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nifr_nodes], 
                              'nicr_nodes': [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nicr_nodes],})

                # be careful: reward here have to be the reward of the next state because the reward of the current state is already obtained
                # This result in the reward of, e.g, pre-final state is 0 while in fact the code gonna stop because it find that final state is already the next step
                (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, nextState.reward, self.env.is_last())
                           

                print("------------------- REWARD OF THIS ACTION --------------------------: ",reward)
                rewardsEpisode.append(reward)
                if reward == 1:
                    self.episodeWon += 1

                # increment the step count
                step_count += 1

                # Calculate the time taken for this step and add it to the clock counter
                self.clock_counter += time.time() - start_time

                

                if terminalState:
                    print("Terminal state reached, end episode")
                    break
                    
                if not terminalState:
                    print("Terminal state not reached, continue episode")

                print("Next state: ", nextState)

                # add all the inputs to the replay buffer
                print("TYPE OF CURRENT STATE: ", type(currentState.observation))
                # os.system("pause")
                currentObservation = [currentState.observation, self.epssMatrix, self.connectionMatrix]

                self.replayBuffer.append((np.array(currentState.observation), np.array(self.epssMatrix), np.array(self.connectionMatrix), action, reward, nextStateObservation, terminalState))

                self.trainNetwork()
                
                print("------------------- NETWORKS TRAINED -------------------")

                self.visitCounts = self.visitCounts + 1
                print("Visit counts: ",self.visitCounts)
                 
                currentState=nextState

            # add the step count to the global step counter
            self.step_counter += step_count

            # if episode is a multiple of 50, append step count and calculate dsp
            if episode % 2 == 0:
                self.step_globalcounter.append(self.getStepCount())
                print("episode Won: ", self.episodeWon)
                print("episode: ", episode)
                dsp = self.episodeWon / (episode+1)
                print("Defense Success Probability: ", dsp)
                
                # Add the current clock counter value to the time taken list
                self.time_taken.append(self.clock_counter)
                
                # os.system("pause")
                self.dsp_globalcounter.append(dsp)
                

        print("Sum of rewards {}".format(np.sum(rewardsEpisode)))        
        self.sumRewardsEpisode.append(np.sum(rewardsEpisode)) 


               
    ###########################################################################
    #   END - trainingEpisodes function
    ###########################################################################
    
    ###########################################################################
    #   START - step counting function for calculating dsp
    #   Status: Active
    ###########################################################################
    
    def getStepCount(self):
        return self.step_counter
    
    ###########################################################################
    #   END - step counting function for calculating dsp
    ###########################################################################
    
    ###########################################################################
    #   START - step_globalcounter retrieval function for calculating dsp
    #   Status: Active
    ###########################################################################
    
    def getGlobalStepCount(self):
        return self.step_globalcounter
    
    ###########################################################################
    #   END - step counting function for calculating dsp
    ###########################################################################
    
    ###########################################################################
    #   START - dsp_globalcounter retrieval function for calculating dsp
    #   Status: Active
    ###########################################################################
    
    def getGlobalDSPCount(self):
        return self.dsp_globalcounter
    
    ###########################################################################
    #   END - step counting function for calculating dsp
    ###########################################################################
    
    ###########################################################################
    #   START - time_taken retrieval function for calculating time taken
    #   Status: Active
    ###########################################################################
    
    def getGlobalTimeTaken(self):
        return self.time_taken
    
    ###########################################################################
    #   END - time_taken retrieval function for calculating time taken
    ###########################################################################

    ###########################################################################
    #   START - selectAction & mapping Q-values to action matrix function
    #   Status: Active
    #   https://stackoverflow.com/questions/30821071/how-to-use-numpy-random-choice-in-a-list-of-tuples
    ###########################################################################
    
    def selectAction(self, state, episode):
        
        # Epsilon-greedy approach
        randomValue = np.random.random()
        if episode > 20:
            self.epsilon = 0.999 * self.epsilon
        
        # Exploration phase
        if episode < 3:
            action_space_values = list(self.env.action_space().values())        
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action

        # Exploitation phase
        if randomValue < self.epsilon:
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action

        else:

            # Reshape the state to match the expected input shape
            state = state.reshape(1, -1)

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

            epss_input_reshaped = np.array(epss_input).reshape(-1, self.stateDimension, self.stateDimension)
            ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, self.stateDimension, self.stateDimension)

            # print("EPSS INPUT RESHAPED:", epss_input_reshaped)
            # print("NTPG INPUT RESHAPED:", ntpg_input_reshaped)

            # os.system("pause")

            Qvalues = self.mainNetwork.predict([state, epss_input_reshaped, ntpg_input_reshaped])


            # print("STATE TO PREDICT:", state)
            # Qvalues = self.mainNetwork.predict([np.array(state), np.array(self.epssMatrix), np.array(self.connectionMatrix)])


            # Get the index of the maximum Q-value
            max_index = np.argmax(Qvalues)

            # Map the index to an action matrix
            action_matrix = self.index_to_action(max_index)

            return action_matrix


    def index_to_action(self, index):
        
        action_matrix = self.env.action_space()[index]

        return action_matrix


    '''
    Legacy code from the original code (action matrix K*M)
    
    def index_to_action(self, index):
        # Initialize the action matrix with zeros
        action_matrix = np.zeros((self.env.M, self.env.K), dtype=np.int32)
        # print("action matrix to be indexed:", action_matrix)

        # Convert the index to the corresponding row and column for the action matrix
        for i in range(self.env.M):
            # Calculate the index for the current row
            row_index = index // (self.env.K ** (self.env.M - 1 - i))
            index -= row_index * (self.env.K ** (self.env.M - 1 - i))

            # Set the value in the action matrix
            action_matrix[i, row_index] = 1

        # print("index to action matrix:", action_matrix)
        return action_matrix

            # return action_matrix
    '''

    

    ###########################################################################
    #   END - selectAction function
    ###########################################################################

    ###########################################################################
    #   START - trainNetwork function
    #   07/12/2023 - Start working on this funtion 
    #   Status: Taking too much resource, moving...
    ###########################################################################


    # add nodecount and totalpermutation as input
    # nodecount = number of nodes in the network
    # totalpermutation = number of possible actions in the network


    def trainNetwork(self):
        # print("------------------------------------------------------------------------------------------------------------------------------")  
        # print("---------------------------------------- TRAINING MAIN NETWORK AND TARGET NETWORK---------------------------------------------")
        # print("------------------------------------------------------------------------------------------------------------------------------")

 
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
                    outputNetwork[index] = QcurrentStateMainNetwork[index]
                    outputNetwork[index, action] = y
                
                self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, verbose=0, epochs=200)
                print("Main network trained!")
                
                self.counterUpdateTargetNetwork += 1
                print("Counter value {}".format(self.counterUpdateTargetNetwork))
                if self.counterUpdateTargetNetwork > (self.updateTargetNetworkPeriod - 1):
                    self.targetNetwork.set_weights(self.mainNetwork.get_weights())
                    print("Target network updated!")
                    print("Counter value {}".format(self.counterUpdateTargetNetwork))
                    self.counterUpdateTargetNetwork = 0


    ###########################################################################
    #   END - trainNetwork function
    ###########################################################################

    

    def selectActionEval(self, state, episode, model):
        # print("------------------------------------------------------------------------------------------------------------------------------")
        # print("---------------------------------------- EVALUATING THE TRAINED MAIN NETWORK -------------------------------------------------")
        # print("------------------------------------------------------------------------------------------------------------------------------")

        # Exploration phase
        if episode < 1:
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action

        # Epsilon-greedy approach
        randomValue = np.random.random()
        if episode > 20:
            self.epsilon = 0.999 * self.epsilon

        if randomValue < self.epsilon:
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action

        # Exploitation phase
        else:
            # Reshape the state to match the expected input shape
            state = state.reshape(1, -1)

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

            epss_input_reshaped = np.array(epss_input).reshape(-1, self.stateDimension, self.stateDimension)
            ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, self.stateDimension, self.stateDimension)

            # print("EPSS INPUT RESHAPED:", epss_input_reshaped)
            # print("NTPG INPUT RESHAPED:", ntpg_input_reshaped)

            # os.system("pause")

            Qvalues = self.mainNetwork.predict([state, epss_input_reshaped, ntpg_input_reshaped])


            # print("STATE TO PREDICT:", state)
            # Qvalues = self.mainNetwork.predict([np.array(state), np.array(self.epssMatrix), np.array(self.connectionMatrix)])

            # Get the index of the maximum Q-value
            max_index = np.argmax(Qvalues)
            # print("Action with highest Q-values is", max_index)

            # Map the index to an action matrix
            action_matrix = self.index_to_action(max_index)

            # print("ACTION MATRIX exploit:", action_matrix)
            return action_matrix
        
        
    
    