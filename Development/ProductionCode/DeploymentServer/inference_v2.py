
# Make sure to put in your network data (NTPG and HTPG graphs) in the appropriate path with name ntpg_inf.csv and htpg_inf.csv
# Make sure to put in your model to predict in the appropriate path with name inference_model.keras
# You can also replace the loss function with your custom loss function, just load it in the main folder
# The inference server will create an environment base on the data given and the amount of deception nodes available
# To run the inference server, run the following command:
#
#     python inference_v2.py
#
# The server will be running on http://server-ip:35025. You can send a POST request to http://server-ip:35025/predict with the network state and the number of honeypots to deploy.
# Example:
# curl -X POST -H "Content-Type: application/json" -d '{"network_state": [0, 1, 0, 0, 1, 0, 0, 1, 1, 1], "num_honeypots": 2}' http://0.0.0.0:5000/predict


import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
import misc
import ddqn_loss_fn
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

class Agent:

    # Please load the ntpg and htpg data from the appropriate path to create the inference environment

    def __init__(self, model, ntpg_dir, htpg_dir, honeypotAvailable, NMS_fnr=0.1, NMS_fpr=0.1, assume_attack_rate=0.7):

        # Load the ntpg and htpg data
        ntpg, htpg = misc.load_tpg_data(ntpg_dir, htpg_dir)

        # Create the inference environment from baseEnv
        # If you're unsure about attack rate, you can set it to 0.7
        # TODO: Remove fnr, fpr and attack rate for inference environment/ take it from json request send from NMS server
        self.env = misc.create_environment_from_baseEnv(ntpg, htpg, honeypotAvailable, NMS_fnr, NMS_fpr, assume_attack_rate, 5)

        self.epssMatrix = misc.ntpg_to_epss_matrix(self.env.get_ntpg())
        self.connectionMatrix = misc.ntpg_to_connection_matrix(self.env.get_ntpg())

        # Load the model
        self.model = model

    def index_to_action(self, index):
        # Implement the logic to convert the index to the corresponding action
        # based on your environment and action representation
        print("Action space to pick from: ", self.env.action_space())
        print("Action Index: ", index-1)
        print("Action picked: ", self.env.action_space()[index-1])
        action_matrix = self.env.action_space()[index-1]
        return action_matrix

    def selectActionInferenceDDQN(self, state):
        state = np.array(state, dtype=np.float32).reshape(1, -1)  # Reshape the state for model input
        Qvalues = self.model.predict(state)[0]  # Get the Q-values for the state
        max_index = np.argmax(Qvalues)  # Get the index of the maximum Q-value
        action_matrix = self.index_to_action(max_index)  # Convert the index to the corresponding action
        return action_matrix
    
    def selectActionInferenceConv1D(self, state):

        epss_matrix = np.array(self.epssMatrix)        
        ntpg_matrix = np.array(self.connectionMatrix)

        if len(epss_matrix.shape) > 2:
            epss_matrix = np.stack(epss_matrix)
        if len(ntpg_matrix.shape) > 2:
            ntpg_matrix = np.stack(ntpg_matrix)

        epss_input = np.expand_dims(epss_matrix, axis=-1)
        ntpg_input = np.expand_dims(ntpg_matrix, axis=-1)

        epss_input_reshaped = np.array(epss_input).reshape(-1, len(state), len(state))
        ntpg_input_reshaped = np.array(ntpg_input).reshape(-1, len(state), len(state))

        state = np.array(state, dtype=np.float32).reshape(1, -1)  # Reshape the state for model input
        Qvalues = self.model.predict([state, epss_input_reshaped, ntpg_input_reshaped])  # Get the Q-values for the state
        print(Qvalues)
        print(np.argmax(Qvalues))
        max_index = np.argmax(Qvalues)  # Get the index of the maximum Q-value
        action_matrix = self.index_to_action(max_index)  # Convert the index to the corresponding action
        
        return action_matrix
    
    def selectActionInferenceSARSA(self, state, trained_model):
        state = state.reshape(1, -1)
        q_values = trained_model.predict(state)[0]
        
        if np.random.uniform(0, 1) < self.epsilon:
            # Choose a random action
            action_space_values = list(self.env.action_space().values())
            random_action = np.random.choice(action_space_values)
            action = np.array(random_action, dtype=np.int32)
        else:
            action_index = np.argmax(q_values)
            action = self.index_to_action(action_index)

        return action
    

@app.route('/predict', methods=['POST'])
def predict():
    # Get the network state from the request
    network_state = request.get_json()['network_state']
    num_honeypots = request.get_json()['num_honeypots']
    
    start_time = time.time()

    # Create an instance of your agent
    agent = Agent(model=model_infer, ntpg_dir=ntpg_infer_csv, htpg_dir=htpg_infer_csv, honeypotAvailable=num_honeypots)  # Initialize with the appropriate arguments

    # Get the predicted action for the current state
    if 'conv1D' in model_path:
        action = agent.selectActionInferenceConv1D(network_state)
    elif 'obsdense' in model_path:
        action = agent.selectActionInferenceDDQN(network_state)
    elif 'SARSA' in model_path:
        action = agent.selectActionInferenceSARSA(network_state, model_infer)
    else:
        # Handle the case when the model name doesn't match any expected patterns
        action = None

    # Get the indices of the top `num_honeypots` predictions
    # top_indices = np.argsort(action)[-num_honeypots:]
    # deployment_targets = top_indices.tolist()
    deployment_targets = action
    
    # Chon subnet cho ket qua predict
    subnet_targets = [0] * 4
    
    for node in deployment_targets:
        subnet = None
        if node in range(0, 2):
            subnet = 0
        elif node in range(2, 5):
            subnet = 1
        elif node in range(5, 8):
            subnet = 2
        elif node in range(8, 10):
            subnet = 3
        subnet_targets[subnet] = 1

    # Write the subnet_targets to 'output.tmp' file
    with open('output.tmp', 'w') as file:
        for target in subnet_targets:
            file.write(str(target) + '\n')
            
    # Check hit condition
    # Determine which subnets have '1' in the network_state
    subnet_with_one = [0] * 4
    for i, state in enumerate(network_state):
        if state == 1:
            subnet = 0 if i in range(0, 2) else 1 if i in range(2, 5) else 2 if i in range(5, 8) else 3
            subnet_with_one[subnet] = 1
    
    # Check for hits
    hit = False
    for node in deployment_targets:
        subnet = 0 if node in range(0, 2) else 1 if node in range(2, 5) else 2 if node in range(5, 8) else 3
        if subnet_with_one[subnet] == 1:
            hit = True
            break
    
    elapsed_time = time.time() - start_time
    
    # Return the deployment targets as a JSON response
    return jsonify({'deployment_targets': deployment_targets, 'subnet': subnet_targets, elapsed_time: elapsed_time, 'hit': hit})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35025)