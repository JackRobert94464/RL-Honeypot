import gym
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from NetworkHoneypotEnv import NetworkHoneypotEnv

class DQN(tf.keras.Model):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = Dense(24, activation='relu', input_shape=(state_size,))
        self.fc2 = Dense(24, activation='relu')
        self.fc3 = Dense(action_size, activation='linear')

    def call(self, inputs):
        x = self.fc1(inputs)
        x = self.fc2(x)
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, discount_factor=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.batch_size = 32
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.model = DQN(state_size, action_size)
        self.optimizer = Adam(learning_rate=self.learning_rate)
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def choose_action(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.action_size)
        q_values = self.model.predict(state)
        return np.argmax(q_values[0])
        
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        minibatch = np.random.choice(self.memory, self.batch_size, replace=False)
        
        for state, action, reward, next_state, done in minibatch:
            print("Shapes:", state.shape, action.shape, reward.shape, next_state.shape, done.shape)  # Debug line
            
            target = reward
            if not done:
                target = (reward + self.discount_factor * np.amax(self.model.predict(next_state)[0]))
            target_q_values = self.model.predict(state)
            target_q_values[0][action] = target
            
            with tf.GradientTape() as tape:
                q_values = self.model(state)
                loss = tf.keras.losses.mean_squared_error(target_q_values, q_values)
            gradients = tape.gradient(loss, self.model.trainable_variables)
            self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


env = NetworkHoneypotEnv()
state_size = 10  # Use the state size you defined in NetworkHoneypotEnv class
action_size = 3

agent = DQNAgent(state_size, action_size)

num_episodes = 1000

for episode in range(num_episodes):
    state = env.reset()
    total_reward = 0
    done = False
    
    while not done:
        state_array = np.reshape(state, [1, state_size])
        action = agent.choose_action(state_array)
        
        # Convert the chosen action to a binary array
        action_array = np.zeros(action_size)
        action_array[action] = 1
        
        next_state, reward, done, _ = env.step(action_array)
        total_reward += reward
        agent.remember(state, action, reward, next_state, done)
        
        # Convert next_state to an array
        next_state_array = np.reshape(next_state, [1, state_size])
        
        agent.replay()
        state = next_state_array
    
    print(f"Episode: {episode + 1}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.4f}")