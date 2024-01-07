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






# Visualize the environment
import os
import imageio
import matplotlib.pyplot as plt
import networkx as nx

def visualize_steps(steps, output_folder, output_movie):
    G = nx.Graph()
    G.add_nodes_from(your_nodes_list)
    G.add_edges_from(your_edges_list)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = []

    for i, step in enumerate(steps):
        plt.figure()
        colors = []
        for node in G.nodes:
            if node == step['attacker_node']:
                colors.append('red')
            elif node in step['nifr_nodes']:
                colors.append('blue')
            else:
                colors.append('green')

        nx.draw(G, with_labels=True, node_color=colors)
        image_path = os.path.join(output_folder, f'step_{i}.png')
        plt.savefig(image_path)
        images.append(imageio.imread(image_path))
        plt.close()

    imageio.mimsave(output_movie, images, duration=500)










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
# 20/12/2023 - added step counter to the environment


class NetworkHoneypotEnv(py_environment.PyEnvironment):  # Inherit from gym.Env


    #------------------------------------------------------------------------------------------------------------
    #-------------------------------------------- TPGs Converter ------------------------------------------------
    #------------------------------------------------------------------------------------------------------------
    def tpgs_converter(self, ntpg, htpg):
        return ntpg, htpg        
    


    def __init__(self, N, M, K, P, ntpg, htpg):

        # Initialize the spec for the environment
        self.N = N # Total amount of nodes (n)
        self.M = M # Number of deception nodes (m)
        self.K = K # Number of normal nodes (k)
        self.P = P # Probability of attacker moving to the next node

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

        # Step counter (20/12/2023 - added step counter)
        self.current_step = 0
        # Maximum number of steps in an episode
        self.maxSteps=50
        
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
        # self._ntpg = {'192.168.0.2': [ ('192.168.0.3', 0.8,0.6),('192.168.0.3', 0.8,0.6)], 
        #             '192.168.0.3': [ ('192.168.0.5', 0.5,0.1)], 
        #             '192.168.0.4': [('192.168.0.5', 0.8,0.2),('192.168.0.6', 0.4,0.2),('192.168.0.7', 0.3,0.1),], 
        #             '192.168.0.5': [('192.168.0.8', 0.2,0.1),('192.168.0.7', 0.6,0.3)],
        #             '192.168.0.6': [],
        #             '192.168.0.7': [('192.168.0.8', 0.2,0.9)],
        #             '192.168.0.8': [],}

        # 5/1/2024 - add TPG input for initialization
        self._ntpg = ntpg


        # self._htpg = {'192.168.0.2': [('NetBT', 'CVE-2017-0161', 0.6, ('192.168.0.4', 'User')),
        #                            ('Win32k', 'CVE-2018-8120', 0.04, ('192.168.0.4', 'Root')),
        #                            ('VBScript', 'CVE-2018-8174', 0.5, ('192.168.0.4', 'Root')),
        #                            ('Apache', 'CVE-2017-9798', 0.8, ('192.168.0.3', 'User')),
        #                            ('Apache', 'CVE-2014-0226', 0.6, ('192.168.0.3', 'Root')),], 
        #            '192.168.0.3': [('Apache', 'CVE-2017-9798', 0.5, ('192.168.0.5', 'User')),
        #                            ('Apache', 'CVE-2014-0226', 0.1, ('192.168.0.5', 'Root')),], 
        #            '192.168.0.4': [('NetBT', 'CVE-2017-0161', 0.8, ('192.168.0.5', 'User')),
        #                            ('Win32k', 'CVE-2018-8120', 0.02, ('192.168.0.5', 'Root')),
        #                            ('VBScript', 'CVE-2018-8174', 0.2, ('192.168.0.5', 'Root')),
        #                            ('OJVM', 'CVE-2016-5555', 0.4, ('192.168.0.6', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.2, ('192.168.0.6', 'Root')),
        #                            ('HFS', 'CVE-2014-6287', 0.3, ('192.168.0.7', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.7', 'Root')),], 
        #            '192.168.0.5': [('HFS', 'CVE-2014-6287', 0.6, ('192.168.0.7', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.3, ('192.168.0.7', 'Root')),
        #                            ('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root')),],
        #            '192.168.0.6': [],
        #            '192.168.0.7': [('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root'))],
        #            '192.168.0.8': [],
        #}

        self._htpg = htpg
        

        print("State vector:", self._state)
        print("Matrix:", self._matrix)
        print("NTPG:", self._ntpg)
        print("HTPG:", self._htpg)

        # Initialize attacker entrypoint
        # 20/12/2023 - fixed example, will be change later 
        # TODO: Dynamically locate this entrypoint
        self._current_attacker_node = list(ntpg.keys())[2]

        #print(self.get_info())


    def action_spec(self):
        return self._action_spec
    
    def observation_spec(self):
        return self._observation_spec
    

    def _reset(self):

        # Reset the step counter
        self.current_step = 0

        # Reset the nicr node by random choosing a new one
        self.nicr_nodes = [np.random.choice(self.K)]
        print("NICR node after reset:", self.nicr_nodes)

        # Reset list for the nifr (fake resource node)
        self.nifr_nodes = []

        # Reset the state vector as an empty vector of 0s with size K
        # update 06/12/2023 - resetting state cause the next visit count to turn the state into 0, 
        # which in turn make Q guessing networks broken. So i will comment this out.
        # update 07/01/2024 - the above update was because of a false logic in the training code, each attacker action
        # should correspond with a defender action. This was fix, so we need to reset the env properly again.
        self._state = np.zeros(self.K, dtype=np.int32)
        print("State vector after reset:", self._state)
        
        # Reset the matrix for the defender's view as zeros
        self._matrix = np.zeros((self.M, self.K), dtype=np.int32)
        print("Matrix after reset:", self._matrix)
        
        # Reset the dictionary for the NTPG as an empty dictionary
        # self._ntpg = {} fug u bitch
        
        # Reset the dictionary for the HTPG as an empty dictionary
        # self._htpg = {}
        
        # Reset the episode ended flag as False
        self._episode_ended = False
        print("Episode ended flag after reset:", self._episode_ended)
            
        # Regenerate the NTPG and HTPG based on some logic or data
        # Here I will use the same code as in the __init__ function (12/11/2023 - reset to fixed example)
        # self._ntpg = {'192.168.0.2': [ ('192.168.0.3', 0.8,0.6),('192.168.0.3', 0.8,0.6)], 
        #               '192.168.0.3': [ ('192.168.0.5', 0.5,0.1)], 
        #               '192.168.0.4': [('192.168.0.5', 0.8,0.2),('192.168.0.6', 0.4,0.2),('192.168.0.7', 0.3,0.1),], 
        #               '192.168.0.5': [('192.168.0.8', 0.2,0.1),('192.168.0.7', 0.6,0.3)],
        #               '192.168.0.6': [],
        #               '192.168.0.7': [('192.168.0.8', 0.2,0.9)],
        #               '192.168.0.8': [],}


        # self._htpg = {'192.168.0.2': [('NetBT', 'CVE-2017-0161', 0.6, ('192.168.0.4', 'User')),
        #                            ('Win32k', 'CVE-2018-8120', 0.04, ('192.168.0.4', 'Root')),
        #                            ('VBScript', 'CVE-2018-8174', 0.5, ('192.168.0.4', 'Root')),
        #                            ('Apache', 'CVE-2017-9798', 0.8, ('192.168.0.3', 'User')),
        #                            ('Apache', 'CVE-2014-0226', 0.6, ('192.168.0.3', 'Root')),], 
        #            '192.168.0.3': [('Apache', 'CVE-2017-9798', 0.5, ('192.168.0.5', 'User')),
        #                            ('Apache', 'CVE-2014-0226', 0.1, ('192.168.0.5', 'Root')),], 
        #            '192.168.0.4': [('NetBT', 'CVE-2017-0161', 0.8, ('192.168.0.5', 'User')),
        #                            ('Win32k', 'CVE-2018-8120', 0.02, ('192.168.0.5', 'Root')),
        #                            ('VBScript', 'CVE-2018-8174', 0.2, ('192.168.0.5', 'Root')),
        #                            ('OJVM', 'CVE-2016-5555', 0.4, ('192.168.0.6', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.2, ('192.168.0.6', 'Root')),
        #                            ('HFS', 'CVE-2014-6287', 0.3, ('192.168.0.7', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.7', 'Root')),], 
        #            '192.168.0.5': [('HFS', 'CVE-2014-6287', 0.6, ('192.168.0.7', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.3, ('192.168.0.7', 'Root')),
        #                            ('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root')),],
        #            '192.168.0.6': [],
        #            '192.168.0.7': [('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
        #                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root'))],
        #            '192.168.0.8': [],
        #}

        self._current_attacker_node = list(ntpg.keys())[2]

        # print(self.get_info())

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

    
    # Attacker themselves move with each "step" in the environment too
    # Does this code represent that? or just a static mapping?
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
            print(self._htpg.get(current_node)[0][2])
            if self._htpg.get(current_node) == []:
                print("No more possible routes, exit the loop. State vector after the attack:", self._state)
                print(self._htpg.get(current_node)[0][2])
                break

            # Attack the current node with a probability based on the HTPG
            # THis shit flop omg im dumb

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
                print(self._htpg.get(current_node)[0][2])
                break  # No more possible routes, exit the loop

        # Update the NIFR list based on the action matrix
        self.__update_nifr_nodes(self.nifr_nodes)
        print("NIFR list after attack:", self.nifr_nodes)

    def __attacker_move_step(self):
        """Simulates one step of the attacker's move based on the NTPG and HTPG.
        Updates the state vector with the new attacked node.
        """
        # Get the current node information
        current_node = self._current_attacker_node
        current_node_index = int(current_node.split('.')[-1]) - 2

        # Check if the current node has possible routes
        print("NTPG:", self._ntpg)
        print("current_node:", current_node)
        print("NTPG OF CURRENT NODE:" , self._ntpg.get(current_node)[0]) if self._ntpg.get(current_node) else print("I cum in yo mom mouth")
        os.system("pause")
        if self._ntpg.get(current_node):
            # Iterate over the possible routes from the current node
            for route in self._ntpg.get(current_node):
                next_node = route[0]
                attack_chance = route[1]  # Use the chance to attack the node
                if np.random.random() <= attack_chance:
                    self._state[current_node_index] = 1
                    print("Attacked node:", current_node)
                    break  # Attack successful, exit the loop

            # Move to the next node based on HTPG probability
            next_node = np.random.choice([route[0] for route in self._ntpg.get(current_node)])  # Fix: Specify a 1-dimensional array
            self._current_attacker_node = next_node
            print("Next node to attempt attack:", next_node)

        else:
            print("No more possible routes, exit the loop. State vector after the attack:", self._state)

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
                if len(nifr_nodes) > 3:
                    nifr_nodes.pop(0)
                print("NIFR list after update:", nifr_nodes)
    
    def _step(self, action):
        # Check if the episode has ended
        if self._episode_ended:
            # If yes, reset the environment and return the initial state
            return self.reset()
        
        # Check if the maximum number of steps has been reached
        if self.current_step >= self.maxSteps:
            # If yes, end the episode and return the termination state and reward
            print("Maximum number of steps reached, end the episode, agent lose")
            self._episode_ended = True
            reward = -1
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        
        # Check if the action is valid
        if self.__is_action_valid(action):
            # If yes, update the matrix for the defender's view with the action
            self._matrix = action

            # Update the NIFR list based on the action matrix.
            self.__update_nifr_nodes(self.nifr_nodes)
            
            # Simulate the attacker's move based on the NTPG and HTPG
            self.__attacker_move_step()
            
            # Check if the attacker has reached a nicr or a fake resource node
            if self.__is_nicr_attacked(self.nicr_nodes):
                # If yes, end the episode and return the termination state and reward
                self._episode_ended = True
                print("Attacker reached nicr, end the episode")
                print("Current node attacker residing in:", self._current_attacker_node)
                print("nicr nodes:", self.nicr_nodes)
                reward = -1
                return ts.termination(np.array([self._state], dtype=np.int32), reward)
            if self.__is_nifr_attacked(self.nifr_nodes):
                # If yes, end the episode and return the termination state and reward
                self._episode_ended = True
                print("Attacker reached nifr, end the episode")
                print("Current node attacker residing in:", self._current_attacker_node)
                print("nifr nodes:", self.nifr_nodes)
                reward = 1
                return ts.termination(np.array([self._state], dtype=np.int32), reward)
            else:
                reward = 0
                # Increment the step counter
                self.current_step += 1
                # If no, continue the episode and return the transition state and reward
                return ts.transition(np.array([self._state], dtype=np.int32), reward)
        else:
            # If no, end the episode and return the termination state and reward
            print("Invalid Action:", action)
            print("Invalid action, end the episode")
            self._episode_ended = True
            reward = -1
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        
          
#environment = NetworkHoneypotEnv(10, 3, 7, 0.8, 0.2)
#utils.validate_py_environment(environment, episodes=10)










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
      # action dimension k!/(k-m)! (07/12/2023 - different permutation problem)
      self.actionDimension = factorial(env.K) / factorial(env.K - env.M)
      print("ACTION DIMENSION --- AGENT TRAINING",self.actionDimension)
      # this is the maximum size of the replay buffer
      self.replayBufferSize=300
      # this is the size of the training batch that is randomly sampled from the replay buffer
      self.batchReplayBufferSize=20
        
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
        # the final layer is a dense layer with k!/(k-m)! units, one for each possible deployment combination
        model = Sequential()

        model.add(InputLayer(input_shape=self.stateDimension))

        # Add another dropout layer with 0.25 probability
        model.add(keras.layers.Dropout(0.25))

        # Add a flatten layer to convert the 2D feature maps to 1D feature vectors
        model.add(keras.layers.Flatten())

        # Add a dense layer with 256 units and ReLU activation
        model.add(keras.layers.Dense(256, activation='relu'))

        # Add another batch normalization layer
        model.add(keras.layers.BatchNormalization())

        # Add another dropout layer with 0.5 probability
        model.add(keras.layers.Dropout(0.5))

        # Add another dense layer with 128 units and ReLU activation
        model.add(keras.layers.Dense(128, activation='relu'))

        # Add another batch normalization layer
        model.add(keras.layers.BatchNormalization())

        # Add another dropout layer with 0.5 probability
        model.add(keras.layers.Dropout(0.5))

        # Add an output layer with 10 units and softmax activation for multi-class classification
        model.add(keras.layers.Dense(10, activation='softmax'))

        #lmao
        model.add(Dense(64, activation='relu'))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.actionDimension, activation='linear'))
        
        # use mean squared error as the loss function
        # original used a custom loss one, but for this case im not sure
        model.compile(loss=mean_squared_error, optimizer=RMSprop(), metrics = ['accuracy'])
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

        # iterate over the episodes
        for episode in range(self.numberEpisodes):
            
            # self.env = NetworkHoneypotEnv(10, 3, 7, 0.8, 0.2)
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
            while not env.is_last():
                # Your code here
                
                #print("while looping through all the K nodes after stateCount times to check if nicr or nifr got attacked") 
                print("Patroling until either nicr or nifr got attacked - end episode")

                # select the action based on the epsilon-greedy approach
                print("observed state: ",currentState.observation)
                action = self.selectAction(currentState.observation.reshape(1, -1), episode)
                print("Action selected: ",action)
                print("self.env.step based on action: ",self.env.step(action))

                # here we step and return the state, reward, and boolean denoting if the state is a terminal state
                # (terminalState, discount, reward, nextState) = self.env.step(action)
                nextState = self.env.step(action)
                steps.append({'attacker_node': self.env._current_attacker_node, 'nifr_nodes': self.env.nifr_nodes})


                # Basically we just assign the result after we step to a variable called nextState
                # Then we seperate the variable (which is a TimeStep object) to 4 part of it: step_type, reward, discount, and observation
                # This kinda lengthen the process but im a student so...
                (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, currentState.reward, currentState.is_last())
                # This part is dumb probably need to fix
                print("I NEED TO LEARN HOW TO MLG LIKE BOSS PINK GUY")
                print((discount, nextStateObservation, reward, terminalState))

                if terminalState:
                    print("Terminal state reached, end episode")
                    
                if not terminalState:
                    print("Terminal state not reached, continue episode")
        
                print("------------------- REWARD OF THIS ACTION --------------------------: ",reward)
                os.system("pause")
                rewardsEpisode.append(reward)


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

            print("------------------------- END LOOP HERE -------------------------")


        # Visualize the steps
        visualize_steps(steps, 'images', 'movie.gif')


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
        if episode < 20:
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
    #   Status: Active
    ###########################################################################

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
            currentStateBatch=np.zeros(shape=(self.batchReplayBufferSize,7))
            print("Current state batch: ",currentStateBatch)

            nextStateBatch=np.zeros(shape=(self.batchReplayBufferSize,7))      
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
            outputNetwork=np.zeros(shape=(self.batchReplayBufferSize,210))
            print("Output network: ",outputNetwork)
             
            # this list will contain the actions that are selected from the batch 
            # this list is used in my_loss_fn to define the loss-function
            self.actionsAppend=[]            
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
                self.actionsAppend.append(action)
                print("Actions after append: ",self.actionsAppend)
                 
                # this actually does not matter since we do not use all the entries in the cost function
                outputNetwork[index]=QcurrentStateMainNetwork[index]
                print("Output network index: ",outputNetwork)
                # this is what matters
                outputNetwork[index,action]=y
                print("Output network: ",outputNetwork)
             
            # here, we train the network
            self.mainNetwork.fit(inputNetwork,outputNetwork,batch_size = self.batchReplayBufferSize, verbose=1,epochs=20) 
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
        print("LOSS FUNCTION - Y_TRUE:",y_true)
        s1,s2=y_true.shape
        print("LOSS FUNCTION - S1 AND S2:",s1,s2)
        
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
gamma = 0.9
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

ntpg = {'192.168.1.3': [('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0),('192.168.2.3', 0,0.9756)],
                      '192.168.2.3': [('192.168.1.3', 0,0.0009),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.2.4': [('192.168.2.3', 0,0.9756),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.3.3': [],
                      '192.168.3.4': [('192.168.3.5', 0,0.0009)],
                      '192.168.3.5': [('192.168.4.3', 0,0.9756)],
                      '192.168.4.3': [('192.168.3.4', 0,0.9756),('192.168.3.5', 0,0.0009),('192.168.3.3', 0.9746,0)],} 

htpg = {'192.168.1.3': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),
                              ('Apache', 'CVE-2014-6271', 0.9756, ('192.168.2.3', 'Root')),
                              ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],
                      '192.168.2.3': [('PHP Server', 'CVE-2020-35132', 0.0009, ('192.168.1.3', 'Root')),
                                      ('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),
                                      ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],
                      '192.168.2.4': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.2.3', 'Root')),
                                      ('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),
                                      ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],
                      '192.168.3.3': [],
                      '192.168.3.4': [('PHP Server','CVE-2020-35132','0.0009', ('192.168.3.5', 'Root')),],
                      '192.168.3.5': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),],
                      '192.168.4.3': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.3.4', 'Root')),
                                      ('PHP Server','CVE-2020-35132','0.0009', ('192.168.3.5', 'Root')),
                                      ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],}


# Extract nodes from the ntpg dictionary
your_nodes_list = list(ntpg.keys())

# Extract edges from the ntpg dictionary
your_edges_list = [(node, edge[0]) for node in ntpg for edge in ntpg[node]]





env = NetworkHoneypotEnv(10, 3, 7, 0.8, ntpg, htpg)
# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
tf_env = tf_py_environment.TFPyEnvironment(env)


timestep = tf_env.reset()
rewards = []
steps = []
numberEpisodes = 5



# create an object
LearningQDeep=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes)
# run the learning process
LearningQDeep.trainingEpisodes()
# get the obtained rewards in every episode
LearningQDeep.sumRewardsEpisode

print(rewards)

# num_steps = np.sum(steps)
# avg_length = np.mean(steps)
# avg_reward = np.mean(rewards)
# max_reward = np.max(rewards)
# max_length = np.max(steps)

# print('num_episodes:', numberEpisodes, 'num_steps:', num_steps)
# print('avg_length', avg_length)
# print('max_length', max_length)
# print('avg_length', avg_length, 'avg_reward:', avg_reward)
# print('max_length', max_length, 'max_reward:', max_reward)



#  summarize the model
LearningQDeep.mainNetwork.summary()
# save the model, this is important, since it takes long time to train the model 
# and we will need model in another file to visualize the trained model performance
LearningQDeep.mainNetwork.save("RL_Honeypot_trained_model_temp.keras")






###########################################################################
#    EVALUATION CODE
###########################################################################   



import matplotlib.pyplot as plt

# Load the trained model
trained_model = tf.keras.models.load_model("RL_Honeypot_trained_model_temp.keras")

# Create a new environment for evaluation
eval_env = NetworkHoneypotEnv(10, 3, 7, 0.8, ntpg, htpg)
# tf_eval_env = tf_py_environment.TFPyEnvironment(eval_env)

# Reset the environment
eval_time_step = eval_env.reset()

# Initialize variables for tracking rewards and steps
eval_rewards = []
eval_steps = []

# Evaluate the model for a certain number of episodes
eval_episodes = 3
for _ in range(eval_episodes):
    episode_reward = 0
    episode_steps = 0

    print("------------------------------------------------------------------------------------------------------------------------")
    print("Evaluating episode number: ",eval_episodes)
    print("------------------------------------------------------------------------------------------------------------------------")

    # Run the evaluation episode
    while not eval_time_step.is_last():
        # Get the action from the trained model
        
        action = LearningQDeep.selectActionEval(eval_time_step.observation, _, trained_model)
        print("ACTION SELECTED:", action)
        # Take a step in the environment
        eval_time_step = eval_env.step(action)
        print("EVAL TIME STEP:", eval_time_step)

        # Update the episode reward and steps
        episode_reward += eval_time_step.reward
        print("EPISODE REWARD:", episode_reward)
        episode_steps += 1
        print("EPISODE STEPS:", episode_steps)

    # Append the episode reward and steps to the evaluation lists
    eval_rewards.append(episode_reward)
    eval_steps.append(episode_steps)

    # Reset the environment for the next episode
    eval_time_step = eval_env.reset()

# Calculate the average reward and steps per episode
avg_eval_reward = np.mean(eval_rewards)
avg_eval_steps = np.mean(eval_steps)

# Print the evaluation results
print("Evaluation Results:")
print("Average Reward per Episode:", avg_eval_reward)
print("Average Steps per Episode:", avg_eval_steps)

# Plot the rewards and steps per episode
plt.figure(figsize=(30, 30))
plt.subplot(1, 2, 1)
plt.plot(eval_rewards)
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.title("Rewards per Episode")

plt.subplot(1, 2, 2)
plt.plot(eval_steps)
plt.xlabel("Episode")
plt.ylabel("Steps")
plt.title("Steps per Episode")

plt.tight_layout()
plt.show()


# 17/12/2023 - Tam giai quyet xong phan ham lost, dang thuc hien evaluation model







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