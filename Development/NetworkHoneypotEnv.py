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
        self.nicr_nodes = [np.random.choice(K)]
        print("NICR node:", self.nicr_nodes)

        # Initialize an empty list for the nifr (fake resource node)
        # As an example to test the environment, uncomment this for nifr hard-coded
        # self.nifr_nodes = [2,3,5]
        self.nifr_nodes = []
        print("NIFR list:", self.nifr_nodes)

        self._action_spec = array_spec.BoundedArraySpec(
            shape=(M, K), dtype=np.int32, minimum=0, maximum=1, name='action')
        print("Action spec:", self._action_spec)
        
        # Add the observation spec for the state vector
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(1,K), dtype=np.int32, minimum=0, maximum=1, name='observation')
        print("Observation spec:", self._observation_spec)

        self._reward_spec = array_spec.BoundedArraySpec(
            shape=(1,K), dtype=np.int32, minimum=-1, maximum=1, name='reward')
        print("Reward spec:", self._reward_spec)
        
        # Initialize the state vector as an empty vector of 0s with size K
        self._state = np.zeros(self.K, dtype=np.int32)
        print("State vector:", self._state)
        
        # Initialize the matrix for the defender's view as zeros
        self._matrix = np.zeros((M, K), dtype=np.int32)
        print("Matrix:", self._matrix)
        
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
        self.nicr_nodes = [np.random.choice(self.K)]
        print("NICR node after reset:", self.nicr_nodes)

        # Reset list for the nifr (fake resource node)
        self.nifr_nodes = []

        # Reset the state vector as an empty vector of 0s with size K
        # update 06/12/2023 - resetting state cause the next visit count to turn the state into 0, 
        # which in turn make Q guessing networks broken. So i will comment this out.
        # self._state = np.zeros(self.K, dtype=np.int32)
        # print("State vector after reset:", self._state)
        
        # Reset the matrix for the defender's view as zeros
        # self._matrix = np.zeros((self.M, self.K), dtype=np.int32)
        # print("Matrix after reset:", self._matrix)
        
        # Reset the dictionary for the NTPG as an empty dictionary
        self._ntpg = {}
        
        # Reset the dictionary for the HTPG as an empty dictionary
        self._htpg = {}
        
        # Reset the episode ended flag as False
        self._episode_ended = False
        print("Episode ended flag after reset:", self._episode_ended)
            
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
        
        # Check if each row has only one 1
        if not np.all(np.sum(action, axis=1) == 1):
            return False
        
        # If all checks pass, return True
        return True


    def __attacker_move(self):
        """Simulates the attacker's move based on the NTPG and HTPG.
        Updates the state vector with the new attacked node.
        """

        # Fix the current_node to the very first node
        current_node = '192.168.0.2'
        current_node_index = int(current_node.split('.')[-1]) - 2  # Get the index of the current_node
        print("Current node attacker residing in:", current_node)
        print("Current node index:", current_node_index)

        while True:
            print("HTPG OF CURRENT NODE:" , self._htpg.get(current_node))
            # print(self._htpg.get(current_node)[0][2])
            if self._htpg.get(current_node) == []:
                print("No more possible routes, exit the loop. State vector after the attack:", self._state)
                break

            # Attack the current node with a probability based on the HTPG
            elif np.random.random() <= self._htpg.get(current_node)[0][2]:
                self._state[current_node_index] = 1  # Use the index to update the state
                print("Attacked node:", current_node)

            # Move to the next node with a probability based on the NTPG
            elif np.random.random() <= self._ntpg.get(current_node)[0][1] or np.random.random() <= self._ntpg.get(current_node)[0][2]:
                current_node = self._ntpg.get(current_node)[0][0]
                current_node_index = int(current_node.split('.')[-1]) - 2  # Update the current_node_index
                print("Next node to attack:", current_node)

            else:
                print("No more possible routes, exit the loop. State vector after the attack:", self._state)
                break  # No more possible routes, exit the loop

        # Update the NIFR list based on the action matrix
        self.__update_nifr_nodes(self.nifr_nodes)
        print("NIFR list after attack:", self.nifr_nodes)






    def __is_nicr_attacked(self, nicr_nodes):
        # Check if any nicr (important resource node) is attacked or not
        # Return True if any nicr is attacked, False otherwise
        
        # Check if any nicr node is attacked in the state vector
        for i in nicr_nodes:
            if self._state[i] == 1:
                # End the episode and calculate the reward
                self._episode_ended = True
                return True
        
        # If no nicr node is attacked, return False
        return False

    def __is_nifr_attacked(self, nifr_nodes):
        # Check if any fake resource node is attacked or not
        # Return True if any fake resource node is attacked, False otherwise

        # Check if any nicr node is attacked in the state vector
        for i in nifr_nodes:
            if self._state[i] == 1:
                # End the episode and calculate the reward
                self._episode_ended = True
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
        print("self._matrix to update nifr nodes:", self._matrix)
        for row in self._matrix:
            if any(row):
                print("row.argmax():", row.argmax())
                nifr_nodes.append(row.argmax())
                print("NIFR list after update:", nifr_nodes)
    
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
                reward = 0
                # If no, continue the episode and return the transition state and reward
                return ts.transition(np.array([self._state], dtype=np.int32), reward)
        else:
            # If no, end the episode and return the termination state and reward
            print("Invalid Action:", action)
            print("Invalid action, end the episode")
            self._episode_ended = True
            reward = -1
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        
          
environment = NetworkHoneypotEnv(10, 3, 7, 0.8, 0.2)
utils.validate_py_environment(environment, episodes=10)










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
from keras.optimizers import RMSprop
from keras.optimizers import Adam
from collections import deque 
from tensorflow import gather_nd
from keras.losses import mean_squared_error 
 


# Outline the difference from cartpole:
# Policy
# - The policy is a function that maps states to actions.
# - The policy is represented by a neural network that takes the state as input and outputs the action.
# - The policy is trained by the agent to maximize the total reward.
# - Here, we use a neural network with two hidden layers of 100 units each and ReLU activation.
# - The final layer is a dense layer with 2 units, one for each possible action in the deception network environment.

# hình như thầy bảo cố định lại 1 cái môi trường HTPG NTPG
# 14/11/2023 - đã cố định một môi trường HTPG-NTPG


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
      self.stateDimension = env.K
      print("STATE DIMENSION --- AGENT TRAINING",self.stateDimension)
      # action dimension
      self.actionDimension = env.M * env.K
      print("ACTION DIMENSION --- AGENT TRAINING",self.actionDimension)
      # this is the maximum size of the replay buffer
      self.replayBufferSize=100
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

      # initialize visit(s,a)
      self.visitCounts = 0
        
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
    #   START - createNetwork function
    ###########################################################################
    
    def createNetwork(self):
        # create a neural network with two hidden layers of 100 units each and ReLU activation (must fix!)
        # the final layer is a dense layer with m*k units, one for each possible deployment combination
        model = Sequential()

        model.add(InputLayer(input_shape=self.stateDimension))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.actionDimension, activation='linear'))
        
        # use mean squared error as the loss function
        # original used a custom loss one, but for this case im not sure
        model.compile(loss=self.my_loss_fn, optimizer=Adam(), metrics = ['accuracy'])
        print("Created network:", model.summary())
        return model

    ###########################################################################
    #   END - createNetwork function
    ###########################################################################

    ###########################################################################
    #   START - trainingEpisodes function
    ###########################################################################
    
    def trainingEpisodes(self):
        
        # iterate over the episodes
        for episode in range(self.numberEpisodes):

            # list that store rewards in each episode to keep track of convergence
            rewardsEpisode=[]

            print("------------------------------------------------------------------------------------------------------------------------")
            print("Simulating episode number: ",episode)
            print("------------------------------------------------------------------------------------------------------------------------")

            # reset the environment
            # in other words, s=s0
            # reset = self.env.reset()
            # print("Resetting the environment", reset)
            currentState=self.env.reset()

            print("Current state: ", currentState.observation)

            # here we step from one state to another
            # in other words, s=s0, s=s1, s=s2, ..., s=sn
            # until either nicr or nifr got attacked, sum up the state and get reward
            # stateCount = 100
            for i in range (self.env.K):
                
                print("while looping through all the K nodes after stateCount times to check if nicr or nifr got attacked") 

                # select the action based on the epsilon-greedy approach
                print("observed state: ",currentState.observation)
                action = self.selectAction(currentState.observation.reshape(1, -1), episode)
                print("Action selected: ",action)
                print("self.env.step based on action: ",self.env.step(action))

                # here we step and return the state, reward, and boolean denoting if the state is a terminal state
                # (terminalState, discount, reward, nextState) = self.env.step(action)
                nextState = self.env.step(action)

                # Basically we just assign the result after we step to a variable called nextState
                # Then we seperate the variable (which is a TimeStep object) to 4 part of it: step_type, reward, discount, and observation
                # This kinda lengthen the process but im a student so...
                (terminalState, discount, reward, nextStateObservation) = nextState
                # This part is dumb probably need to fix
                print((terminalState, discount, nextStateObservation, reward))


                print("------------------- REWARD OF THIS ACTION --------------------------: ",reward)
                rewardsEpisode.append(reward)


                print("Next state: ", nextState)


                # add current state, action, reward, next state, and terminal flag to the replay buffer
                # print("Next state observation array: ", nextState)
                self.replayBuffer.append((currentState.observation, action, reward, nextStateObservation, terminalState))
                print("Replay buffer: ",self.replayBuffer)

                # train network
                self.trainNetwork()

                # visiting next node in the network
                self.visitCounts = self.visitCounts + 1
                print("Visit counts: ",self.visitCounts)
                 
                # set the current state for the next step s <- s'
                currentState=nextState
                print("Current state after step: ", currentState)

                # stateCount = stateCount + 1

            print("------------------------- END LOOP HERE -------------------------")

        # tbh i dont even know if summing reward here is neccessary
        print("Sum of rewards {}".format(np.sum(rewardsEpisode)))        
        self.sumRewardsEpisode.append(np.sum(rewardsEpisode)) 
               
    ###########################################################################
    #   END - trainingEpisodes function
    ###########################################################################

    ###########################################################################
    #   START - selectAction function
    ###########################################################################
    
    def selectAction(self, state, episode):
        # we know nothing about the environment in first few episodes, so we need to explore
        # feel free to change for more exploration
        if episode < 1:
            action = np.zeros((self.env.M, self.env.K))
            for i in range(self.env.M):
                action[i, np.random.randint(0, self.env.K)] = 1
            action = action.astype(np.int32)
            print("ACTION MATRIX exploit:", action)
            return action

        # Random number for epsilon-greedy approach [0.0, 1.0)
        randomValue = np.random.random()

        # After a certain amount of episode, we start to decrease the epsilon value
        # This is to make sure that the agent will not stuck in a local optimum
        if episode > 200:
            self.epsilon = 0.999 * self.epsilon

        # If the random number is less than epsilon, we explore
        if randomValue < self.epsilon:
            action = np.zeros((self.env.M, self.env.K))
            for i in range(self.env.M):
                action[i, np.random.randint(0, self.env.K)] = 1
            action = action.astype(np.int32)
            print("ACTION MATRIX exploit:", action)
            return action

        # If the random number is greater than epsilon, we exploit
        else:
            # we return the action that Qvalues[state,:] of which has the max value
            # that is, since the index denotes an action, we select greedy actions
            # basically, we select the action that gives the max Qvalue

            # use mainNetwork to predict the Qvalues (Qvalues is an array of size m*k represent Q-values of all the actions)
            print("STATE TO PREDICT:", state)
            Qvalues = self.mainNetwork.predict(state)
            print("QVALUES:", Qvalues)

            # Get the index of the maximum Q-value
            max_index = np.argmax(Qvalues)

            # Create an action matrix with only one 1 on each row based on the maximum Q-value index
            action_matrix = np.zeros((self.env.M, self.env.K))
            action_matrix[max_index // self.env.K, max_index % self.env.K] = 1

            action_matrix = action_matrix.astype(np.int32)

            print("ACTION MATRIX exploit:", action_matrix)
            return action_matrix

            # return action_matrix

    ###########################################################################
    #   END - selectAction function
    ###########################################################################

    ###########################################################################
    #   START - trainNetwork function
    ###########################################################################

    def trainNetwork(self):
        if len(self.replayBuffer) < self.replayBufferSize:
            return

        randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
        print("Random sample batch:", randomSampleBatch)
        inputNetwork = np.zeros((self.batchReplayBufferSize, 4))
        print("Input network:", inputNetwork)
        outputNetwork = np.zeros((self.batchReplayBufferSize, 2))
        print("Output network:", outputNetwork)
        self.actionsAppend = []
        self.actionsAppend = []


        for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
            # parameter for the current state-action pair
            alpha = 1 / (1 + self.visitCounts)

            QcurrentStateMainNetwork = self.mainNetwork.predict(currentState.reshape(1, 4))
            QnextStateMainNetwork = self.mainNetwork.predict(nextState.reshape(1, 4))

            # if the next state is the terminal state
            if terminated:
                y = reward
            # if the next state is not the terminal state
            else:
                y = reward + self.gamma * np.max(QnextStateMainNetwork[0])

            # this is necessary for defining the cost function
            self.actionsAppend.append(action)  # this actually does not matter since we do not use all the entries in the cost function
            outputNetwork[index] = QcurrentStateMainNetwork[0]  # this is what matters
            outputNetwork[index, action] = y  # scale the output by the alpha parameter
            outputNetwork[index] = outputNetwork[index] * alpha

            # assign the current state to the input
            inputNetwork[index] = currentState

        self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, epochs=1, verbose=0)
        self.counterUpdateTargetNetwork = self.counterUpdateTargetNetwork + 1

        if self.counterUpdateTargetNetwork == self.updateTargetNetworkPeriod:
            self.targetNetwork.set_weights(self.mainNetwork.get_weights())
            self.counterUpdateTargetNetwork = 0
            print("Target network updated!")

    ###########################################################################
    #   END - trainNetwork function
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
numberEpisodes = 2



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
# env.reset()
# env.close()