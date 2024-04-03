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
from keras.layers import Dense
from keras.layers import InputLayer
from keras.models import Sequential

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
 
from visualizer import visualize_steps

import pandas as pd

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

        # state dimension 
        self.stateDimension = env.K
        # print("STATE DIMENSION --- AGENT TRAINING",self.stateDimension)
        # action dimension k!/(k-m)! (07/12/2023 - different permutation problem)
        self.actionDimension = factorial(env.K) / factorial(env.K - env.M)
        # print("ACTION DIMENSION --- AGENT TRAINING",self.actionDimension)
        # this is the maximum size of the replay buffer
        self.replayBufferSize=80
        # this is the size of the training batch that is randomly sampled from the replay buffer
        self.batchReplayBufferSize=20

        # number of training episodes it takes to update the target network parameters
        # that is, every updateTargetNetworkPeriod we update the target network parameters
        self.updateTargetNetworkPeriod=5

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

        # this list is used in the cost function to select certain entries of the 
        # predicted and true sample matrices in order to form the loss
        # self.actionsAppend=[]

        # this is the main network
        # create network
        self.mainNetwork=self.createNetwork()

        # this is the target network
        # create network
        self.targetNetwork=self.createNetwork()

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
    
    def createNetwork(self):
        # create a neural network with two hidden layers of 100 units each and ReLU activation (must fix!)
        # the final layer is a dense layer with k!/(k-m)! units, one for each possible deployment combination
        model = Sequential()

        model.add(InputLayer(input_shape=self.stateDimension))

        #lmao
        model.add(Dense(64, activation='relu'))
        # model.add(Dense(128, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.actionDimension, activation='linear'))
        
        # use mean squared error as the loss function
        # original used a custom loss one, but for this case im not sure
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics = ['accuracy'])
        print("Created network:", model.summary())
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

                if terminalState:
                    print("Terminal state reached, end episode")
                    break
                    
                if not terminalState:
                    print("Terminal state not reached, continue episode")

                print("Next state: ", nextState)

                self.replayBuffer.append((currentState.observation, action, reward, nextStateObservation, terminalState))

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
    #   START - selectAction & mapping Q-values to action matrix function
    #   Status: Active
    ###########################################################################
    
    def selectAction(self, state, episode):
        
        # Epsilon-greedy approach
        randomValue = np.random.random()
        if episode > 20:
            self.epsilon = 0.999 * self.epsilon
        
        # Exploration phase
        if episode < 3:
            action = np.zeros((self.env.M, self.env.K))
            for i in range(self.env.M):
                action[i, np.random.randint(0, self.env.K)] = 1
                # print("Deploying honeypot number", i, "in normal nodes:", action)
            action = action.astype(np.int32)
            # print("ACTION MATRIX exploit:", action)
            return action

        # Exploitation phase
        if randomValue < self.epsilon:
            action = np.zeros((self.env.M, self.env.K))
            for i in range(self.env.M):
                action[i, np.random.randint(0, self.env.K)] = 1
                # print("Deploying honeypot number", i, "in normal nodes:", action)
            action = action.astype(np.int32)
            # print("ACTION MATRIX exploit:", action)
            return action

        else:
            # print("STATE TO PREDICT:", state)
            Qvalues = self.mainNetwork.predict(state)
            # print("QVALUES:", Qvalues)

            # Get the index of the maximum Q-value
            max_index = np.argmax(Qvalues)
            # print("action with the highest Q-value:", max_index)

            # Map the index to an action matrix
            action_matrix = self.index_to_action(max_index)

            # print("ACTION MATRIX exploit:", action_matrix)
            return action_matrix

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

 
        # if the replay buffer has at least batchReplayBufferSize elements,
        # then train the model 
        # otherwise wait until the size of the elements exceeds batchReplayBufferSize
        if (len(self.replayBuffer)>self.batchReplayBufferSize):
             
 
            # sample a batch from the replay buffer
            randomSampleBatch=random.sample(self.replayBuffer, self.batchReplayBufferSize)
            # print("Random sample batch chosen: ",randomSampleBatch)
             
            # here we form current state batch 
            # and next state batch
            # they are used as inputs for prediction
            currentStateBatch=np.zeros(shape=(self.batchReplayBufferSize,self.nodecount))
            # print("Current state batch: ",currentStateBatch)

            nextStateBatch=np.zeros(shape=(self.batchReplayBufferSize,self.nodecount))      
            # print("Next state batch: ",nextStateBatch)      
            # this will enumerate the tuple entries of the randomSampleBatch
            # index will loop through the number of tuples
            for index,tupleS in enumerate(randomSampleBatch):
                # print("Sample batch no. ",index)
                # print("Current state of sample batch: ",tupleS[0])
                # first entry of the tuple is the current state
                currentStateBatch[index,:]=tupleS[0]

                # fourth entry of the tuple is the next state
                # print("Next state of sample batch: ",tupleS[3])
                nextStateBatch[index,:]=tupleS[3]
             
            # here, use the target network to predict Q-values 
            QnextStateTargetNetwork=self.targetNetwork.predict(nextStateBatch)
            # print("QnextStateTargetNetwork: ",QnextStateTargetNetwork)
            # here, use the main network to predict Q-values 
            QcurrentStateMainNetwork=self.mainNetwork.predict(currentStateBatch)
            # print("QcurrentStateMainNetwork: ",QcurrentStateMainNetwork)
             
            # now, we form batches for training
            # input for training
            inputNetwork=currentStateBatch
            # print("Input network: ",inputNetwork)
            # output for training
            outputNetwork=np.zeros(shape=(self.batchReplayBufferSize,int(self.totalpermutation)))
            # print("Output network: ",outputNetwork)
             
            # this list will contain the actions that are selected from the batch 
            # this list is used in my_loss_fn to define the loss-function
            # self.actionsAppend=[]            
            for index,(currentState,action,reward,nextState,terminated) in enumerate(randomSampleBatch):
                 
                # if the next state is the terminal state
                if terminated:
                    # print("Next state is the terminal state")
                    # print("y: ",reward)
                    y=reward                  
                # if the next state if not the terminal state    
                else:
                    # print("Next state is not the terminal state")
                    # print("y: ",reward+self.gamma*np.max(QnextStateTargetNetwork[index]))
                    y=reward+self.gamma*np.max(QnextStateTargetNetwork[index])
                 
                # this is necessary for defining the cost function
                actionsAppend.append(action)
                # print("Actions after append: ",actionsAppend)
                 
                # this actually does not matter since we do not use all the entries in the cost function
                outputNetwork[index]=QcurrentStateMainNetwork[index]
                # print("Output network index: ",outputNetwork)
                # this is what matters
                outputNetwork[index,action]=y
                # print("Output network: ",outputNetwork)
             
            # here, we train the network
            self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size = self.batchReplayBufferSize, verbose=0, epochs=100)
            print("Main network trained!")
             
            # after updateTargetNetworkPeriod training sessions, update the coefficients 
            # of the target network
            # increase the counter for training the target network
            self.counterUpdateTargetNetwork+=1 
            print("Counter value {}".format(self.counterUpdateTargetNetwork))
            if (self.counterUpdateTargetNetwork>(self.updateTargetNetworkPeriod-1)):
                # copy the weights to targetNetwork
                self.targetNetwork.set_weights(self.mainNetwork.get_weights())        
                print("Target network updated!")
                # os.system("pause")
                print("Counter value {}".format(self.counterUpdateTargetNetwork))
                # reset the counter
                self.counterUpdateTargetNetwork=0

    ###########################################################################
    #   END - trainNetwork function
    ###########################################################################

    

    def selectActionEval(self, state, episode, model):
        # print("------------------------------------------------------------------------------------------------------------------------------")
        # print("---------------------------------------- EVALUATING THE TRAINED MAIN NETWORK -------------------------------------------------")
        # print("------------------------------------------------------------------------------------------------------------------------------")

        # Exploration phase
        if episode < 1:
            action = np.zeros((self.env.M, self.env.K))
            for i in range(self.env.M):
                action[i, np.random.randint(0, self.env.K)] = 1
                # print("Deploying honeypot number", i, "in normal nodes:", action)
            action = action.astype(np.int32)
            # print("ACTION MATRIX exploit:", action)
            return action

        # Epsilon-greedy approach
        randomValue = np.random.random()
        if episode > 20:
            self.epsilon = 0.999 * self.epsilon

            if randomValue < self.epsilon:
                action = np.zeros((self.env.M, self.env.K))
                for i in range(self.env.M):
                    action[i, np.random.randint(0, self.env.K)] = 1
                    # print("Deploying honeypot number", i, "in normal nodes:", action)
                action = action.astype(np.int32)
                # print("ACTION MATRIX exploit:", action)
                return action

        # Exploitation phase
        else:
            # print("STATE TO PREDICT:", state)
            Qvalues = model.predict(state)
            # print("QVALUES:", Qvalues)

            # Get the index of the maximum Q-value
            max_index = np.argmax(Qvalues)
            # print("Action with highest Q-values is", max_index)

            # Map the index to an action matrix
            action_matrix = self.index_to_action(max_index)

            # print("ACTION MATRIX exploit:", action_matrix)
            return action_matrix