# https://www.geeksforgeeks.org/sarsa-reinforcement-learning/

# Importing libraries

import numpy as np
import random
import os
import misc
import tensorflow as tf
import time

# import FNR FPR simulation code
from fnr_fpr_test.fnrfpr_calc_v2 import simulate_alert_training
import random
import string

# Policy
# - The policy is a function that maps states to actions.
# - The policy is represented by a neural network that takes the state as input and outputs the action.
# - The policy is trained by the agent to maximize the total reward.
# - The policy is updated using the SARSA algorithm, which is an on-policy reinforcement learning algorithm.
# - The policy is updated by minimizing the loss between the predicted action values and the target action values.
# - The policy is updated using the Adam optimizer with a learning rate of 0.001.
# - The policy is updated using the Huber loss function, which is less sensitive to outliers than the mean squared error loss function.

class SARSAQNetwork:
    def __init__(self, observation_space_size, action_space_size):
        # Define the neural network structure here
        self.model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(observation_space_size,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(action_space_size)
        ])
        # Compile the model with an optimizer and a loss function
        self.model.compile(optimizer='adam', loss='mse')  # You can choose the optimizer and loss function that fit your problem
        # Print the model summary
        self.model.summary()
        
        
    def predict(self, observation):
        # Forward pass through the network to get Q-values
        # print("Raw prediction: ", self.model.predict(observation))
        return self.model.predict(observation)
        



class SarsaLearning:
    def __init__(self, env, epsilon, numberEpisodes, max_steps, alpha, gamma, total_permutations, fnr, fpr):

        self.env=env
        # Testing purposes
        # self.env=NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

        # this sum is used to store the sum of rewards obtained during each training episode
        self.sumRewardsEpisode=[]
        
        
        self.epsilon=epsilon
        self.numberEpisodes=numberEpisodes

        #Defining the different parameters

        self.max_steps=max_steps
        self.alpha=alpha
        self.gamma=gamma

        self.total_permutations=total_permutations

        self.num_action_space = len(self.env.action_space())  # Example action space size, adjust based on the environment
        self.num_observation_space = self.env.K  # Example observation space size, adjust based on the environment
        print("Action space size: ", self.num_action_space)
        print("Observation space size: ", self.num_observation_space)

        # Create the Q-network
        self.mainNetwork = SARSAQNetwork(self.num_observation_space, self.num_action_space)

        #Initializing the Q-matrix
        # Q = np.zeros((env.observation_space.n, env.action_space.n))
        # self.Q = np.zeros((int(2 ** self.env.K), int(self.total_permutations)))

        # initialize step counter (time/dsp)
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

        # number of episode won
        # TODO: replace this later
        self.episodeWon = 0
        
        self.currentTrainingEpisode = 0
        
        self._fnr = fnr
        self._fpr = fpr



        
    #Function to choose the next action
    def selectAction(self, state):
        # Reshape the state observation to match the input shape of the Q-network
        state = state.reshape(1, -1)

        # Get the Q-values for the current state from the Q-network
        q_values = self.mainNetwork.predict(state)[0]

        # Choose the action based on the epsilon-greedy policy
        if np.random.uniform(0, 1) < self.epsilon:
            # Choose a random action
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
        else:
            # Choose the action with the maximum Q-value
            action_index = np.argmax(q_values)
            action = self.index_to_action(action_index)

        return action
    
    # Function to infer the action from the saved model
    def selectActionEval(self, state, episode, trained_model):
        state = state.reshape(1, -1)
        q_values = trained_model.predict(state)[0]
        
        # Choose the action based on the epsilon-greedy policy
        if np.random.uniform(0, 1) < self.epsilon:
            # Choose a random action
            action_space_values = list(self.env.action_space().values())
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
        else:
            # Choose the action with the maximum Q-value
            action_index = np.argmax(q_values)
            action = self.index_to_action(action_index)

        return action
    
    def index_to_action(self, index):
        
        action_matrix = self.env.action_space()[index]

        return action_matrix
    

    # Function to learn the Q-value
    # SARSA update rule with function approximation
    def updateQvalues(self, state1, action1, reward, state2, action2, done):
        # Reshape the observations to fit the neural network input
        state = state1.reshape(1, -1)
        state2 = state2.reshape(1, -1)
        
        # Get Q-values for the current state and the next state
        current_q_values = self.mainNetwork.predict(state)
        next_q_values = self.mainNetwork.predict(state2)

        # print("Current Q-values: ", current_q_values)
        # print("Next Q-values: ", next_q_values)
        # print("Action 1: ", action1)
        # print("Action 2: ", action2)
        # print("Action space: ", self.env.action_space())
        
        # Find the index of the action1 and action2 in the action space
        # Convert the action1 array to a tuple
        action1_tuple = tuple(action1)

        # Find the index of the action1 and action2 in the action space
        action_index = list(self.env.action_space().keys())[list(self.env.action_space().values()).index(action1_tuple)]

        action2_tuple = tuple(action2)

        action2_index = list(self.env.action_space().keys())[list(self.env.action_space().values()).index(action2_tuple)] if not done else 0
        
        # SARSA target uses the Q-value of the next state-action pair
        target = reward + self.gamma * next_q_values[0][action2_index] * (1 - int(done))
        
        # Update the Q-values
        target_vector = current_q_values.copy()
        target_vector[0][action_index] = target
        
        # Train the network with the state as input and target vector as desired output
        self.mainNetwork.model.fit(state, target_vector, epochs=1, verbose=0)


    def trainingEpisodes(self):
        
        # Starting the SARSA learning
        for episode in range(self.numberEpisodes):
            
            # Time/DSP calculation
            # reset the step count for the new episode
            step_count = 0

            # list that store rewards in each episode to keep track of convergence
            rewardsEpisode=[]

            t = 0
            state1 = self.env.reset()
            action1 = self.selectAction(state1)

            while t < self.max_steps:
                #Visualizing the training
                # self.env.render()


                # Time/DSP calculation
                # Start the timer
                start_time = time.time()
                # Time/DSP calculation
                
                #Getting the next state
                state2 = self.env.step(action1)
                
                # print("State 1 observation: ", state1)
                # print("Action 1: ", action1)
                
                (discount, state2Observation, reward, terminalState) = (state1.discount, state2.observation, state2.reward, self.env.is_last())
                # (discount, nextStateObservation, reward, terminalState) = (currentState.discount, nextState.observation, nextState.reward, self.env.is_last())
                # print("State 2: ", state2)
                # print("State 2 observation: ", state2Observation)
                # print("Reward: ", reward)
                # print("Done: ", terminalState)
                # print("Discount: ", discount)

                #Choosing the next action
                action2 = self.selectAction(state2)
                
                #Learning the Q-value
                # self, state1, action1, reward, state2, action2, done
                self.updateQvalues(state1, action1, reward, state2, action2, terminalState)

                state1 = state2
                action1 = action2
                
                #Updating the respective vaLues
                t += 1
                reward += 1

                rewardsEpisode.append(reward)


                # increment the step count
                step_count += 1

                # Calculate the time taken for this step and add it to the clock counter
                self.clock_counter += time.time() - start_time
                # Time/DSP calculation

                
                #If at the end of learning process
                if terminalState:
                    break


            # Time/DSP calculation
            # add the step count to the global step counter
            self.step_counter = step_count


        print("Sum of rewards {}".format(np.sum(rewardsEpisode)))        
        self.sumRewardsEpisode.append(np.sum(rewardsEpisode)) 
        
    def trainingSingleEpisodes(self):
        step_count = 0
        rewardsEpisode = []

        t = 0
        state1 = self.env.reset()
        
        # Initialize alerted observation (Defender's view of the network through Network Monitoring System)
        # alerted_initial = [0] * len(state1.observation.reshape(1, -1)[0])
        # alerted_observation1 = simulate_alert_training(state1.observation.reshape(1, -1)[0], alerted_initial, self._fnr, self._fpr)

        alerted_observation1 = self.env.get_alerted_state()
        alerted_observation1 = np.array(alerted_observation1)
        alerted_observation1 = np.expand_dims(alerted_observation1, axis=0)

        action1 = self.selectAction(alerted_observation1)

        while t < self.max_steps:
            start_time = time.time()

            state2 = self.env.step(action1)

            (discount, state2Observation, reward, terminalState) = (state1.discount, state2.observation, state2.reward, self.env.is_last())
            
            # Update alerted observation
            # alerted_observation2 = simulate_alert_training(state2Observation.reshape(1, -1)[0], alerted_observation1[0], self._fnr, self._fpr)
            alerted_observation2 = self.env.get_alerted_state()
            alerted_observation2 = np.array(alerted_observation2)
            alerted_observation2 = np.expand_dims(alerted_observation2, axis=0)

            action2 = self.selectAction(alerted_observation2)

            self.updateQvalues(alerted_observation1, action1, reward, alerted_observation2, action2, terminalState)

            state1 = state2
            action1 = action2
            alerted_observation1 = alerted_observation2  # Update alerted state for next iteration

            t += 1
            reward += 1

            rewardsEpisode.append(reward)

            if reward == 1:
                self.episodeWon += 1

            step_count += 1
            self.step_counter += 1
            if self.step_counter in [250, 500, 750, 1000, 2000, 5000, 10000, 20000, 30000]:
                break
            self.clock_counter += time.time() - start_time

            if terminalState:
                break
        
        self.time_taken.append(self.clock_counter)
        
    def evaluateModel(self):

        total_episode_rewards = []

        for episode in range(50):  

            # Initialize the state
            state = self.env.reset()
            done = False
            current_reward = 0

            while not done:
                # Select action based on the current policy (greedy with respect to Q-values)
                action = self.selectAction(state)

                # Perform the action in the environment
                state2 = self.env.step(action)

                # Update the total reward
                current_reward += state2.reward

                # Update the current state
                state = state2

                # Check if the episode is done
                done = self.env.is_last()

            total_episode_rewards.append(current_reward)
            
    
            dsp = total_episode_rewards.count(1) / (episode+1)
            print("Defense Success Probability: ", dsp)
                
            # os.system("pause")
            self.dsp_globalcounter.append(dsp)

        return total_episode_rewards
    
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
    
    def updateTrainingEpisode(self, episode):
        self.currentTrainingEpisode = episode
        
    def updateModelPath(self, path):
        self._modelPath = path
        
    def retrieveModelPath(self):
        return self._modelPath
    
    def saveModel(self):
        if os.name == 'nt':
            os.makedirs("./TrainedModel/weighted_random_attacker/SARSA_1_INPUT", exist_ok=True)
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.mainNetwork.model.save(f"./TrainedModel/weighted_random_attacker/SARSA_1_INPUT/RL_Honeypot_SARSA_win_ver{self.getStepCount()}_{token}.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/SARSA_1_INPUT/RL_Honeypot_SARSA_win_ver{self.getStepCount()}_{token}.keras")
        else:
            os.makedirs("./TrainedModel/weighted_random_attacker/SARSA_1_INPUT", exist_ok=True)
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.mainNetwork.model.save(f"./TrainedModel/weighted_random_attacker/SARSA_1_INPUT/RL_Honeypot_SARSA_linux_ver{self.getStepCount()}_{token}.keras")
            self.updateModelPath(f"./TrainedModel/weighted_random_attacker/SARSA_1_INPUT/RL_Honeypot_SARSA_linux_ver{self.getStepCount()}_{token}.keras")
    