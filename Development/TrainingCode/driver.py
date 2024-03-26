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
from NetworkHoneypotEnv import NetworkHoneypotEnv

# import the agent
from ddqn_agent_headless import DoubleDeepQLearning

 

# import miscellaneous funtions
import misc

import os

# Defining parameters
gamma = 0.9
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

'''
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
'''


ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg.csv")
# os.system("pause")
htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg.csv")




deception_nodes = misc.random_deception_amount(ntpg)
normal_nodes = misc.count_nodes(ntpg)
first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

print("First parameter:", first_parameter)
print("Deception nodes:", deception_nodes)
print("Normal nodes:", normal_nodes)

# os.system("pause")

env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

# os.system("pause")
# exit(0)


# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
tf_env = tf_py_environment.TFPyEnvironment(env)


timestep = tf_env.reset()
rewards = []
numberEpisodes = 150


# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# create an object
LearningQDeep=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations)
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








# 17/12/2023 - Tam giai quyet xong phan ham lost, dang thuc hien evaluation model

# CONTRUCTION ZONE

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


# Attacker themselves move with each "step" in the environment too
# Does this code represent that? or just a static mapping?
# 14/01/2023 Remove this function (logic fault), attacker will move with each step in the environment
# 18/02/2024 Attacker simulate code is use for training only - for production we will need to demo in some way