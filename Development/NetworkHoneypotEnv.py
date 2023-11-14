import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.environments import suite_gym
from tf_agents.trajectories import time_step as ts

import gym
from gym import spaces
import numpy as np


# Outline the Environment:
# Preliminary
# Both the attacker 
# State
# - The state space is now a 2-dimensional vector of 0s and 1s, where 1s represent the attacked nodes as reported by NMS
# Action
# - The action space is the number of deception resources available to the defender (m) multiply with the number of normal nodes (k)
# - The vector with the size of m*k will also be a a vector of 0s and 1s, represent if the defender deploy the deception resource or not (yes 1 no 0)
# Reward
# - with each step in an episode:
#   - if the attacker is in the fake node, reward = 1, terminate the episode
#   - if the attacker is in the nicr node, reward = -1, terminate the episode
#   - if the attacker is in the normal node, reward = 0 and continue the episode



class NetworkHoneypotEnv(py_environment.PyEnvironment):  # Inherit from gym.Env
    def __init__(self, N, M, K, P, Q):

        # Initialize the spec for the environment
        self.N = N # Total amount of nodes (n)
        self.M = M # Number of deception nodes (m)
        self.K = K # Number of normal nodes (k)
        self.P = P # Probability of attacker moving to the next node
        self.Q = Q # Probability of attacker moving to a random node

        # Pick a random node to be the nicr (important resource node)
        # As an example to test the environment, uncomment this for nicr hard-coded
        # self.nifr_nodes = [6]
        self.nicr_nodes = [np.random.choice(N)]

        # Initialize an empty list for the nifr (fake resource node)
        # As an example to test the environment, uncomment this for nifr hard-coded
        # self.nifr_nodes = [2,3,5]
        self.nifr_nodes = []

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(M,K), dtype=np.int32, minimum=0, maximum=1, name='action')
        
        # Add the observation spec for the state vector
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(1,N), dtype=np.int32, minimum=0, maximum=1, name='observation')
        
        # Initialize the state vector as a random vector of 0s and 1s
        self._state = np.random.randint(0, 2, size=(N,))
        
        # Initialize the matrix for the defender's view as zeros
        self._matrix = np.zeros((M, K), dtype=np.int32)
        
        # Initialize the dictionary for the NTPG as an empty dictionary
        self._ntpg = {}
        
        # Initialize the dictionary for the HTPG as an empty dictionary
        self._htpg = {}
        
        self._episode_ended = False
        
        # Add some code to generate the NTPG and HTPG based on some logic or data
        # For example, you can use a loop to iterate over the nodes and add edges randomly
        # Or you can use some existing library or tool to generate the graphs
        # Or you can hard-code the graphs based on some predefined structure
        # Here I will just use a simple loop and random numbers as an example
        
        # 29/10/2023 - Fixed example is provided as follow, i will include image of the sample graph
        self._ntpg = {'192.168.0.2': [ ('192.168.0.3', 0.8,0.6),('192.168.0.3', 0.8,0.6)], 
                      '192.168.0.3': [ ('192.168.0.5', 0.5,0.1)], 
                      '192.168.0.4': [('192.168.0.5', 0.8,0.2),('192.168.0.6', 0.4,0.2),('192.168.0.7', 0.3,0.1),], 
                      '192.168.0.5': [('192.168.0.8', 0.2,0.1),('192.168.0.7', 0.6,0.3)],
                      '192.168.0.6': [],
                      '192.168.0.7': [('192.168.0.8', 0.2,0.9)],
                      '192.168.0.8': [],}


        self._htpg = {'192.168.0.2': [('NetBT', 'CVE-2017-0161', 0.6, ('192.168.0.4', 'User')),
                                      ('Win32k', 'CVE-2018-8120', 0.04, ('192.168.0.4', 'Root')),
                                      ('VBScript', 'CVE-2018-8174', 0.5, ('192.168.0.4', 'Root')),
                                      ('Apache', 'CVE-2017-9798', 0.8, ('192.168.0.3', 'User')),
                                      ('Apache', 'CVE-2014-0226', 0.6, ('192.168.0.3', 'Root')),], 
                      '192.168.0.3': [('Apache', 'CVE-2017-9798', 0.5, ('192.168.0.5', 'User')),
                                      ('Apache', 'CVE-2014-0226', 0.1, ('192.168.0.5', 'Root')),], 
                      '192.168.0.4': [('NetBT', 'CVE-2017-0161', 0.8, ('192.168.0.5', 'User')),
                                      ('Win32k', 'CVE-2018-8120', 0.02, ('192.168.0.5', 'Root')),
                                      ('VBScript', 'CVE-2018-8174', 0.2, ('192.168.0.5', 'Root')),
                                      ('OJVM', 'CVE-2016-5555', 0.4, ('192.168.0.6', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.2, ('192.168.0.6', 'Root')),
                                      ('HFS', 'CVE-2014-6287', 0.3, ('192.168.0.7', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.7', 'Root')),], 
                      '192.168.0.5': [('HFS', 'CVE-2014-6287', 0.6, ('192.168.0.7', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.3, ('192.168.0.7', 'Root')),
                                      ('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root')),],
                      '192.168.0.6': [],
                      '192.168.0.7': [('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root'))],
                      '192.168.0.8': [],
        }
        

        print("State vector:", self._state)
        print("Matrix:", self._matrix)
        print("NTPG:", self._ntpg)
        print("HTPG:", self._htpg)


    def action_spec(self):
        return self._action_spec
    
    def observation_spec(self):
        return self._observation_spec
    

    def _reset(self):

        # Reset the nicr node by random choosing a new one
        self.nicr_nodes = [np.random.choice(self.N)]

        # Reset list for the nifr (fake resource node)
        self.nifr_nodes = []

        # Reset the state vector as a random vector of 0s and 1s
        self._state = np.random.randint(0, 2, size=(self.N,))
        
        # Reset the matrix for the defender's view as zeros
        self._matrix = np.zeros((self.M, self.K), dtype=np.int32)
        
        # Reset the dictionary for the NTPG as an empty dictionary
        self._ntpg = {}
        
        # Reset the dictionary for the HTPG as an empty dictionary
        self._htpg = {}
        
        # Reset the episode ended flag as False
        self._episode_ended = False
            
        # Regenerate the NTPG and HTPG based on some logic or data
        # Here I will use the same code as in the __init__ function (12/11/2023 - reset to fixed example)
        self._ntpg = {'192.168.0.2': [ ('192.168.0.3', 0.8,0.6),('192.168.0.3', 0.8,0.6)], 
                      '192.168.0.3': [ ('192.168.0.5', 0.5,0.1)], 
                      '192.168.0.4': [('192.168.0.5', 0.8,0.2),('192.168.0.6', 0.4,0.2),('192.168.0.7', 0.3,0.1),], 
                      '192.168.0.5': [('192.168.0.8', 0.2,0.1),('192.168.0.7', 0.6,0.3)],
                      '192.168.0.6': [],
                      '192.168.0.7': [('192.168.0.8', 0.2,0.9)],
                      '192.168.0.8': [],}


        self._htpg = {'192.168.0.2': [('NetBT', 'CVE-2017-0161', 0.6, ('192.168.0.4', 'User')),
                                      ('Win32k', 'CVE-2018-8120', 0.04, ('192.168.0.4', 'Root')),
                                      ('VBScript', 'CVE-2018-8174', 0.5, ('192.168.0.4', 'Root')),
                                      ('Apache', 'CVE-2017-9798', 0.8, ('192.168.0.3', 'User')),
                                      ('Apache', 'CVE-2014-0226', 0.6, ('192.168.0.3', 'Root')),], 
                      '192.168.0.3': [('Apache', 'CVE-2017-9798', 0.5, ('192.168.0.5', 'User')),
                                      ('Apache', 'CVE-2014-0226', 0.1, ('192.168.0.5', 'Root')),], 
                      '192.168.0.4': [('NetBT', 'CVE-2017-0161', 0.8, ('192.168.0.5', 'User')),
                                      ('Win32k', 'CVE-2018-8120', 0.02, ('192.168.0.5', 'Root')),
                                      ('VBScript', 'CVE-2018-8174', 0.2, ('192.168.0.5', 'Root')),
                                      ('OJVM', 'CVE-2016-5555', 0.4, ('192.168.0.6', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.2, ('192.168.0.6', 'Root')),
                                      ('HFS', 'CVE-2014-6287', 0.3, ('192.168.0.7', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.7', 'Root')),], 
                      '192.168.0.5': [('HFS', 'CVE-2014-6287', 0.6, ('192.168.0.7', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.3, ('192.168.0.7', 'Root')),
                                      ('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root')),],
                      '192.168.0.6': [],
                      '192.168.0.7': [('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root'))],
                      '192.168.0.8': [],
        }

        
        # Return the state of the environment and information that it is the first step of the simulation
        return ts.restart(np.array([self._state], dtype=np.int32))
        
    
    def __is_action_valid(self, action):
        # Check if the action is a valid matrix of size m*k with values 0 or 1
        # Return True if the action is valid, False otherwise
        
        # Check if the action has the correct shape
        if action.shape != (self.M, self.K):
            return False
        
        # Check if the action has the correct type
        if action.dtype != np.int32:
            return False
        
        # Check if the action has the correct values
        if not np.all(np.isin(action, [0, 1])):
            return False
        
        # If all checks pass, return True
        return True


    def __attacker_move(self):
        """Simulates the attacker's move based on the NTPG and HTPG.
        Updates the state vector with the new attacked node.
        """

        # Choose a random node based on the NTPG
        current_node = np.random.choice(list(self._ntpg.keys()))

        # Attack the current node with a probability based on the HTPG
        if np.random.random() <= self._htpg[current_node][0][2]:
            self._state[current_node] = 1

        # Update the NIFR list based on the action matrix
        self.__update_nifr_nodes(self.nifr_nodes)




    def __is_nicr_attacked(self, nicr_nodes):
        # Check if any nicr (important resource node) is attacked or not
        # Return True if any nicr is attacked, False otherwise
        
        # Check if any nicr node is attacked in the state vector
        for i in nicr_nodes:
            if self._state[i] == 1:
                return True
        
        # If no nicr node is attacked, return False
        return False

    def __is_nifr_attacked(self, nifr_nodes):
        # Check if any fake resource node is attacked or not
        # Return True if any fake resource node is attacked, False otherwise

        # Check if any nicr node is attacked in the state vector
        for i in nifr_nodes:
            if self._state[i] == 1:
                return True
        
        # If no nicr node is attacked, return False
        return False
    
    def is_last(self):
        # Check if the episode has ended
        # Return True if the episode has ended, False otherwise
        
        # Check if the episode ended flag is True
        if self._episode_ended:
            return True
        
        # If no, return False
        return False

    # Updates the NIFR list based on the action matrix.
    def __update_nifr_nodes(self, nifr_nodes):
        for row in self._matrix:
            if any(row):
                self.nifr_nodes.append(row.argmax())
    
    def _step(self, action):
        # Check if the episode has ended
        if self._episode_ended:
            # If yes, reset the environment and return the initial state
            return self.reset()
        
        # Check if the action is valid
        if self.__is_action_valid(action):
            # If yes, update the matrix for the defender's view with the action
            self._matrix = action

            # Update the NIFR list based on the action matrix.
            self.__update_nifr_nodes(self.nifr_nodes)
            
            # Simulate the attacker's move based on the NTPG and HTPG
            self.__attacker_move()
            
            # Check if the attacker has reached a nicr or a fake resource node
            if self.__is_nicr_attacked(self.nicr_nodes) or self.__is_nifr_attacked(self.nifr_nodes):
                # If yes, end the episode and return the termination state and reward
                self._episode_ended = True
                reward = 1 if self.__is_nifr_attacked(self.nifr_nodes) else -1
                return ts.termination(np.array([self._state], dtype=np.int32), reward)
            else:
                # If no, continue the episode and return the transition state and reward
                return ts.transition(np.array([self._state], dtype=np.int32), reward=0, discount=1.0)
        
        else:
            # If no, end the episode and return the termination state and reward
            self._episode_ended = True
            return ts.termination(np.array([self._state], dtype=np.int32), -1)
        
          
# environment = NetworkHoneypotEnv()
# utils.validate_py_environment(environment, episodes=2)


















####################################################################################
# This is the code for the DQN agent
# I will use the same code from the TF-Agents tutorial
####################################################################################

# import the necessary libraries
import numpy as np
import random
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import RMSprop
from collections import deque 
from tensorflow import gather_nd
from tensorflow.keras.losses import mean_squared_error 
 


# Outline the difference from cartpole:
# Policy
# - The policy is a function that maps states to actions.
# - The policy is represented by a neural network that takes the state as input and outputs the action.
# - The policy is trained by the agent to maximize the total reward.
# - Here, we use a neural network with two hidden layers of 100 units each and ReLU activation.
# - The final layer is a dense layer with 2 units, one for each possible action in the deception network environment.

# hình như thầy bảo cố định lại 1 cái môi trường HTPG NTPG


class DoubleDeepQLearning:
    
    ###########################################################################
    #   START - __init__ function
    ###########################################################################
    # INPUTS: 
    # env - Training network environment
    # gamma - discount rate
    # epsilon - parameter for epsilon-greedy approach
    # numberEpisodes - total number of simulation episodes
    
      
    def __init__(self,env,gamma,epsilon,numberEpisodes):
      self.env=env
      self.gamma=gamma
      self.epsilon=epsilon
      self.numberEpisodes=numberEpisodes
      
      # self.n = "total number of nodes"
      # self.m = "number of deception resource available"
      # self.k = "number of normal nodes"

      print(env)

      # state dimension 
      self.stateDimension = env.N
      print("STATE DIMENSION --- AGENT TRAINING",self.stateDimension)
      # action dimension
      self.actionDimension = env.M * env.K
      print("ACTION DIMENSION --- AGENT TRAINING",self.actionDimension)
      # this is the maximum size of the replay buffer
      self.replayBufferSize=300
      # this is the size of the training batch that is randomly sampled from the replay buffer
      self.batchReplayBufferSize=100
        
      # number of training episodes it takes to update the target network parameters
      # that is, every updateTargetNetworkPeriod we update the target network parameters
      self.updateTargetNetworkPeriod=100
        
      # this is the counter for updating the target network 
      # if this counter exceeds (updateTargetNetworkPeriod-1) we update the network 
      # parameters and reset the counter to zero, this process is repeated until the end of the training process
      self.counterUpdateTargetNetwork=0
        
      # this sum is used to store the sum of rewards obtained during each training episode
      self.sumRewardsEpisode=[]
        
      # replay buffer
      self.replayBuffer=deque(maxlen=self.replayBufferSize)
        
      # this is the main network
      # create network
      self.mainNetwork=self.createNetwork()
        
      # this is the target network
      # create network
      self.targetNetwork=self.createNetwork()
        
      # copy the initial weights to targetNetwork
      self.targetNetwork.set_weights(self.mainNetwork.get_weights())
        
      # this list is used in the cost function to select certain entries of the 
      # predicted and true sample matrices in order to form the loss
      self.actionsAppend=[]
     
    ###########################################################################
    #   END - __init__ function
    ###########################################################################
     
    ###########################################################################
    # START - function for defining the loss (cost) function
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
     
    def my_loss_fn(self,y_true, y_pred):
      s1,s2=y_true.shape
      #print(s1,s2)
        
      # this matrix defines indices of a set of entries that we want to 
      # extract from y_true and y_pred
      # s2=2
      # s1=self.batchReplayBufferSize
      indices=np.zeros(shape=(s1,s2))
      indices[:,0]=np.arange(s1)
      indices[:,1]=self.actionsAppend
        
      # gather_nd and mean_squared_error are TensorFlow functions
      loss = mean_squared_error(gather_nd(y_true,indices=indices.astype(int)), gather_nd(y_pred,indices=indices.astype(int)))
      #print(loss)
      return loss    
    ###########################################################################
    #   END - of function my_loss_fn
    ###########################################################################
     
     
    ###########################################################################
    #   START - function createNetwork()
    # this function creates the network
    ###########################################################################
     
    # create a neural network
    def createNetwork(self):
      model=Sequential()
      model.add(Dense(128,input_dim=self.stateDimension,activation='relu'))
      model.add(Dense(56,activation='relu'))
      model.add(Dense(self.actionDimension,activation='linear'))
      # compile the network with the custom loss defined in my_loss_fn
      model.compile(optimizer = RMSprop(), loss = self.my_loss_fn, metrics = ['accuracy'])
      return model
    ###########################################################################
    #   END - function createNetwork()
    ###########################################################################
             
    ###########################################################################
    #   START - function trainingEpisodes()
    #   - this function simulates the episodes and calls the training function 
    #   - trainNetwork()
    ###########################################################################
 
    def trainingEpisodes(self):        
      # here we loop through the episodes
      for indexEpisode in range(self.numberEpisodes):        
        # list that stores rewards per episode - this is necessary for keeping track of convergence 
        rewardsEpisode=[]
                    
        print("Simulating episode {}".format(indexEpisode))
          
        # reset the environment at the beginning of every episode
        (currentState)=self.env.reset()
                    
        # here we step from one state to another
        # this will loop until a terminal state is reached
        terminalState=False
        while not terminalState:
                                    
            # select an action on the basis of the current state, denoted by currentState
            action = self.selectAction(currentState,indexEpisode,self.env.M,self.env.K)
            print("Action selected {}".format(action))
              
            # here we step and return the state, reward, and boolean denoting if the state is a terminal state
            print("self.env.step(action)", self.env.step(action))
            (nextState, reward, terminalState,_) = self.env.step(action)          
            rewardsEpisode.append(reward)
      
            # add current state, action, reward, next state, and terminal flag to the replay buffer
            self.replayBuffer.append((currentState,action,reward,nextState,terminalState))
              
            # train network
            self.trainNetwork()
              
            # set the current state for the next step
            currentState=nextState
          
        print("Sum of rewards {}".format(np.sum(rewardsEpisode)))        
        self.sumRewardsEpisode.append(np.sum(rewardsEpisode))
    ###########################################################################
    #   END - function trainingEpisodes()
    ###########################################################################
             
        
    ###########################################################################
    #    START - function for selecting an action: epsilon-greedy approach
    ###########################################################################
    # this function selects an action on the basis of the current state 
    # INPUTS: 
    # state - state for which to compute the action
    # index - index of the current episode
    
    def selectAction(self,state,indexEpisode,M,K):

        print("STATE", state)
        # first index episodes we select completely random actions to have enough exploration
        # change this
        if indexEpisode<1:
            return np.random.randint(2, size=(M,K))  #np.random.choice(tf_env.action_spec().maximum + 1)
        # Returns a random real number in the half-open interval [0.0, 1.0)
        # this number is used for the epsilon greedy approach
        randomNumber=np.random.random()
        # after index episodes, we slowly start to decrease the epsilon parameter
        if indexEpisode>200:
            self.epsilon=0.999*self.epsilon
        # if this condition is satisfied, we are exploring, that is, we select random actions
        if randomNumber < self.epsilon:
            # returns a random action selected from: 0,1,...,actionNumber-1
            return np.random.randint(2, size=(M,K)) 

        # otherwise, we are selecting greedy actions
        else:
            # we return the index where Qvalues[state,:] has the max value
            # that is, since the index denotes an action, we select greedy actions
            if len(state.observation) >= 4:
                Qvalues=self.mainNetwork.predict(state.observation.reshape(1,4))
                return np.argmax(Qvalues[0,:]) - 1
            else:
                # If the state observation does not have at least 4 elements, we return a random action.
                return np.random.randint(2, size=(M,K))



    ###########################################################################
    #    END - function selecting an action: epsilon-greedy approach
    ###########################################################################
     
    ###########################################################################
    #    START - function trainNetwork() - this function trains the network
    ###########################################################################
     
    def trainNetwork(self):
      # if the replay buffer has at least batchReplayBufferSize elements,
      # then train the model 
      # otherwise wait until the size of the elements exceeds batchReplayBufferSize
      if (len(self.replayBuffer)>self.batchReplayBufferSize):
        # sample a batch from the replay buffer
        randomSampleBatch=random.sample(self.replayBuffer, self.batchReplayBufferSize)
          
        # here we form current state batch 
        # and next state batch
        # they are used as inputs for prediction
        currentStateBatch=np.zeros(shape=(self.batchReplayBufferSize,4))
        nextStateBatch=np.zeros(shape=(self.batchReplayBufferSize,4))            
        # this will enumerate the tuple entries of the randomSampleBatch
        # index will loop through the number of tuples
        for index,tupleS in enumerate(randomSampleBatch):
            # first entry of the tuple is the current state
            currentStateBatch[index,:]=tupleS[0]
            # fourth entry of the tuple is the next state
            nextStateBatch[index,:]=tupleS[3]
          
        # here, use the target network to predict Q-values 
        QnextStateTargetNetwork=self.targetNetwork.predict(nextStateBatch)
        # here, use the main network to predict Q-values 
        QcurrentStateMainNetwork=self.mainNetwork.predict(currentStateBatch)
          
        # now, we form batches for training
        # input for training
        inputNetwork=currentStateBatch
        # output for training
        outputNetwork=np.zeros(shape=(self.batchReplayBufferSize,2))
          
        # this list will contain the actions that are selected from the batch 
        # this list is used in my_loss_fn to define the loss-function
        self.actionsAppend=[]            
        for index,(currentState,action,reward,nextState,terminated) in enumerate(randomSampleBatch):
              
            # if the next state is the terminal state
            if terminated:
                y=reward                  
            # if the next state if not the terminal state    
            else:
                y=reward+self.gamma*np.max(QnextStateTargetNetwork[index])
              
            # this is necessary for defining the cost function
            self.actionsAppend.append(action)
              
            # this actually does not matter since we do not use all the entries in the cost function
            outputNetwork[index]=QcurrentStateMainNetwork[index]
            # this is what matters
            outputNetwork[index,action]=y
          
        # here, we train the network
        self.mainNetwork.fit(inputNetwork,outputNetwork,batch_size = self.batchReplayBufferSize, verbose=0,epochs=100)     
          
        # after updateTargetNetworkPeriod training sessions, update the coefficients 
        # of the target network
        # increase the counter for training the target network
        self.counterUpdateTargetNetwork+=1 
        if (self.counterUpdateTargetNetwork>(self.updateTargetNetworkPeriod-1)):
            # copy the weights to targetNetwork
            self.targetNetwork.set_weights(self.mainNetwork.get_weights())        
            print("Target network updated!")
            print("Counter value {}".format(self.counterUpdateTargetNetwork))
            # reset the counter
            self.counterUpdateTargetNetwork=0
    ###########################################################################
    #    END - function trainNetwork() 
    ###########################################################################     
                  





###########################################################################
#    DRIVER CODE
###########################################################################   

# import the class
# import HoneypotDDQN
# classical gym 
import gym
# instead of gym, import gymnasium 
#import gymnasium as gym

import numpy as np

import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.environments import suite_gym
from tf_agents.trajectories import time_step as ts

from gym import spaces

# import the environment
# import NetworkHoneypotEnv

# Defining parameters
gamma = 0.99
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

env = NetworkHoneypotEnv(10, 3, 7, 0.8, 0.2)
# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
tf_env = tf_py_environment.TFPyEnvironment(env)


timestep = tf_env.reset()
rewards = []
steps = []
numberEpisodes = 15



# create an object
LearningQDeep=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes)
# run the learning process
LearningQDeep.trainingEpisodes()
# get the obtained rewards in every episode
LearningQDeep.sumRewardsEpisode

print(rewards)

num_steps = np.sum(steps)
avg_length = np.mean(steps)
# avg_reward = np.mean(rewards)
# max_reward = np.max(rewards)
# max_length = np.max(steps)

print('num_episodes:', numberEpisodes, 'num_steps:', num_steps)
print('avg_length', avg_length)
# print('max_length', max_length)
# print('avg_length', avg_length, 'avg_reward:', avg_reward)
# print('max_length', max_length, 'max_reward:', max_reward)



















# select the parameters
# gamma=1
# probability parameter for the epsilon-greedy approach
# epsilon=0.1
# number of training episodes
# NOTE HERE THAT AFTER CERTAIN NUMBERS OF EPISODES, WHEN THE PARAMTERS ARE LEARNED
# THE EPISODE WILL BE LONG, AT THAT POINT YOU CAN STOP THE TRAINING PROCESS BY PRESSING CTRL+C
# DO NOT WORRY, THE PARAMETERS WILL BE MEMORIZED
# numberEpisodes=20
 
# create an object
# LearningQDeep=HoneypotDDQN.DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes)
# run the learning process
# LearningQDeep.trainingEpisodes()
# get the obtained rewards in every episode
# LearningQDeep.sumRewardsEpisode
 
#  summarize the model
# LearningQDeep.mainNetwork.summary()
# save the model, this is important, since it takes long time to train the model 
# and we will need model in another file to visualize the trained model performance
# LearningQDeep.mainNetwork.save("RL_Honeypot_trained_model_temp.keras")



# Visualizing after training

# load the model
# loaded_model = LearningQDeep.mainNetwok

# sumObtainedRewards=0
# simulate the learned policy for verification
 
 
# create the environment, here you need to keep render_mode='rgb_array' since otherwise it will not generate the movie
# env = gym.make("CartPole-v1",render_mode='rgb_array')


# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
# env = tf_py_environment.TFPyEnvironment(NetworkHoneypotEnv.NetworkHoneypotEnv())


# reset the environment
# (currentState,prob)=env.reset()
 
# Wrapper for recording the video
# https://gymnasium.farama.org/api/wrappers/misc_wrappers/#gymnasium.wrappers.RenderCollection
# the name of the folder in which the video is stored is "stored_video"
# length of the video in the number of simulation steps
# if we do not specify the length, the video will be recorded until the end of the episode 
# that is, when terminalState becomes TRUE
# just make sure that this parameter is smaller than the expected number of 
# time steps within an episode
# for some reason this parameter does not produce the expected results, for smaller than 450 it gives OK results
# video_length=400
# the step_trigger parameter is set to 1 in order to ensure that we record the video every step
#env = gym.wrappers.RecordVideo(env, 'stored_video',step_trigger = lambda x: x == 1, video_length=video_length)
# env = gym.wrappers.RecordVideo(env, 'stored_video_ddqn', video_length=video_length)
 
 
# since the initial state is not a terminal state, set this flag to false
# terminalState=False
'''while not terminalState:
    # get the Q-value (1 by 2 vector)
    Qvalues=loaded_model.predict(currentState.reshape(1,4))
    # select the action that gives the max Qvalue
    action=np.random.choice(np.where(Qvalues[0,:]==np.max(Qvalues[0,:]))[0])
    # if you want random actions for comparison
    #action = env.action_space.sample()
    # apply the action
    (currentState, currentReward, terminalState,_,_) = env.step(action)
    # sum the rewards
    sumObtainedRewards+=currentReward
'''
env.reset()
env.close()