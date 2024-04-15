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
import math

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
# from NetworkHoneypotEnv import NetworkHoneypotEnv

# import test env
from Development.TrainingCode.demodsp.demodsp_NetworkHoneypotEnv import NetworkHoneypotEnv

# import the agent
from Development.TrainingCode.demodsp.demodsp_ddqn_agent_headless import DoubleDeepQLearning

 

# import miscellaneous funtions
import misc

import os

import ddqn_dsp_visualizer
import ddqn_trainingtime_visualizer




# Defining parameters
gamma = 0.9
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1


if os.name == 'nt':  # If the operating system is Windows
        ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg.csv")
        htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg.csv")
else:  # For other operating systems like Linux
        ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg.csv")
        htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg.csv")





normal_nodes = misc.count_nodes(ntpg)
print("Normal nodes:", normal_nodes)

# os.system("pause")



'''
Short training for testing out the dsp graphing function

For debugging purpose, uncomment this
'''

deception_nodes = 2 # Change this to the number of deception nodes you want to test

first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

# Create the environment
env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
tf_env = tf_py_environment.TFPyEnvironment(env)


timestep = tf_env.reset()
rewards = []
numberEpisodes = 100

# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# create an object
LearningQDeep=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations)
# run the learning process
LearningQDeep.trainingEpisodes()

import ddqn_dsp_visualizer
import ddqn_trainingtime_visualizer


print("Total steps: ", LearningQDeep.getGlobalStepCount())
print("Total DSP: ", LearningQDeep.getGlobalDSPCount())
print("Total Time: ", LearningQDeep.getGlobalTimeTaken())



# Visualize the Defense Success Probability (DSP) of our method
ddqn_dsp_visualizer.ddqn_dsp_visual(LearningQDeep.getStepInternationalCounter(), LearningQDeep.getEvalDSP())


# Visualize the training time taken of our method
ddqn_trainingtime_visualizer.ddqn_dsp_visual(LearningQDeep.getStepInternationalCounter(), LearningQDeep.getInternationalTimeTaken())


# get the obtained rewards in every episode
LearningQDeep.sumRewardsEpisode

print(rewards)

#  summarize the model
LearningQDeep.mainNetwork.summary()
# save the model, this is important, since it takes long time to train the model 
# and we will need model in another file to visualize the trained model performance
if os.name == 'nt':  # If the operating system is Windows
        LearningQDeep.mainNetwork.save(".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_weighted_attacker_1to5_decoy_win.keras")
else:  # For other operating systems like Linux
        LearningQDeep.mainNetwork.save("./TrainedModel/weighted_random_attacker/RL_Honeypot_weighted_attacker_1to5_decoy_linux.keras")
