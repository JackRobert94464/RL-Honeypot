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



# Sure, I can try to implement the answer I gave you above to this code. Here is one possible way to do it:

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
        
        for i in range(N):
            # Generate a random IP address for each node
            ip = f"192.168.0.{i+1}"
            
            # Add the node IP address as a key to the NTPG and HTPG dictionaries
            self._ntpg[ip] = []
            self._htpg[ip] = {}
            
            # Generate a random number of edges from this node to other nodes in the NTPG
            num_edges = np.random.randint(0, N)
            
            # Choose num_edges random nodes as the destinations of the edges
            dest_nodes = np.random.choice(N, size=num_edges, replace=False)
            
            # For each destination node, generate a random user privilege and root privilege
            for j in dest_nodes:
                up = np.random.uniform(0, 1) # User privilege
                rp = np.random.uniform(0, 1) # Root privilege
                
                # Add the tuple (up, rp) as a value to the NTPG dictionary with the destination node IP address as a key
                dest_ip = f"192.168.0.{j+1}"
                self._ntpg[ip].append((dest_ip, up, rp))
                
            # Generate a random number of tuples for this node in the HTPG
            num_tuples = np.random.randint(0, 2)
            
            # For each tuple, generate a random host and privilege
            for k in range(num_tuples):
                host = np.random.choice(N) + 1 # Host number
                host_ip = f"192.168.0.{host}" # Host IP address
                privilege = np.random.choice(["User", "Root"]) # Privilege
                
                # Add the tuple (host_ip, privilege) as a key to the HTPG dictionary with an empty list as a value
                self._htpg[ip][(host_ip, privilege)] = []
                
                # Generate a random number of edges from this tuple to other tuples in the HTPG
                num_edges = np.random.randint(0, N)
                
                # Choose num_edges random tuples as the destinations of the edges
                dest_tuples = np.random.choice(N*2, size=num_edges, replace=False)
                
                # For each destination tuple, generate a random service, vulnerability, and probability
                for l in dest_tuples:
                    dest_host = l // 2 + 1 # Destination host number
                    dest_host_ip = f"192.168.0.{dest_host}" # Destination host IP address
                    dest_privilege = ["User", "Root"][l % 2] # Destination privilege
                    
                    service = f"Service{chr(ord('A') + l)}" # Service name
                    vulnerability = f"Vul{service}{l+1}" # Vulnerability name
                    probability = np.random.uniform(0, 1) # Probability
                    
                    # Add the triple (service, vulnerability, probability) as a value to the HTPG dictionary with the destination tuple as a key
                    self._htpg[ip][(host_ip, privilege)].append((service, vulnerability, probability, (dest_host_ip, dest_privilege)))
        
        # Print the state vector, the matrix, the NTPG, and the HTPG for debugging purposes
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
        # Here I will use the same code as in the __init__ function
        for i in range(self.N):
            # Generate a random IP address for each node
            ip = f"192.168.0.{i+1}"
            
            # Add the node IP address as a key to the NTPG and HTPG dictionaries
            self._ntpg[ip] = []
            self._htpg[ip] = {}
            
            # Generate a random number of edges from this node to other nodes in the NTPG
            num_edges = np.random.randint(0, self.N)
            
            # Choose num_edges random nodes as the destinations of the edges
            dest_nodes = np.random.choice(self.N, size=num_edges, replace=False)
            
            # For each destination node, generate a random user privilege and root privilege
            for j in dest_nodes:
                up = np.random.uniform(0, 1) # User privilege
                rp = np.random.uniform(0, 1) # Root privilege
                
                # Add the tuple (up, rp) as a value to the NTPG dictionary with the destination node IP address as a key
                dest_ip = f"192.168.0.{j+1}"
                self._ntpg[ip].append((dest_ip, up, rp))
                
            # Generate a random number of tuples for this node in the HTPG
            num_tuples = np.random.randint(0, 2)
            
            # For each tuple, generate a random host and privilege
            for k in range(num_tuples):
                host = np.random.choice(self.N) + 1 # Host number
                host_ip = f"192.168.0.{host}" # Host IP address
                privilege = np.random.choice(["User", "Root"]) # Privilege
                
                # Add the tuple (host_ip, privilege) as a key to the HTPG dictionary with an empty list as a value
                self._htpg[ip][(host_ip, privilege)] = []
                
                # Generate a random number of edges from this tuple to other tuples in the HTPG
                num_edges = np.random.randint(0, self.N)
                
                # Choose num_edges random tuples as the destinations of the edges
                dest_tuples = np.random.choice(self.N*2, size=num_edges, replace=False)
                
                # For each destination tuple, generate a random service, vulnerability, and probability
                for l in dest_tuples:
                    dest_host = l // 2 + 1 # Destination host number
                    dest_host_ip = f"192.168.0.{dest_host}" # Destination host IP address
                    dest_privilege = ["User", "Root"][l % 2] # Destination privilege
                    
                    service = f"Service{chr(ord('A') + l)}" # Service name
                    vulnerability = f"Vul{service}{l+1}" # Vulnerability name
                    probability = np.random.uniform(0, 1) # Probability
                    
                    # Add the triple (service, vulnerability, probability) as a value to the HTPG dictionary with the destination tuple as a key
                    self._htpg[ip][(host_ip, privilege)].append((service, vulnerability, probability, (dest_host_ip, dest_privilege)))
        
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
        # Simulate the attacker's move based on the NTPG and HTPG
        # Update the state vector with the new attacked node
        
        # Get the current attacked node IP address from the state vector
        current_node = f"192.168.0.{np.where(self._state == 1)[0][0] + 1}"
        print("CURRENT NODE:", current_node)
        
        # Get the list of possible destination nodes from the NTPG dictionary
        dest_nodes = self._ntpg[current_node]
        print("DESTINATION NODES", dest_nodes)
        
        # If there are no possible destination nodes, do nothing and return
        if len(dest_nodes) == 0:
            return
        
        # Calculate the probability of moving to each destination node based on the user privilege and root privilege
        probs = [up * self.P + rp * self.Q for _, up, rp in dest_nodes]
        print("PROBABILITIES:", probs)
        
        # Normalize the probabilities to sum up to 1
        probs = probs / np.sum(probs)
        print("PROBABILITIES:", probs)
        
        # Choose a random destination node based on the probabilities
        dest_node = np.random.choice([node for node, _, _ in dest_nodes], p=probs)
        print("DESTINATION NODES CHOICE", dest_nodes)
        
        # Get the index of the destination node from its IP address
        dest_index = int(dest_node.split(".")[-1]) - 1
        print("DESTINATION NODES INDEX", dest_index)
        
        # Check if the destination node is already attacked or not
        if self._state[dest_index] == 1:
            # If yes, do nothing and return
            return
        
        # Get the list of possible tuples for the current node in the HTPG dictionary
        current_tuples = self._htpg[current_node]
        print("CURRENT TUPLES:", current_tuples)
        
        # Get the list of possible tuples for the destination node in the HTPG dictionary
        dest_tuples = self._htpg[dest_node]
        print("DESTINATION TUPLES:", dest_tuples)
        
        # Calculate the probability of moving from each current tuple to each destination tuple based on the service, vulnerability, and probability
        # probs = []
        for ct in current_tuples:
            for dt in dest_tuples:
                for service, vulnerability, probability, dest_tuple in current_tuples[ct]:
                    if dest_tuple == dt:
                        probs.append(probability)
        
        # Normalize the probabilities to sum up to 1
        probs = probs / np.sum(probs)
        print("PROBABILITIES AFTER SUM TO 1:", probs)
        
        # Choose a random tuple pair based on the probabilities
        pair_index = np.random.choice(len(probs), p=probs)
        print("PAIR INDEX:", pair_index)
        print("LENGTH DEST TUPLES", len(dest_tuples))
        
        # Get the current tuple and destination tuple from their indices
        if len(dest_tuples) == 0:
            ct_index = 0
            dt_index = 0
            print("NO MORE DESTINATION CAN BE REACHED")
            return
        else:
            ct_index = pair_index // len(dest_tuples)
            dt_index = pair_index % len(dest_tuples)

        print("CURRENT TUPLE INDEX:", ct_index)
        print("DESTINATION TUPLE INDEX:", dt_index)

        if ct_index == 0 or dt_index == 0:
            print("NO MORE DESTINATION CAN BE REACHED")
            return
        
        current_tuple = list(current_tuples.keys())[ct_index]
        dest_tuple = list(dest_tuples.keys())[dt_index]
        
        # Check if the attacker has obtained root privilege on both tuples or not
        if current_tuple[1] == "Root" and dest_tuple[1] == "Root":
            # If yes, update the state vector with the new attacked node and return
            self._state[dest_index] = 1
            print("ATTACKER HAS OBTAINED ROOT PRIVILEGE")
            return
        
        # Otherwise, do nothing and return
        print("ATTACKER WAS NOT ABLE TO OBTAINED ROOT PRIVILEGE")
        return

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