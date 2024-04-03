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

from visualizer import visualize_steps

# Load the trained model
trained_model = tf.keras.models.load_model(".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_weighted_attacker_1to5_decoy.keras", custom_objects={'loss': DoubleDeepQLearning.ddqn_loss_fn})

# Load the NTPG and HTPG dictionaries
ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_eval.csv")
htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_eval.csv")

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
eval_episodes = 50
eval_rewards = []
eval_steps = []

# Define initial gamma and epsilon
gamma = 0.9
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

# VISUALIZATION #
# Extract nodes from the ntpg dictionary
your_nodes_list = list(ntpg.keys())

# Extract edges from the ntpg dictionary
your_edges_list = [(node, edge[0]) for node in ntpg for edge in ntpg[node]]
# VISUALIZATION #

# Create the model
ddqn_agent = DoubleDeepQLearning(eval_env, gamma, epsilon, eval_episodes, normal_nodes, total_permutations)

# Create a DataFrame to store the visualization data
visualization_data = pd.DataFrame(columns=['episode', 'steps', 'step_entities'])

for episode in range(eval_episodes):
    episode_reward = 0
    episode_steps = 0

    print("------------------------------------------------------------------------------------------------------------------------")
    print("Evaluating episode number: ", episode)
    print("------------------------------------------------------------------------------------------------------------------------")

    # Create a temporary list to hold the step entities
    steps_entity = []

    # Run the evaluation episode
    while not eval_time_step.is_last():

        # Get the action from the trained model
        action = ddqn_agent.selectActionEval(eval_time_step.observation, episode, trained_model)
        print("ACTION SELECTED:", action)
        # Check if the action is None
        if action is None:
            print("No action selected. Skipping this step.")
            
        # Take a step in the environment
        eval_time_step = eval_env.step(action)
        print("EVAL TIME STEP:", eval_time_step)

        steps_entity.append({'attacker_node': eval_env._current_attacker_node, 
                      'nifr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nifr_nodes], 
                      'nicr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nicr_nodes],})

        # Update the episode reward and steps
        episode_reward += eval_time_step.reward
        print("EPISODE REWARD:", episode_reward)
        episode_steps += 1
        print("EPISODE STEPS:", episode_steps)

        # Append the evaluation data to the visualization DataFrame
        visualization_data = visualization_data._append({'episode': episode, 'steps': episode_steps, 'step_entities': steps_entity}, ignore_index=True)

        # clearing the step entity list after each step
        steps_entity = []

    # Append the episode reward and steps to the evaluation lists
    eval_rewards.append(episode_reward)
    eval_steps.append(episode_steps)

    # Reset the environment for the next episode
    eval_time_step = eval_env.reset()


# Save the visualization data to a CSV file
visualization_data.to_csv('visualization_data.csv', index=False)

# Visualize the steps
visualize_steps(your_nodes_list, your_edges_list, 'visualization_data.csv')

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
