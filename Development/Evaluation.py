import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from NetworkHoneypotEnv import NetworkHoneypotEnv
from tf_agents.environments import tf_py_environment
from NetworkHoneypotEnv import DoubleDeepQLearning

# Load the trained model
trained_model = tf.keras.models.load_model("RL_Honeypot_trained_model_temp.keras")

###########################################################################
#    EVALUATION CODE
###########################################################################   


import pandas as pd
import matplotlib.pyplot as plt





# Defining parameters
gamma = 0.9
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

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


# Extract nodes from the ntpg dictionary
your_nodes_list = list(ntpg.keys())

# Extract edges from the ntpg dictionary
your_edges_list = [(node, edge[0]) for node in ntpg for edge in ntpg[node]]







# Load the trained model
trained_model = tf.keras.models.load_model("RL_Honeypot_trained_model_temp.keras")

# Create a new environment for evaluation
eval_env = NetworkHoneypotEnv(10, 3, 7, 0.8, ntpg, htpg)
# tf_eval_env = tf_py_environment.TFPyEnvironment(eval_env)

# create an object
LearningQDeep=DoubleDeepQLearning(eval,gamma,epsilon,3)

# Reset the environment
eval_time_step = eval_env.reset()

# Initialize variables for tracking rewards and steps
eval_rewards = []
eval_steps = []

# Evaluate the model for a certain number of episodes
eval_episodes = 3
eval_rewards = []
eval_steps = []

for _ in range(eval_episodes):
    episode_reward = 0
    episode_steps = 0

    print("------------------------------------------------------------------------------------------------------------------------")
    print("Evaluating episode number: ", eval_episodes)
    print("------------------------------------------------------------------------------------------------------------------------")

    # Run the evaluation episode
    while not eval_time_step.is_last():
        # Get the action from the trained model
        action = LearningQDeep.selectActionEval(eval_time_step.observation, _, trained_model)
        print("ACTION SELECTED:", action)
        # Take a step in the environment
        eval_time_step = eval_env.step(action)
        print("EVAL TIME STEP:", eval_time_step)

        # Update the episode reward and steps
        episode_reward += eval_time_step.reward
        print("EPISODE REWARD:", episode_reward)
        episode_steps += 1
        print("EPISODE STEPS:", episode_steps)

    # Append the episode reward and steps to the evaluation lists
    eval_rewards.append(episode_reward)
    eval_steps.append(episode_steps)

    # Reset the environment for the next episode
    eval_time_step = eval_env.reset()

# Calculate the average reward and steps per episode
avg_eval_reward = np.mean(eval_rewards)
avg_eval_steps = np.mean(eval_steps)

# Define the accuracy_per_episode variable
accuracy_per_episode = [0.9, 0.8, 0.7]  # Replace with the actual accuracy values

# Create a dictionary with the evaluation results
results = {
    "Episode": list(range(1, eval_episodes + 1)),
    "Reward": eval_rewards,
    "Steps": eval_steps,
    "Accuracy": accuracy_per_episode  # Add the accuracy values here
}

# Create a DataFrame from the dictionary
df = pd.DataFrame(results)

print(df)

# Print the evaluation results
print("Evaluation Results:")
print("Number of Episodes:", eval_episodes)
print("Total Reward:", np.sum(eval_rewards))
print("Reward per Episode:", eval_rewards)
print("Total Steps:", np.sum(eval_steps))
print("Steps per Episode:", eval_steps)
print("Average Reward per Episode:", avg_eval_reward)
print("Average Steps per Episode:", avg_eval_steps)


# Plot the rewards and steps per episode
plt.figure(figsize=(30, 30))
plt.subplot(1, 2, 1)
plt.plot(eval_rewards)
plt.xlabel("Episode")
plt.ylabel("Reward")
plt.title("Rewards per Episode")

plt.subplot(1, 2, 2)
plt.plot(eval_steps)
plt.xlabel("Episode")
plt.ylabel("Steps")
plt.title("Steps per Episode")

plt.tight_layout()
plt.show()