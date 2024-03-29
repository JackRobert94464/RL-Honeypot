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
import os

import misc
import random
import csv


#  rule đặt honeypot: vị trí đặt ko được trùng với node đang có kẻ tấn công và node nicr  




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


    #------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------- TPGs Converter - WIP ------------------------------------------------
    #------------------------------------------------------------------------------------------------------------------
    def tpgs_converter(self, ntpg, htpg):
        return ntpg, htpg        
    


    def __init__(self, N, M, K, ntpg, htpg):

        # Initialize the spec for the environment
        self.N = N # Total amount of nodes (n)
        self.M = M # Number of deception nodes (m)
        self.K = K # Number of normal nodes (k)
        # self.P = P Probability of attacker moving to the next node

        # Pick a random node to be the nicr (important resource node)
        # As an example to test the environment, uncomment this for nicr hard-coded
        # self.nifr_nodes = [6]
        # self.nicr_nodes = [np.random.choice(K)]
        # 13/01/2024 (MUST FIX) - Fixed one nicr for presentation purpose comment this after DACN presentation
        # Real system will take nicr as input for init - not change it in reset
        # Train system will take nicr randomly
        self.nicr_nodes = [5]
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
        

        # 5/1/2024 - add TPG input for initialization
        self._ntpg = ntpg

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
    
    def get_ntpg(self):
        return self._ntpg
    
    def get_htpg(self):
        return self._htpg

    def _reset(self):

        # Reset the step counter
        self.current_step = 0

        # Reset the nicr node by random choosing a new one
        # self.nicr_nodes = [np.random.choice(self.K)]
        # 13/01/2024 (MUST FIX) - Fixed one nicr for presentation purpose comment this after DACN presentation
        self.nicr_nodes = [5]

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
        # self._ntpg = {} 
        
        # Reset the dictionary for the HTPG as an empty dictionary
        # self._htpg = {}
        
        # Reset the episode ended flag as False
        self._episode_ended = False
        print("Episode ended flag after reset:", self._episode_ended)

        self._current_attacker_node = list(self._ntpg.keys())[2]

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

    
    def attacker_move_step(self):
        """Simulates one step of the attacker's move based on the NTPG and HTPG.
           Updates the state vector with the new attacked node.
        """

        # Get the current node information
        current_node = self._current_attacker_node
        current_node_index = list(self._ntpg.keys()).index(current_node)
        print("Current node index:", current_node_index)

        # Prepare data for CSV
        data = {
            'current_node': current_node,
            'current_node_index': current_node_index,
            'EPSS_of_next_node': None,
            'next_node': None,
            'EPSS_of_connected_nodes': None,
            
        }

        # Check if the current node has possible routes
        # print("NTPG:", self._ntpg)
        print("current_node:", current_node)
        if self._ntpg.get(current_node):
            print("Attacking current node:", current_node)
            self._state[current_node_index] = 1
            print("Prepare to find the next node to attack")

            print("Possible routes from the current node:", self._ntpg.get(current_node))
            pop=[route[0] for route in self._ntpg.get(current_node)]
            wei=[(route[1] + route[2])/2 for route in self._ntpg.get(current_node)]

            print("Population:", pop)
            print("Weights:", wei)
            
            next_node = random.choices(
                population=pop, # the list to pick stuff out from in this case the ip of the next possible nodes
                weights=wei, # AVG OF BOTH ROOT AND USER
                k=1 # number of sample to pick from population
            )[0]

            data['EPSS_of_connected_nodes'] = [(route[1] + route[2])/2 for route in self._ntpg.get(current_node)]

            self._current_attacker_node = next_node
            print("Next node to attempt attack:", next_node)
            data['next_node'] = next_node
            print(self._ntpg[next_node])
            data['EPSS_of_next_node'] = (self._ntpg[next_node][0][1] + self._ntpg[next_node][0][2])/2

        else:
            print("No more possible routes, exit the loop. State vector after the attack:", self._state)

        # Write data to CSV
        with open('attacker_moves.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writerow(data)


    def __is_nicr_attacked(self, nicr_nodes):
        # Check if any nicr (important resource node) is attacked or not
        # Return True if any nicr is attacked, False otherwise
        
        # Check if any nicr node is attacked in the state vector
        for i in nicr_nodes:
            if i < len(self._state) and self._state[i] == 1:
                print("nicr node attacked:", i)
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
            if i < len(self._state) and self._state[i] == 1:
                # End the episode and calculate the reward
                print("nifr node attacked:", i)
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
                if len(nifr_nodes) > self.M:
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
        

        ######################################################################################
        #
        #
        #               DEPRECATED: ATTACKER SIMULATION DO NOT NEED TO CHECK ACTION
        #
        #
        ######################################################################################
        # Check if the action is valid
        # if self.__is_action_valid(action):
        # If yes, update the matrix for the defender's view with the action
        ######################################################################################
        #
        #
        #               DEPRECATED: ATTACKER SIMULATION DO NOT NEED TO CHECK ACTION
        #
        #
        ######################################################################################



        self._matrix = action

        # Update the NIFR list based on the action matrix.
        self.__update_nifr_nodes(self.nifr_nodes)
        
        # Simulate the attacker's move based on the NTPG and HTPG
        self.attacker_move_step()
        
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


        ######################################################################################
        #
        #
        #               DEPRECATED: ATTACKER SIMULATION DO NOT NEED TO CHECK ACTION
        #
        #
        ######################################################################################
        # else:
            # If no, end the episode and return the termination state and reward
            # print("Invalid Action:", action)
            # print("Invalid action, end the episode")
            # self._episode_ended = True
            # reward = -1
            # return ts.termination(np.array([self._state], dtype=np.int32), reward)
        ######################################################################################
        #
        #
        #               DEPRECATED: ATTACKER SIMULATION DO NOT NEED TO CHECK ACTION
        #
        #
        ######################################################################################
        





# Load the NTPG and HTPG dictionaries
ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_eval.csv")
htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_eval.csv")

# Load the topology param from TPGs
# deception_nodes = misc.get_deception_nodes()
deception_nodes = 5
normal_nodes = misc.count_nodes(ntpg)
first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# Create a new environment for evaluation
environment = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)
utils.validate_py_environment(environment, episodes=10)












