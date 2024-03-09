###########################################################################
#    EVALUATION CODE
###########################################################################   

# Import the environment 
from NetworkHoneypotEnv import NetworkHoneypotEnv
from ddqn_agent import DoubleDeepQLearning

import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

import misc

# Load the trained model
trained_model = tf.keras.models.load_model("RL_Honeypot_trained_model_temp.keras")

# Load the NTPG and HTPG dictionaries
ntpg = misc.create_dictionary_ntpg("ntpg_eval.csv")
htpg = misc.create_dictionary_htpg("htpg_eval.csv")

# Load the topology param from TPGs
deception_nodes = misc.get_deception_nodes()
normal_nodes = misc.count_nodes(ntpg)
first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# Create a new environment for evaluation
eval_env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)
# tf_eval_env = tf_py_environment.TFPyEnvironment(eval_env)

# Reset the environment
eval_time_step = eval_env.reset()

# Initialize variables for tracking rewards and steps
eval_rewards = []
eval_steps = []

# Evaluate the model for a certain number of episodes
eval_episodes = 15
eval_rewards = []
eval_steps = []

# Define initial gamma and epsilon
gamma = 0.9
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

# Create the model
ddqn_agent = DoubleDeepQLearning(eval_env, gamma, epsilon, eval_episodes, normal_nodes, total_permutations)

for _ in range(eval_episodes):
    episode_reward = 0
    episode_steps = 0

    print("------------------------------------------------------------------------------------------------------------------------")
    print("Evaluating episode number: ", eval_episodes)
    print("------------------------------------------------------------------------------------------------------------------------")

    # Run the evaluation episode
    while not eval_time_step.is_last():
        # Get the action from the trained model
        action = ddqn_agent.selectActionEval(eval_time_step.observation, _, trained_model)
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


# Create a dictionary with the evaluation results
results = {
    "Episode": list(range(1, eval_episodes + 1)),
    "Reward": eval_rewards,
    "Steps": eval_steps,
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
