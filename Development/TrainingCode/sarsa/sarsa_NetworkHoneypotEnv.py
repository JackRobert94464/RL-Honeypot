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

import random
import itertools


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

        # self._action_spec = array_spec.BoundedArraySpec(
        #     shape=(M, K), dtype=np.int32, minimum=0, maximum=1, name='action')
        # print("Action spec:", self._action_spec)
        
        
        '''
        New action suggestion (06/04 ngay mai nho doc lai)
        [ 0 0 1 0 1 0 0 ]
        1 la cho se dat honeypot
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(1, K), dtype=np.int32, minimum=0, maximum=1, name='action')
        print("Action spec:", self._action_spec)
        '''
        
        # Define a list of numbers
        my_list = list(range(1, K+1))

        # Generate all possible two-element combinations
        # Convert the resulting iterator to a list
        combinations = list(itertools.combinations(my_list, M))

        # Convert the list of combinations to a dictionary
        self._action_space = dict(enumerate(combinations))

        print("Action space:", self._action_space)
        
        # Define the action spec as a bounded array spec
        # To differentiate, action space is a dict holding all the actions
        # While action spec is the spec of the action (how would an action look like)
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(1, M), dtype=np.int32, minimum=1, maximum=K, name='action')
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
        
        
        '''
        legacy code (since defender pick action directly from action space)
        # Initialize the matrix for the defender's view as zeros
        self._matrix = np.zeros((M, K), dtype=np.int32)
        print("Matrix:", self._matrix)
        '''
        

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
        # print("NTPG:", self._ntpg)
        # print("HTPG:", self._htpg)

        # Initialize attacker entrypoint
        # 20/12/2023 - fixed example, will be change later 
        # TODO: Dynamically locate this entrypoint
        self._current_attacker_node = list(ntpg.keys())[2]
        print("Initial Entrypoint:", self._current_attacker_node)
        # os.system('pause')

        #print(self.get_info())


    def action_spec(self):
        return self._action_spec
    
    def action_space(self):
        return self._action_space
    
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

        # print("NICR node after reset:", self.nicr_nodes)

        # Reset list for the nifr (fake resource node)
        self.nifr_nodes = []

        # Reset the state vector as an empty vector of 0s with size K
        # update 06/12/2023 - resetting state cause the next visit count to turn the state into 0, 
        # which in turn make Q guessing networks broken. So i will comment this out.
        # update 07/01/2024 - the above update was because of a false logic in the training code, each attacker action
        # should correspond with a defender action. This was fix, so we need to reset the env properly again.
        self._state = np.zeros(self.K, dtype=np.int32)
        # print("State vector after reset:", self._state)
        
        
        '''
        legacy code (since defender pick action directly from action space)
        # Reset the matrix for the defender's view as zeros
        self._matrix = np.zeros((self.M, self.K), dtype=np.int32)
        print("Matrix after reset:", self._matrix)
        '''
        
        
        # Reset the episode ended flag as False
        self._episode_ended = False
        # print("Episode ended flag after reset:", self._episode_ended)

        self._current_attacker_node = list(self._ntpg.keys())[2]

        # print(self.get_info())
        
        print("Environment reseted, attacker entrypoint and nicr:", self._current_attacker_node, self.nicr_nodes)

        # Return the state of the environment and information that it is the first step of the simulation
        return ts.restart(np.array([self._state], dtype=np.int32))
    
    
        
    
    '''
    06/04 xem + chinh lai ham nay luon
    legacy code
    def __is_action_valid(self, action):
        # Check if the action is a valid matrix of size m*k with values 0 or 1
        # Return True if the action is valid, False otherwise
        if action is None:
            return False
        
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
    '''
    
    def __is_action_valid(self, action):
        """Checks if the action is within the valid range of the action space."""
        
        print("Action:", action)
        # Convert action to tuple if it's a list or array and sort it
        if isinstance(action, (list, np.ndarray)):
            action = tuple(sorted(action)) if action.ndim > 1 else (action[0],)

        # Sort the action space values and check if the sorted action is in the sorted action space
        sorted_action_space = {k: tuple(sorted(v)) for k, v in self.action_space().items()}
        if action not in sorted_action_space.values():
            return False

        # Finally, check if the action length matches the expected size of the action space
        return len(action) == self._action_spec.shape[1]






    def __attacker_move_step(self):
        """Simulates one step of the attacker's move based on the NTPG and HTPG.
           Updates the state vector with the new attacked node.
        """

        # Get the current node information
        current_node = self._current_attacker_node
        current_node_index = list(self._ntpg.keys()).index(current_node)
        print("Current node index:", current_node_index)


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

            self._current_attacker_node = next_node
            print("Next node to attempt attack:", next_node)
            print(self._ntpg[next_node])

        else:
            print("No more possible routes, exit the loop. State vector after the attack:", self._state)


        # Update the NIFR list based on the action matrix
        self.__update_nifr_nodes(self.nifr_nodes)
        print("NIFR list after attack:", self.nifr_nodes)

    def __truong_attacker_move(self):
        # Simulates the attacker's move based on Truong's fixed flow.

        print("Work In Progress - WIP")

        # Fix the current_node to the very first node

    def __NMS_alert_based_attacker_movement(self):
        # Receive alert from NMS and update the observation space based on the alert.
        # API code to receive alert from NMS and digest it into the observation space and reward.

        # Fix the current_node to the very first node
        print("Work In Progress - WIP")


    def __is_nicr_attacked(self, nicr_nodes):
        # Check if any nicr (important resource node) is attacked or not
        # Return True if any nicr is attacked, False otherwise
        
        # Check if any nicr node is attacked in the state vector
        for i in nicr_nodes:
            if i < len(self._state) and self._state[i] == 1:
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

    '''
    06/04 xem + chinh lai ham nay luon
    Legacy code
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
    '''
    
    # Updates the NIFR list based on the action.
    def __update_nifr_nodes(self, action):
        # Append the action to the nifr_nodes list
        self.nifr_nodes = list(action)
        
        print("NIFR list after update:", self.nifr_nodes)
        
        
    
    def _step(self, action):
        # Check if the episode has ended
        if self._episode_ended:
            # If yes, reset the environment and return the initial state
            return self.reset()
        
        # Check if the maximum number of steps has been reached
        if self.current_step >= self.maxSteps:
            # If yes, end the episode and return the termination state and reward
            reward = -1
            print("Maximum number of steps reached, end the episode, agent lose")
            
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
            self._episode_ended = True
        
        # Check if the attacker has reached a nicr or a fake resource node
        if self.__is_nicr_attacked(self.nicr_nodes):
            # If yes, end the episode and return the termination state and reward
            reward = -1
            
            print("Attacker reached nicr, end the episode")
            print("Current node attacker residing in:", self._current_attacker_node)
            print("nicr nodes:", self.nicr_nodes)
            print("IP of the nicr node:", list(self._ntpg.keys())[self.nicr_nodes[0]])
            
            # os.system('pause')
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
            self._episode_ended = True
            
        if self.__is_nifr_attacked(self.nifr_nodes):
            # If yes, end the episode and return the termination state and reward
            reward = 1
            
            print("Attacker reached nifr, end the episode")
            
            print("Current node attacker residing in:", self._current_attacker_node)
            print("nifr nodes:", self.nifr_nodes)
            
            # os.system('pause')
            return ts.termination(np.array([self._state], dtype=np.int32), reward=1)
            self._episode_ended = True
        
        # Check if the action is valid
        # if self.__is_action_valid(action):
            
        # 04/04/2024 - Move the two end conditions to the top of the step function
        # The result actions start to get more variance, which i think is positive changes
        
        # If yes, update the matrix for the defender's view with the action
        # self._matrix = list(action)
        
        # print("Matrix after action:", self._matrix)
        # os.system('pause')
        
        # for random testing purpose, comment this out later
        

        # Update the NIFR list based on the action matrix.
        self.__update_nifr_nodes(action)
        
        # Simulate the attacker's move based on the NTPG and HTPG
        self.__attacker_move_step()
        
        reward = 0
        # Increment the step counter
        self.current_step += 1
        # If no, continue the episode and return the transition state and reward
        return ts.transition(np.array([self._state], dtype=np.int32), reward=0)
        
        

        '''
        legacy code
        check if the action is valid K*M matrix
        else:
            # If no, end the episode and return the termination state and reward
            reward = -1
            print("Invalid Action:", action)
            print("Invalid action, end the episode")
            
            return ts.termination(np.array([self._state], dtype=np.int32), reward=reward)
            self._episode_ended = True
        '''
        
        
          


'''
#environment = NetworkHoneypotEnv(10, 3, 7, ntpg, htpg)
#utils.validate_py_environment(environment, episodes=10)
# Load the NTPG and HTPG dictionaries
import misc


if os.name == 'nt':  # If the operating system is Windows
    ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg.csv")
    htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg.csv")
else:  # For other operating systems like Linux
    ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg_eval.csv")
    htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg_eval.csv")

# Load the topology param from TPGs
deception_nodes = misc.get_deception_nodes()
normal_nodes = misc.count_nodes(ntpg)
first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# Create a new environment for evaluation
eval_env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

print(eval_env)

if eval_env is not None:
    utils.validate_py_environment(eval_env, episodes=10)

'''







