# https://www.geeksforgeeks.org/sarsa-reinforcement-learning/

# Importing libraries

import numpy as np
import random
import os
import misc
from Development.TrainingCode.sarsa.sarsa_NetworkHoneypotEnv import NetworkHoneypotEnv


# Policy
# - The policy is a function that maps states to actions.
# - The policy is represented by a neural network that takes the state as input and outputs the action.
# - The policy is trained by the agent to maximize the total reward.
# - The policy is updated using the SARSA algorithm, which is an on-policy reinforcement learning algorithm.
# - The policy is updated by minimizing the loss between the predicted action values and the target action values.
# - The policy is updated using the Adam optimizer with a learning rate of 0.001.
# - The policy is updated using the Huber loss function, which is less sensitive to outliers than the mean squared error loss function.







class SarsaLearning:
    def __init__(self, env, epsilon, numberEpisodes, max_steps, alpha, gamma, total_permutations):

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

        #Initializing the Q-matrix
        # Q = np.zeros((env.observation_space.n, env.action_space.n))
        self.Q = np.zeros((int(2 ** self.env.K), int(self.total_permutations)))
        
    #Function to choose the next action
    def selectAction(self, state):
        action=0
        if np.random.uniform(0, 1) < self.epsilon:
            action_space_values = list(self.env.action_space().values())        
            random_action = random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
            return action
        else:
            print("State: ", state)
            print("BIG BAD Q: ", self.Q)

            observation_flat = state.observation[0]

            state_index = int("".join(str(int(x)) for x in observation_flat), 2)
            print("State index: ", state_index)
            os.system("pause")

            max_index = np.argmax(self.Q[state_index, :])
            action = self.index_to_action(max_index)
        return action
    
    def index_to_action(self, index):
        
        action_matrix = self.env.action_space()[index]

        return action_matrix

    #Function to learn the Q-value
    def updateQvalues(self, state, state2, reward, action, action2):
        predict = self.Q[state, action]
        target = reward + self.gamma * self.Q[state2, action2]
        self.Q[state, action] = self.Q[state, action] + self.alpha * (target - predict)
        
    def trainingEpisodes(self):
        
        # Starting the SARSA learning
        for episode in range(self.numberEpisodes):

            # list that store rewards in each episode to keep track of convergence
            rewardsEpisode=[]

            t = 0
            state1 = self.env.reset()
            action1 = self.selectAction(state1)

            while t < self.max_steps:
                #Visualizing the training
                # self.env.render()
                
                #Getting the next state
                state2, reward, done, info = self.env.step(action1)

                
                print("ACTUAL STEP: ", self.env.step(action1))
                print("State 2: ", state2)
                print("Reward: ", reward)
                print("Done: ", done)
                print("Info: ", info)

                #Choosing the next action
                action2 = self.selectAction(state2)
                
                #Learning the Q-value
                self.updateQvalues(state1, state2, reward, action1, action2)

                state1 = state2
                action1 = action2
                
                #Updating the respective vaLues
                t += 1
                reward += 1

                rewardsEpisode.append(reward)
                
                #If at the end of learning process
                if done:
                    break

        print("Sum of rewards {}".format(np.sum(rewardsEpisode)))        
        self.sumRewardsEpisode.append(np.sum(rewardsEpisode)) 
        
        
        


        
    