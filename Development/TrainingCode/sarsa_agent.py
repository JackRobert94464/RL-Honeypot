# https://www.geeksforgeeks.org/sarsa-reinforcement-learning/

# Importing libraries

import numpy as np
import os
import misc
from NetworkHoneypotEnv import NetworkHoneypotEnv


# Policy
# - The policy is a function that maps states to actions.
# - The policy is represented by a neural network that takes the state as input and outputs the action.
# - The policy is trained by the agent to maximize the total reward.
# - The policy is updated using the SARSA algorithm, which is an on-policy reinforcement learning algorithm.
# - The policy is updated by minimizing the loss between the predicted action values and the target action values.
# - The policy is updated using the Adam optimizer with a learning rate of 0.001.
# - The policy is updated using the Huber loss function, which is less sensitive to outliers than the mean squared error loss function.







class SarsaLearning:
    def __init__(self, env, epsilon, numberEpisodes, max_steps, alpha, gamma):

        self.env=env
        # Testing purposes
        # self.env=NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)
        
        
        self.epsilon=epsilon
        self.numberEpisodes=numberEpisodes

        #Defining the different parameters

        self.max_steps=max_steps
        self.alpha=alpha
        self.gamma=gamma

        #Initializing the Q-matrix
        Q = np.zeros((env.observation_space.n, env.action_space.n))
        
    #Function to choose the next action
    def selectAction(self, state):
        action=0
        if np.random.uniform(0, 1) < self.epsilon:
            action = self.env.action_space.sample()
        else:
            action = np.argmax(Q[state, :])
        return action

    #Function to learn the Q-value
    def updateQvalues(self, state, state2, reward, action, action2):
        predict = self.Q[state, action]
        target = reward + self.gamma * self.Q[state2, action2]
        self.Q[state, action] = self.Q[state, action] + self.alpha * (target - predict)
        
    def trainingEpisodes(self):
        
        # Starting the SARSA learning
        for episode in range(self.numberEpisodes):
            t = 0
            state1 = self.env.reset()
            action1 = self.selectAction(state1)

            while t < self.max_steps:
                #Visualizing the training
                self.env.render()
                
                #Getting the next state
                state2, reward, done, info = self.env.step(action1)

                #Choosing the next action
                action2 = self.selectAction(state2)
                
                #Learning the Q-value
                self.updateQvalues(state1, state2, reward, action1, action2)

                state1 = state2
                action1 = action2
                
                #Updating the respective vaLues
                t += 1
                reward += 1
                
                #If at the end of learning process
                if done:
                    break
        
        
        


        
    