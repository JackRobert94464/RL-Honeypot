print("------------------------------------------------------------------------------------------------------------------------")   
print("------------------------------------------------------------------------------------------------------------------------")
print("------------------------------------------------------------------------------------------------------------------------")
print("------------------------------------------------------------------------------------------------------------------------")
print("---------------------------------------  TRAINING THE AGENT BASED ON THE ENV -------------------------------------------")
print("------------------------------------------------------------------------------------------------------------------------")   
print("------------------------------------------------------------------------------------------------------------------------")
print("------------------------------------------------------------------------------------------------------------------------")
print("------------------------------------------------------------------------------------------------------------------------")






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

import pandas as pd
 
from visualizer import visualize_steps_manual

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

        print(env)

        # DIMENSION INITIALIZATION

        # state dimension 
        self.stateDimension = env.K
        print("STATE DIMENSION --- AGENT TRAINING",self.stateDimension)
        
        # action dimension k!/(k-m)! (07/12/2023 - different permutation problem)
        self.actionDimension = factorial(env.K) / factorial(env.K - env.M)
        print("ACTION DIMENSION --- AGENT TRAINING",self.actionDimension)

        # epss dimension
        # epss = ma tran EPSS size K*K 
        # => tinh trung binh epss cua tung canh => tao ma tran nxn => tai moi vi tri (k, l) cua ma tran => epss(k, l) = trung binh epss cua canh (k, l)
        self.epssDimension = env.K * env.K
        print("EPSS DIMENSION --- AGENT TRAINING",self.epssDimension)

        # ntpg dimension
        # ntpg = ma tran ntpg size K*K
        # => tao ma tran nxn => tai moi vi tri (k, l) cua ma tran => ntpg(k, l) = 1 neu co canh tu k den l, nguoc lai = 0
        self.ntpgDimension = env.K * env.K
        print("NTPG DIMENSION --- AGENT TRAINING",self.ntpgDimension)


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

        # replay buffer
        self.replayBuffer=deque(maxlen=self.replayBufferSize)

        # initialize visit(s,a)
        self.visitCounts = 0

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
        print("LOSS FUNCTION - Y_TRUE:", y_true)
        s1, s2 = y_true.shape
        print("LOSS FUNCTION - S1 AND S2:", s1, s2)
        print("LOSS FUNCTION - ACTIONS APPEND:", actionsAppend)

        # count the amount of actions in actionsAppend
        countact = len(actionsAppend)
        print("LOSS FUNCTION - COUNTACT:", countact)


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
        data = pd.DataFrame(columns=['steps', 'nodes', 'edges', 'episode'])


        # iterate over the episodes
        for episode in range(self.numberEpisodes):
            
            # self.env = NetworkHoneypotEnv(10, 3, 7, ntpg, htpg)
            # reset the environment
            currentState=self.env.reset()

            # list that store rewards in each episode to keep track of convergence
            rewardsEpisode=[]

            print("------------------------------------------------------------------------------------------------------------------------")
            print("Simulating episode number: ",episode)
            print("------------------------------------------------------------------------------------------------------------------------")

            # reset the environment
            # in other words, s=s0
            # reset = self.env.reset()
            # print("Resetting the environment", reset)
            

            print("Current state: ", currentState.observation)


            # here we step from one state to another
            # in other words, s=s0, s=s1, s=s2, ..., s=sn
            # until either nicr or nifr got attacked, sum up the state and get reward
            # stateCount = 100
            # This part logic is faulty - the attacker attack with each step, and we need to stop him on each step till he reach
            # final state, not just doing K loop
            # 20/12/2023 - Replacing for K loop whatever with indefinite while (until nicr or nifr got hit)
            while not self.env.is_last():
                # Your code here
                
                #print("while looping through all the K nodes after stateCount times to check if nicr or nifr got attacked") 
                print("Patroling until either nicr or nifr got attacked - end episode")

                # select the action based on the epsilon-greedy approach

                # Fix this to change the state to not only the observation but additional epss and ntpg matrices - 27/03/2024

                print("observed state: ",currentState.observation)
                action = self.selectAction(currentState.observation.reshape(1, -1), episode)
                print("Action selected: ",action)
                print("self.env.step based on action: ",self.env.step(action))

                # here we step and return the state, reward, and boolean denoting if the state is a terminal state
                # (terminalState, discount, reward, nextState) = self.env.step(action)
                nextState = self.env.step(action)
                print("attacker node for drawing: ", self.env._current_attacker_node)
                print("nifr nodes for drawing: ", self.env.nifr_nodes)
                print("ntpg ip of the nifr nodes: ", [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nifr_nodes])
                print("nicr nodes for drawing: ", self.env.nicr_nodes)
                print("ntpg ip of the nicr node: ", [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nicr_nodes])
                # os.system("pause")
                steps.append({'attacker_node': self.env._current_attacker_node, 
                              'nifr_nodes': [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nifr_nodes], 
                              'nicr_nodes': [list(self.env._ntpg.keys())[node_index-1] for node_index in self.env.nicr_nodes],})


                # Basically we just assign the result after we step to a variable called nextState
                # Then we seperate the variable (which is a TimeStep object) to 4 part of it: step_type, reward, discount, and observation
                (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, currentState.reward, currentState.is_last())
                # This part probably need to fix
                print("parameters of environment:")
                print((discount, nextStateObservation, reward, terminalState))

            
        
                print("------------------- REWARD OF THIS ACTION --------------------------: ",reward)
                # os.system("pause")
                rewardsEpisode.append(reward)


                if terminalState:
                    print("Terminal state reached, end episode")
                    break
                    
                if not terminalState:
                    print("Terminal state not reached, continue episode")

                print("Next state: ", nextState)


                # add current state, action, reward, next state, and terminal flag to the replay buffer
                # print("Next state observation array: ", nextState)
                self.replayBuffer.append((currentState.observation, action, reward, nextStateObservation, terminalState))
                print("Replay buffer: ",self.replayBuffer)

                # train network
                self.trainNetwork()
                print("------------------- NETWORKS TRAINED -------------------")

                # visiting next node in the network
                self.visitCounts = self.visitCounts + 1
                print("Visit counts: ",self.visitCounts)
                 
                # set the current state for the next step s <- s'
                currentState=nextState
                print("Current state after step: ", currentState)

                # stateCount = stateCount + 1

            # Visualize the steps
            print("Your edges list: ", your_edges_list)
            # import os
            # os.system("pause")
            # print("steps: ", steps)
            # import os
            # os.system("pause")
            # visualize_steps_manual(steps, your_nodes_list, your_edges_list, 'images', 'movie.gif', episode)

            # Append the data to the DataFrame
            # data = data.append({'steps': steps, 'nodes': your_nodes_list, 'edges': your_edges_list, 'episode': episode}, ignore_index=True)
            

            print("------------------------- END LOOP HERE -------------------------")


        # Save the DataFrame to a CSV file
        data.to_csv('sim_graph.csv', index=False)


        # tbh i dont even know if summing reward here is neccessary
        print("Sum of rewards {}".format(np.sum(rewardsEpisode)))        
        self.sumRewardsEpisode.append(np.sum(rewardsEpisode)) 
               
    ###########################################################################
    #   END - trainingEpisodes function
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
                print("Deploying honeypot number", i, "in normal nodes:", action)
            action = action.astype(np.int32)
            print("ACTION MATRIX exploit:", action)
            return action

        # Exploitation phase
        if randomValue < self.epsilon:
            action = np.zeros((self.env.M, self.env.K))
            for i in range(self.env.M):
                action[i, np.random.randint(0, self.env.K)] = 1
                print("Deploying honeypot number", i, "in normal nodes:", action)
            action = action.astype(np.int32)
            print("ACTION MATRIX exploit:", action)
            return action

        else:
            print("STATE TO PREDICT:", state)
            Qvalues = self.mainNetwork.predict(state)
            print("QVALUES:", Qvalues)

            # Get the index of the maximum Q-value
            max_index = np.argmax(Qvalues)
            print("action with the highest Q-value:", max_index)

            # Map the index to an action matrix
            action_matrix = self.index_to_action(max_index)

            print("ACTION MATRIX exploit:", action_matrix)
            return action_matrix

    def index_to_action(self, index):
        # Initialize the action matrix with zeros
        action_matrix = np.zeros((self.env.M, self.env.K), dtype=np.int32)
        print("action matrix to be indexed:", action_matrix)

        # Convert the index to the corresponding row and column for the action matrix
        for i in range(self.env.M):
            # Calculate the index for the current row
            row_index = index // (self.env.K ** (self.env.M - 1 - i))
            index -= row_index * (self.env.K ** (self.env.M - 1 - i))

            # Set the value in the action matrix
            action_matrix[i, row_index] = 1

        print("index to action matrix:", action_matrix)
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
        print("------------------------------------------------------------------------------------------------------------------------------")  
        print("---------------------------------------- TRAINING MAIN NETWORK AND TARGET NETWORK---------------------------------------------")
        print("------------------------------------------------------------------------------------------------------------------------------")

 
        # if the replay buffer has at least batchReplayBufferSize elements,
        # then train the model 
        # otherwise wait until the size of the elements exceeds batchReplayBufferSize
        if (len(self.replayBuffer)>self.batchReplayBufferSize):
             
 
            # sample a batch from the replay buffer
            randomSampleBatch=random.sample(self.replayBuffer, self.batchReplayBufferSize)
            print("Random sample batch chosen: ",randomSampleBatch)
             
            # here we form current state batch 
            # and next state batch
            # they are used as inputs for prediction
            currentStateBatch=np.zeros(shape=(self.batchReplayBufferSize,self.nodecount))
            print("Current state batch: ",currentStateBatch)

            nextStateBatch=np.zeros(shape=(self.batchReplayBufferSize,self.nodecount))      
            print("Next state batch: ",nextStateBatch)      
            # this will enumerate the tuple entries of the randomSampleBatch
            # index will loop through the number of tuples
            for index,tupleS in enumerate(randomSampleBatch):
                print("Sample batch no. ",index)
                print("Current state of sample batch: ",tupleS[0])
                # first entry of the tuple is the current state
                currentStateBatch[index,:]=tupleS[0]

                # fourth entry of the tuple is the next state
                print("Next state of sample batch: ",tupleS[3])
                nextStateBatch[index,:]=tupleS[3]
             
            # here, use the target network to predict Q-values 
            QnextStateTargetNetwork=self.targetNetwork.predict(nextStateBatch)
            print("QnextStateTargetNetwork: ",QnextStateTargetNetwork)
            # here, use the main network to predict Q-values 
            QcurrentStateMainNetwork=self.mainNetwork.predict(currentStateBatch)
            print("QcurrentStateMainNetwork: ",QcurrentStateMainNetwork)
             
            # now, we form batches for training
            # input for training
            inputNetwork=currentStateBatch
            print("Input network: ",inputNetwork)
            # output for training
            outputNetwork=np.zeros(shape=(self.batchReplayBufferSize,int(self.totalpermutation)))
            print("Output network: ",outputNetwork)
             
            # this list will contain the actions that are selected from the batch 
            # this list is used in my_loss_fn to define the loss-function
            # self.actionsAppend=[]            
            for index,(currentState,action,reward,nextState,terminated) in enumerate(randomSampleBatch):
                 
                # if the next state is the terminal state
                if terminated:
                    print("Next state is the terminal state")
                    print("y: ",reward)
                    y=reward                  
                # if the next state if not the terminal state    
                else:
                    print("Next state is not the terminal state")
                    print("y: ",reward+self.gamma*np.max(QnextStateTargetNetwork[index]))
                    y=reward+self.gamma*np.max(QnextStateTargetNetwork[index])
                 
                # this is necessary for defining the cost function
                actionsAppend.append(action)
                print("Actions after append: ",actionsAppend)
                 
                # this actually does not matter since we do not use all the entries in the cost function
                outputNetwork[index]=QcurrentStateMainNetwork[index]
                print("Output network index: ",outputNetwork)
                # this is what matters
                outputNetwork[index,action]=y
                print("Output network: ",outputNetwork)
             
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
                print("Counter value {}".format(self.counterUpdateTargetNetwork))
                # reset the counter
                self.counterUpdateTargetNetwork=0

    ###########################################################################
    #   END - trainNetwork function
    ###########################################################################

    

    def selectActionEval(self, state, episode, model):
        print("------------------------------------------------------------------------------------------------------------------------------")
        print("---------------------------------------- EVALUATING THE TRAINED MAIN NETWORK -------------------------------------------------")
        print("------------------------------------------------------------------------------------------------------------------------------")

        # Exploration phase
        if episode < 1:
            action = np.zeros((self.env.M, self.env.K))
            for i in range(self.env.M):
                action[i, np.random.randint(0, self.env.K)] = 1
                print("Deploying honeypot number", i, "in normal nodes:", action)
            action = action.astype(np.int32)
            print("ACTION MATRIX exploit:", action)
            return action

        # Epsilon-greedy approach
        randomValue = np.random.random()
        if episode > 200:
            self.epsilon = 0.999 * self.epsilon

            if randomValue < self.epsilon:
                action = np.zeros((self.env.M, self.env.K))
                for i in range(self.env.M):
                    action[i, np.random.randint(0, self.env.K)] = 1
                    print("Deploying honeypot number", i, "in normal nodes:", action)
                action = action.astype(np.int32)
                print("ACTION MATRIX exploit:", action)
                return action

        # Exploitation phase
        else:
            print("STATE TO PREDICT:", state)
            Qvalues = model.predict(state)
            print("QVALUES:", Qvalues)

            # Get the index of the maximum Q-value
            max_index = np.argmax(Qvalues)
            print("Action with highest Q-values is", max_index)

            # Map the index to an action matrix
            action_matrix = self.index_to_action(max_index)

            print("ACTION MATRIX exploit:", action_matrix)
            return action_matrix