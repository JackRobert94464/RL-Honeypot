# https://www.geeksforgeeks.org/sarsa-reinforcement-learning/

# Importing libraries

import numpy as np


# Policy
# - The policy is a function that maps states to actions.
# - The policy is represented by a neural network that takes the state as input and outputs the action.
# - The policy is trained by the agent to maximize the total reward.
# - The policy is updated using the SARSA algorithm, which is an on-policy reinforcement learning algorithm.
# - The policy is updated by minimizing the loss between the predicted action values and the target action values.
# - The policy is updated using the Adam optimizer with a learning rate of 0.001.
# - The policy is updated using the Huber loss function, which is less sensitive to outliers than the mean squared error loss function.


class DoubleDeepQLearning:
    def __init__(self, env, epsilon, numberEpisodes, max_steps, alpha, gamma):

        self.env=env
        self.epsilon=epsilon
        self.numberEpisodes=numberEpisodes

        #Defining the different parameters

        self.max_steps=max_steps
        self.alpha=alpha
        self.gamma=gamma

        #Initializing the Q-matrix
        Q = np.zeros((env.observation_space.n, env.action_space.n))


        
    