# import the class
import HoneypotDDQN
# classical gym 
import gym
# instead of gym, import gymnasium 
#import gymnasium as gym

import numpy as np

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
import NetworkHoneypotEnv

# Defining parameters
gamma = 0.99
epsilon = 0.1

env = NetworkHoneypotEnv.NetworkHoneypotEnv(10, 3, 7, 0.8, 0.2)
# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
tf_env = tf_py_environment.TFPyEnvironment(env)


timestep = tf_env.reset()
rewards = []
steps = []
numberEpisodes = 10

for _ in range(numberEpisodes):
    episode_reward = 0
    episode_steps = 0
    while not env.is_last():
        action = np.random.choice(tf_env.action_spec().maximum + 1)
        timestep = tf_env.step(action)
        episode_steps += 1
        episode_reward += timestep.reward.numpy()
    rewards.append(episode_reward)
    steps.append(episode_steps)


# create an object
LearningQDeep=HoneypotDDQN.DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes)
# run the learning process
LearningQDeep.trainingEpisodes()
# get the obtained rewards in every episode
LearningQDeep.sumRewardsEpisode

print(rewards)

num_steps = np.sum(steps)
avg_length = np.mean(steps)
# avg_reward = np.mean(rewards)
# max_reward = np.max(rewards)
max_length = np.max(steps)

print('num_episodes:', numberEpisodes, 'num_steps:', num_steps)
print('avg_length', avg_length)
print('max_length', max_length)
# print('avg_length', avg_length, 'avg_reward:', avg_reward)
# print('max_length', max_length, 'max_reward:', max_reward)



















# select the parameters
# gamma=1
# probability parameter for the epsilon-greedy approach
# epsilon=0.1
# number of training episodes
# NOTE HERE THAT AFTER CERTAIN NUMBERS OF EPISODES, WHEN THE PARAMTERS ARE LEARNED
# THE EPISODE WILL BE LONG, AT THAT POINT YOU CAN STOP THE TRAINING PROCESS BY PRESSING CTRL+C
# DO NOT WORRY, THE PARAMETERS WILL BE MEMORIZED
# numberEpisodes=20
 
# create an object
# LearningQDeep=HoneypotDDQN.DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes)
# run the learning process
# LearningQDeep.trainingEpisodes()
# get the obtained rewards in every episode
# LearningQDeep.sumRewardsEpisode
 
#  summarize the model
# LearningQDeep.mainNetwork.summary()
# save the model, this is important, since it takes long time to train the model 
# and we will need model in another file to visualize the trained model performance
# LearningQDeep.mainNetwork.save("RL_Honeypot_trained_model_temp.keras")



# Visualizing after training

# load the model
# loaded_model = LearningQDeep.mainNetwok

# sumObtainedRewards=0
# simulate the learned policy for verification
 
 
# create the environment, here you need to keep render_mode='rgb_array' since otherwise it will not generate the movie
# env = gym.make("CartPole-v1",render_mode='rgb_array')


# Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
# env = tf_py_environment.TFPyEnvironment(NetworkHoneypotEnv.NetworkHoneypotEnv())


# reset the environment
# (currentState,prob)=env.reset()
 
# Wrapper for recording the video
# https://gymnasium.farama.org/api/wrappers/misc_wrappers/#gymnasium.wrappers.RenderCollection
# the name of the folder in which the video is stored is "stored_video"
# length of the video in the number of simulation steps
# if we do not specify the length, the video will be recorded until the end of the episode 
# that is, when terminalState becomes TRUE
# just make sure that this parameter is smaller than the expected number of 
# time steps within an episode
# for some reason this parameter does not produce the expected results, for smaller than 450 it gives OK results
# video_length=400
# the step_trigger parameter is set to 1 in order to ensure that we record the video every step
#env = gym.wrappers.RecordVideo(env, 'stored_video',step_trigger = lambda x: x == 1, video_length=video_length)
# env = gym.wrappers.RecordVideo(env, 'stored_video_ddqn', video_length=video_length)
 
 
# since the initial state is not a terminal state, set this flag to false
# terminalState=False
'''while not terminalState:
    # get the Q-value (1 by 2 vector)
    Qvalues=loaded_model.predict(currentState.reshape(1,4))
    # select the action that gives the max Qvalue
    action=np.random.choice(np.where(Qvalues[0,:]==np.max(Qvalues[0,:]))[0])
    # if you want random actions for comparison
    #action = env.action_space.sample()
    # apply the action
    (currentState, currentReward, terminalState,_,_) = env.step(action)
    # sum the rewards
    sumObtainedRewards+=currentReward
'''
env.reset()
env.close()