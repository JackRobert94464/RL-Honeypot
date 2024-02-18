import pandas as pd
import numpy as np
# Define the accuracy_per_episode variable
accuracy_per_episode = [0.4, 0.8, 0.7, 0.85, 0.75, 0.95, 0.95, 1, 1, 0.9]  # Replace with the actual accuracy values

# Create a dictionary with the evaluation results
eval_episodes = 10
eval_rewards = [-1, 1, 1, 1, 1, 1, 0, 1, 1, 1]
eval_steps = [100, 132, 98, 101, 85, 73, 64, 97, 52, 76]
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
print("Average Reward per Episode:", np.mean(eval_rewards))
print("Average Steps per Episode:", np.mean(eval_steps))
