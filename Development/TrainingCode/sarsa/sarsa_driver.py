# Miscellaneous imports
import os
import misc

# tf_agent imports block
from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.environments import suite_gym
from tf_agents.trajectories import time_step as ts

# Local imports
from sarsa_NetworkHoneypotEnv import NetworkHoneypotEnv
from sarsa_agent import SarsaLearning

# Load the NTPG and HTPG dictionaries
if os.name == 'nt':  # If the operating system is Windows
    ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_big.csv")
    htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_big.csv")
else:  # For other operating systems like Linux
    ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg_eval_mini.csv")
    htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg_eval_mini.csv")

# Load the topology param from TPGs
normal_nodes = misc.count_nodes(ntpg)

# ---------------- Environment Creation Block ----------------
deception_nodes = 2 # Change this to the number of deception nodes you want to test

first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

# Create the environment
env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
tf_env = tf_py_environment.TFPyEnvironment(env)

timestep = tf_env.reset()
rewards = []

# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# ---------------- Environment Creation Block ----------------


# ---------------- Agent Creation Block ----------------     

epsilon = 0.1
numberEpisodes = 500
max_steps = 100
alpha = 0.1
gamma = 0.9


# create an object
SarsaAgent=SarsaLearning(env, epsilon, numberEpisodes, max_steps, alpha, gamma, total_permutations)
# run the learning process
# SarsaAgent.trainingEpisodes()

# ---------------- Agent Creation Block ----------------     





# ---------------- Training Block ----------------
for ep in range (numberEpisodes):
    SarsaAgent.trainingSingleEpisode()
    # if episode is a multiple of 50, append step count and calculate dsp
    if ep % 50 == 0:

        SarsaAgent.evaluateModel()


        SarsaAgent.step_globalcounter.append(SarsaAgent.getStepCount())
        
        # Add the current clock counter value to the time taken list
        SarsaAgent.time_taken.append(SarsaAgent.clock_counter)
        
# ---------------- Training Block ----------------







# -------------- DSP + Training Time Visualization --------------

import sarsa_dsp_visualizer
import sarsa_trainingtime_visualizer


print("Total steps: ", SarsaAgent.getGlobalStepCount())
print("Total DSP: ", SarsaAgent.getGlobalDSPCount())
print("Total Time: ", SarsaAgent.getGlobalTimeTaken())



# Visualize the Defense Success Probability (DSP) of our method
sarsa_dsp_visualizer.sarsa_dsp_visual(SarsaAgent.getGlobalStepCount(), SarsaAgent.getGlobalDSPCount())


# Visualize the training time taken of our method
sarsa_trainingtime_visualizer.sarsa_dsp_visual(SarsaAgent.getGlobalStepCount(), SarsaAgent.getGlobalTimeTaken())

# -------------- DSP + Training Time Visualization --------------


# -------------- Model Summary + Save --------------

# get the obtained rewards in every episode
rewards = SarsaAgent.sumRewardsEpisode

print(rewards)

# -------------- Model Summary + Save --------------

# -------------- Model Evaluation --------------

# Evaluate the model
print("Total evaluation rewards: ", SarsaAgent.evaluateModel())

# -------------- Model Evaluation --------------