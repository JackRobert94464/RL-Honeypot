import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
import misc
import ddqn_loss_fn
from collections import deque
import random
import time

# Default value
ntpg_infer_csv = "ntpg_inf.csv"
htpg_infer_csv = "htpg_inf.csv"

# Load the trained model
model_path = 'RL_Honeypot_1to5_conv1D_simpleinput_v2_linux_ver49890.keras'

ddqn_loss_fn = ddqn_loss_fn.ddqn_loss_fn
model_infer = misc.load_trained_model(model_path=model_path, loss_fn=ddqn_loss_fn)

# Initialize the Flask app
app = Flask(__name__)

# Replay buffer settings
REPLAY_BUFFER_SIZE = 50
BATCH_SIZE = 5
GAMMA = 0.99  # Discount factor for reward

class Agent:
    def __init__(self, model, ntpg_dir, htpg_dir, honeypotAvailable, NMS_fnr=0.1, NMS_fpr=0.1, assume_attack_rate=0.7):
        self.model = model
        self.replay_buffer = deque(maxlen=REPLAY_BUFFER_SIZE)
        self.previous_state = None

        # Load the ntpg and htpg data
        ntpg, htpg = misc.load_tpg_data(ntpg_dir, htpg_dir)
        self.env = misc.create_environment_from_baseEnv(ntpg, htpg, honeypotAvailable, NMS_fnr, NMS_fpr, assume_attack_rate)

        self.epssMatrix = misc.ntpg_to_epss_matrix(self.env.get_ntpg())
        self.connectionMatrix = misc.ntpg_to_connection_matrix(self.env.get_ntpg())

    def index_to_action(self, index):
        action_matrix = self.env.action_space()[index - 1]
        return action_matrix

    def select_action(self, state, strategy='DDQN'):
        state = np.array(state, dtype=np.float32).reshape(1, -1)  # Reshape the state for model input
        if strategy == 'Conv1D':
            epss_input = np.expand_dims(np.stack(self.epssMatrix), axis=-1)
            ntpg_input = np.expand_dims(np.stack(self.connectionMatrix), axis=-1)
            epss_input_reshaped = epss_input.reshape(-1, 10, 10)
            ntpg_input_reshaped = ntpg_input.reshape(-1, 10, 10)
            Qvalues = self.model.predict([state, epss_input_reshaped, ntpg_input_reshaped])
        else:
            Qvalues = self.model.predict(state)

        max_index = np.argmax(Qvalues)
        action_matrix = self.index_to_action(max_index)
        return action_matrix

    def save_transition(self, current_state, action, reward, next_state, terminal):
        self.replay_buffer.append((current_state, action, reward, next_state, terminal))

    def train_network(self):
        print("BATCH_SIZE: ", BATCH_SIZE)
        if len(self.replay_buffer) < BATCH_SIZE:
            return

        batch = random.sample(self.replay_buffer, BATCH_SIZE)
        current_states = np.array([transition[0] for transition in batch])
        actions = np.array([transition[1] for transition in batch])
        rewards = np.array([transition[2] for transition in batch])
        next_states = np.array([transition[3] for transition in batch])
        terminals = np.array([transition[4] for transition in batch])

        Q_next = self.model.predict(next_states)
        Q_target = rewards + GAMMA * np.max(Q_next, axis=1) * (~terminals)

        Q_values = self.model.predict(current_states)
        for i, action in enumerate(actions):
            Q_values[i, action] = Q_target[i]

        self.model.fit(current_states, Q_values, batch_size=BATCH_SIZE, verbose=0)

    def process_inference(self, network_state, num_honeypots):
        current_state = network_state
        print("Current state: ", current_state)
        action = self.select_action(current_state, strategy='Conv1D' if 'conv1D' in model_path else 'DDQN')
        print("Action: ", action)
        
        reward = 0
        terminal = False
        
        for node in action:
            print("Node: ", node)
            if current_state[node-1] == 1:
                reward = 1
                terminal = True
                break
            
        if current_state[7] == 1:
            reward = -1
            terminal = True

        # Reward calculation and terminal state determination
        # reward = 1 if any(current_state[i] == 1 for i in action) else -1
        # terminal = any(current_state[i] == 1 for i in action)
        
        if self.previous_state is not None:
            print("Previous state: ", self.previous_state)
            print("START TRAINING")
            self.save_transition(self.previous_state, action, reward, current_state, terminal)
            self.train_network()

        self.previous_state = current_state
        return action

@app.route('/predict', methods=['POST'])
def predict():
    request_data = request.get_json()
    network_state = request_data['network_state']
    num_honeypots = request_data['num_honeypots']

    agent = Agent(model=model_infer, ntpg_dir=ntpg_infer_csv, htpg_dir=htpg_infer_csv, honeypotAvailable=num_honeypots)

    action = agent.process_inference(network_state, num_honeypots)
    deployment_targets = action

    subnet_targets = [0] * 4
    for node in deployment_targets:
        subnet = 0 if node in range(0, 2) else 1 if node in range(2, 5) else 2 if node in range(5, 8) else 3
        subnet_targets[subnet] = 1

    with open('output.tmp', 'w') as file:
        for target in subnet_targets:
            file.write(str(target) + '\n')

    return jsonify({'deployment_targets': deployment_targets, 'subnet': subnet_targets})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35025)
