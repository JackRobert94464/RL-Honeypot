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



 '''
    def createNetwork(self):
        # Define input layers for each type of input data
        
        observable_input = Input(shape=(self.stateDimension,))
        epss_input = Input(shape=(self.epssDimension,))
        ntpg_input = Input(shape=(self.ntpgDimension,))
        
        # Branch 1: Process observable matrix
        observable_branch = Dense(64, activation='relu')(observable_input)
        
        # Branch 2: Process EPSS matrix
        epss_branch = Dense(64, activation='relu')(epss_input)
        
        # Branch 3: Process ntpg penetration graph
        ntpg_branch = Dense(64, activation='relu')(ntpg_input)
        
        # Concatenate the outputs of all branches
        concatenated = Concatenate()([observable_branch, epss_branch, ntpg_branch])
        
        # Intermediate dense layer
        concatenated = Dense(64, activation='relu')(concatenated)
        
        # Output layer
        output = Dense(self.actionDimension, activation='linear')(concatenated)
        
        # Create model
        model = Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)
        
        # Compile model
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics=['accuracy'])
        
        print("Created network:", model.summary())
        
        return model
    '''
    