###########################################################################
#    EVALUATION CODE
###########################################################################   

# ------------------- LIBRARIES ------------------- #

# Import the environment 
from demodsp_NetworkHoneypotEnv import NetworkHoneypotEnv
from demodsp_ddqn_agent_headless import DoubleDeepQLearning

import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

import misc
import os

# from visualizer import visualize_steps
import ddqn_dsp_visualizer

# ------------------- LIBRARIES ------------------- #


# ------------------------- ENVIRONMENT --------------------------------- #


# Load the NTPG and HTPG dictionaries
if os.name == 'nt':  # If the operating system is Windows
    ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_eval.csv")
    htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_eval.csv")
else:  # For other operating systems like Linux
    ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg_eval.csv")
    htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg_eval.csv")

# Load the topology param from TPGs
# deception_nodes = misc.get_deception_nodes()
deception_nodes = 2
normal_nodes = misc.count_nodes(ntpg)
first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# Create a new environment for evaluation
eval_env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)
# tf_eval_env = tf_py_environment.TFPyEnvironment(eval_env)

# Reset the environment
eval_time_step = eval_env.reset()

# ------------------------- ENVIRONMENT --------------------------------- #




# -------------------------- TRACKING PARAMETERS ------------------------- #

# Initialize variables for tracking rewards and steps
ddqn_eval_rewards = []
ddqn_eval_steps = []

static_eval_rewards = []
static_eval_steps = []

randomdyn_eval_rewards = []
randomdyn_eval_steps = []

# Evaluate the model for a certain number of episodes
eval_episodes = 50

# Number of Random Dynamic Policy Experiments
numberofExperiments = 10

# Create a list to store step count every 50 episodes
ddqn_step_globalcounter = []
static_step_globalcounter = []
randomdyn_step_globalcounter = []

# Create a list to store dsp every 50 episodes
# dsp_globalcounter = []
ddqn_dsp_globalcounter = []
static_dsp_globalcounter = []
randomdyn_dsp_globalcounter = []

ddqn_step_counter = 0
ddqn_episodeWon = 0

static_step_counter = 0
static_episodeWon = 0

randomdyn_step_counter = 0
randomdyn_episodeWon = 0


# -------------------------- TRACKING PARAMETERS ------------------------- #


# -------------------------- AGENT PARAMETERS ------------------------- #

# Define initial gamma and epsilon
gamma = 0.9
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

# VISUALIZATION #
# Extract nodes from the ntpg dictionary
your_nodes_list = list(ntpg.keys())

# Extract edges from the ntpg dictionary
your_edges_list = [(node, edge[0]) for node in ntpg for edge in ntpg[node]]

# Create the model
ddqn_agent = DoubleDeepQLearning(eval_env, gamma, epsilon, eval_episodes, normal_nodes, total_permutations)

# Load the trained model
if os.name == 'nt':  # If the operating system is Windows
    trained_model = tf.keras.models.load_model(".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_weighted_attacker_1to5_decoy_win.keras", custom_objects={'loss': DoubleDeepQLearning.ddqn_loss_fn})
else:  # For other operating systems like Linux
    trained_model = tf.keras.models.load_model("./TrainedModel/weighted_random_attacker/RL_Honeypot_weighted_attacker_1to5_decoy_linux.keras", custom_objects={'loss': DoubleDeepQLearning.ddqn_loss_fn})


# -------------------------- AGENT PARAMETERS ------------------------- #



# -------------------------- VISUALIZATION ------------------------- #


# Create a DataFrame to store the visualization data
visualization_data = pd.DataFrame(columns=['episode', 'steps', 'step_entities'])

# -------------------------- VISUALIZATION ------------------------- #




'''
Evaluating DDQN algorithm
'''
for episode in range(eval_episodes):
    ddqn_episode_reward = 0
    ddqn_episode_steps = 0

    print("------------------------------------------------------------------------------------------------------------------------")
    print("Evaluating episode number: ", episode, "with DDQN algorithm")
    print("------------------------------------------------------------------------------------------------------------------------")

    # Create a temporary list to hold the step entities
    ddqn_steps_entity = []

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

        ddqn_steps_entity.append({'attacker_node': eval_env._current_attacker_node, 
                      'nifr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nifr_nodes], 
                      'nicr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nicr_nodes],})

        # Update the episode reward and steps
        ddqn_episode_reward += eval_time_step.reward
        print("EPISODE REWARD:", ddqn_episode_reward)
        ddqn_episode_steps += 1
        print("EPISODE STEPS:", ddqn_episode_steps)

        # Append the evaluation data to the visualization DataFrame
        visualization_data = visualization_data._append({'episode': episode, 'steps': ddqn_episode_steps, 'step_entities': ddqn_steps_entity}, ignore_index=True)

        # clearing the step entity list after each step
        ddqn_steps_entity = []

    if ddqn_episode_reward > 0:
        ddqn_episodeWon += 1

    # add the step count to the global step counter
    ddqn_step_counter += ddqn_episode_steps
    
    
    '''
    # if episode is a multiple of 50, append step count and calculate dsp
    if episode % 2 == 0:
        step_globalcounter.append(step_counter)
        print("episode Won: ", episodeWon)
        print("episode: ", episode)
        dsp = episodeWon / (episode+1)
        print("Defense Success Probability: ", dsp)
        
        # os.system("pause")
        dsp_globalcounter.append(dsp)
    '''

    # Append the episode reward and steps to the evaluation lists
    ddqn_eval_rewards.append(ddqn_episode_reward)
    ddqn_eval_steps.append(ddqn_episode_steps)

    # Reset the environment for the next episode
    eval_time_step = eval_env.reset()
    
    
    
    
# Calculate the average reward and steps per episode
ddqn_avg_eval_reward = np.mean(ddqn_eval_rewards)
ddqn_avg_eval_steps = np.mean(ddqn_eval_steps)


# Create a dictionary with the evaluation results
results = {
    "Episode": list(range(1, eval_episodes + 1)),
    "Reward": ddqn_eval_rewards,
    "Steps": ddqn_eval_steps,
}

# Create a DataFrame from the dictionary
df = pd.DataFrame(results)

print(df)

# Print the evaluation results
print("Evaluation Results:")
print("Number of Episodes:", eval_episodes)
print("Total Reward:", np.sum(ddqn_eval_rewards))
print("Reward per Episode:", ddqn_eval_rewards)
print("Total Steps:", np.sum(ddqn_eval_steps))
print("Steps per Episode:", ddqn_eval_steps)
print("Average Reward per Episode:", ddqn_avg_eval_reward)
print("Average Steps per Episode:", ddqn_avg_eval_steps)

# Calculate the Defense Success Probability (DSP)
ddqn_num_successful_defense = sum(reward > 0 for reward in ddqn_eval_rewards)
ddqn_dsp = (ddqn_num_successful_defense / eval_episodes)

print("Number of Successful Defense:", ddqn_num_successful_defense)
print("Defense Success Probability (DSP):", ddqn_dsp)

# Save the dsp score to the eval_dsp variable of the agent
# ddqn_agent.appendEvalDSP(dsp)

# Save the DSP score to a file
with open('dsp_score_ddqn_temp.txt', 'w') as file:
    file.write(str(ddqn_dsp))




'''
Evaluating Static Policy
for the amount of actions available in action space:
try that action out for eval_episodes episodes + summarize the dsp
'''
policyArray = []

for numberofActions in range(len(eval_env.action_space())):
    
    
    # reset the static_eval_rewards
    static_eval_rewards = []
    
    
    policyArray.append(numberofActions)
    
    for episode in range(eval_episodes):
        static_episode_reward = 0
        static_episode_steps = 0

        print("------------------------------------------------------------------------------------------------------------------------")
        print("Evaluating episode number: ", episode, "with Static Policy Number: ", numberofActions)
        print("------------------------------------------------------------------------------------------------------------------------")

        # Create a temporary list to hold the step entities
        static_steps_entity = []

        # Run the evaluation episode
        while not eval_time_step.is_last():

            # Get the action from the trained model
            action = ddqn_agent.selectActionStatic(numberofActions)
            print("ACTION SELECTED:", action)
            # Check if the action is None
            if action is None:
                print("No action selected. Skipping this step.")
                
            # Take a step in the environment
            eval_time_step = eval_env.step(action)
            print("EVAL TIME STEP:", eval_time_step)

            static_steps_entity.append({'attacker_node': eval_env._current_attacker_node, 
                        'nifr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nifr_nodes], 
                        'nicr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nicr_nodes],})

            # Update the episode reward and steps
            static_episode_reward += eval_time_step.reward
            print("EPISODE REWARD:", static_episode_reward)
            static_episode_steps += 1
            print("EPISODE STEPS:", static_episode_steps)

            # Append the evaluation data to the visualization DataFrame
            visualization_data = visualization_data._append({'episode': episode, 'steps': static_episode_steps, 'step_entities': static_steps_entity}, ignore_index=True)

            # clearing the step entity list after each step
            static_steps_entity = []

        if static_episode_reward > 0:
            static_episodeWon += 1

        # add the step count to the global step counter
        static_step_counter += static_episode_steps

        # Append the episode reward and steps to the evaluation lists
        static_eval_rewards.append(static_episode_reward)
        static_eval_steps.append(static_episode_steps)

        # Reset the environment for the next episode
        eval_time_step = eval_env.reset()


    
    # Calculate the average reward and steps per episode
    static_avg_eval_reward = np.mean(static_eval_rewards)
    static_avg_eval_steps = np.mean(static_eval_steps)


    # Print the evaluation results
    print("Evaluation Results:")
    print("Number of Episodes:", eval_episodes)
    print("Total Reward:", np.sum(static_eval_rewards))
    print("Reward per Episode:", static_eval_rewards)
    print("Total Steps:", np.sum(static_eval_steps))
    print("Steps per Episode:", static_eval_steps)
    print("Average Reward per Episode:", static_avg_eval_reward)
    print("Average Steps per Episode:", static_avg_eval_steps)

    # Calculate the Defense Success Probability (DSP)
    static_num_successful_defense = sum(reward > 0 for reward in static_eval_rewards)
    static_dsp = (static_num_successful_defense / eval_episodes)

    print("Number of Successful Defense:", static_num_successful_defense)
    print("Defense Success Probability (DSP):", static_dsp)
    
    # os.system("pause")
    
    static_dsp_globalcounter.append(static_dsp)

    # Save the dsp score to the eval_dsp variable of the agent
    # static_agent.appendEvalDSP(dsp)

# Save the DSP score to a file
with open('dsp_score_static_temp.txt', 'w') as file:
    file.write(str(static_dsp_globalcounter))


# draw
ddqn_dsp_visualizer.static_dsp_visual(policyArray, static_dsp_globalcounter)



'''
Evaluating Random Dynamic Policy
'''
experimentNo = []
for experiment in range(numberofExperiments):
    
    # reset the randomdyn_eval_rewards
    randomdyn_eval_rewards = []
   
    experimentNo.append(experiment)
    
    for episode in range(eval_episodes):
        randomdyn_episode_reward = 0
        randomdyn_episode_steps = 0

        print("------------------------------------------------------------------------------------------------------------------------")
        print("Evaluating episode number: ", episode, "with Random Dynamic Policy Experiment Number: ", experiment)
        print("------------------------------------------------------------------------------------------------------------------------")

        # Create a temporary list to hold the step entities
        randomdyn_steps_entity = []

        # Run the evaluation episode
        while not eval_time_step.is_last():

            # Get the action from the trained model
            action = ddqn_agent.selectActionDynamicRandom()
            print("ACTION SELECTED:", action)
            # Check if the action is None
            if action is None:
                print("No action selected. Skipping this step.")
                
            # Take a step in the environment
            eval_time_step = eval_env.step(action)
            print("EVAL TIME STEP:", eval_time_step)

            randomdyn_steps_entity.append({'attacker_node': eval_env._current_attacker_node, 
                        'nifr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nifr_nodes], 
                        'nicr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nicr_nodes],})

            # Update the episode reward and steps
            randomdyn_episode_reward += eval_time_step.reward
            print("EPISODE REWARD:", randomdyn_episode_reward)
            randomdyn_episode_steps += 1
            print("EPISODE STEPS:", randomdyn_episode_steps)

            # Append the evaluation data to the visualization DataFrame
            visualization_data = visualization_data._append({'episode': episode, 'steps': randomdyn_episode_steps, 'step_entities': randomdyn_steps_entity}, ignore_index=True)

            # clearing the step entity list after each step
            randomdyn_steps_entity = []

        if randomdyn_episode_reward > 0:
            randomdyn_episodeWon += 1

        # add the step count to the global step counter
        randomdyn_step_counter += randomdyn_episode_steps
        
        # Append the episode reward and steps to the evaluation lists
        randomdyn_eval_rewards.append(randomdyn_episode_reward)
        randomdyn_eval_steps.append(randomdyn_episode_steps)

        # Reset the environment for the next episode
        eval_time_step = eval_env.reset()



    # Calculate the average reward and steps per episode
    randomdyn_avg_eval_reward = np.mean(randomdyn_eval_rewards)
    randomdyn_avg_eval_steps = np.mean(randomdyn_eval_steps)


    # Print the evaluation results
    print("Evaluation Results:")
    print("Number of Episodes:", eval_episodes)
    print("Total Reward:", np.sum(randomdyn_eval_rewards))
    print("Reward per Episode:", randomdyn_eval_rewards)
    print("Total Steps:", np.sum(randomdyn_eval_steps))
    print("Steps per Episode:", randomdyn_eval_steps)
    print("Average Reward per Episode:", randomdyn_avg_eval_reward)
    print("Average Steps per Episode:", randomdyn_avg_eval_steps)

    # Calculate the Defense Success Probability (DSP)
    randomdyn_num_successful_defense = sum(reward > 0 for reward in randomdyn_eval_rewards)
    randomdyn_dsp = (randomdyn_num_successful_defense / eval_episodes)

    print("Number of Successful Defense:", randomdyn_num_successful_defense)
    print("Defense Success Probability (DSP):", randomdyn_dsp)
    
    
    # os.system("pause")
    
    
    randomdyn_dsp_globalcounter.append(randomdyn_dsp)
    
    
    # Save the dsp score to the eval_dsp variable of the agent
    # randomdyn_agent.appendEvalDSP(dsp)

# Save the DSP score to a file
with open('dsp_score_randomdyn_temp.txt', 'w') as file:
    file.write(str(randomdyn_dsp_globalcounter))


# draw
ddqn_dsp_visualizer.randomdyn_dsp_visual(experimentNo, randomdyn_dsp_globalcounter)








# Visualize the Defense Success Probability (DSP) of our method
# ddqn_dsp_visualizer.ddqn_dsp_visual(step_globalcounter, dsp_globalcounter)


'''
# Save the visualization data to a CSV file
visualization_data.to_csv('visualization_data.csv', index=False)

# Visualize the steps
visualize_steps(your_nodes_list, your_edges_list, 'visualization_data.csv')
'''






'''
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

'''
