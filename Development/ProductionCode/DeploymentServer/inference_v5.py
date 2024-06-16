import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
import misc
import ddqn_loss_fn
from collections import deque
import random
import time

import ddqn_agent_3x_simple_state_fnrfpr_v2
import threading

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

rt_buffer = deque(maxlen=REPLAY_BUFFER_SIZE)
rt_action_buffer = deque(maxlen=REPLAY_BUFFER_SIZE)

# Load the ntpg and htpg data
ntpg, htpg = misc.load_tpg_data(ntpg_infer_csv, htpg_infer_csv)

@app.route('/predict', methods=['POST'])
def predict():
    request_data = request.get_json()
    network_state = request_data['network_state']
    num_honeypots = request_data['num_honeypots']
    
    start_time = time.time()
    
    # saving state for continuous learning
    rt_buffer.append(network_state)
    
    
    normal_nodes = len(network_state)
    deception_nodes_amount = num_honeypots
    totalpermutation = misc.calculate_permutation(normal_nodes, deception_nodes_amount)

    # agent = Agent.get_instance(model=model_infer, ntpg_dir=ntpg_infer_csv, htpg_dir=htpg_infer_csv, honeypotAvailable=num_honeypots)
    env = misc.create_environment_from_baseEnv(ntpg, htpg, num_honeypots, 0.1, 0.1, 0.7)
    agent = ddqn_agent_3x_simple_state_fnrfpr_v2.DoubleDeepQLearning(env, 0.99, 0.1, 200, normal_nodes, totalpermutation, 0.2, 0.14)

    action = agent.selectActionInferenceConv1D(network_state, model_infer)
    
    # saving action for continuous learning
    rt_action_buffer.append(action)
    
    deployment_targets = action

    subnet_targets = [0] * 4
    for node in deployment_targets:
        subnet = 0 if node in range(0, 2) else 1 if node in range(2, 5) else 2 if node in range(5, 8) else 3
        subnet_targets[subnet] = 1

    with open('output.tmp', 'w') as file:
        for target in subnet_targets:
            file.write(str(target) + '\n')
            
            
    # Run an asynchronous task to update the model
    # update_model.delay(rt_buffer, rt_action_buffer)
    def update_model(rt_buffer, rt_action_buffer):
        print("Starting the learning from acquired experience")
        agent.trainingInference(rt_buffer, rt_action_buffer)

    # Start a new thread to run the update_model function
    # update_thread = threading.Thread(target=update_model, args=(rt_buffer, rt_action_buffer))
    # update_thread.start()
    
    # Uncomment for synchronous test (will get some lag in prediction)
    update_model(rt_buffer, rt_action_buffer)
    
    elapsed_time = time.time() - start_time
    print("Elapsed time:", elapsed_time)

    return jsonify({'deployment_targets': deployment_targets, 'subnet': subnet_targets})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35025)
