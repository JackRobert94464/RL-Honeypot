import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from NetworkHoneypotEnv import NetworkHoneypotEnv
from tf_agents.environments import tf_py_environment

# Load the trained model
trained_model = tf.keras.models.load_model("RL_Honeypot_trained_model_temp.keras")

# Create a new environment for evaluation
eval_env = NetworkHoneypotEnv(10, 3, 7, 0.8, 0.2)

# Reset the environment
eval_time_step = eval_env.reset()

# Initialize variables for tracking rewards and steps
eval_rewards = []
eval_steps = []

# Evaluate the model for a certain number of episodes
eval_episodes = 2
for _ in range(eval_episodes):
    episode_reward = 0
    episode_steps = 0

    # Run the evaluation episode
    while not eval_time_step.is_last():
        # Get the action from the trained model
        action = trained_model.predict(eval_time_step.observation.reshape(1, -1))

        # Take a step in the environment
        eval_time_step = eval_env.step(action)

        # Update the episode reward and steps
        episode_reward += eval_time_step.reward
        episode_steps += 1

    # Append the episode reward and steps to the evaluation lists
    eval_rewards.append(episode_reward)
    eval_steps.append(episode_steps)

    # Reset the environment for the next episode
    eval_time_step = eval_env.reset()

# Calculate the average reward and steps per episode
avg_eval_reward = np.mean(eval_rewards)
avg_eval_steps = np.mean(eval_steps)

# Print the evaluation results
print("Evaluation Results:")
print("Average Reward per Episode:", avg_eval_reward)
print("Average Steps per Episode:", avg_eval_steps)

# Plot the rewards and steps per episode
plt.figure(figsize=(2, 5))
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