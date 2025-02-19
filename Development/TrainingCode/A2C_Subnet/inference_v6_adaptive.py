import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
import misc
import ddqn_loss_fn
from collections import deque
import random
import time
import json
import subprocess

import a2c_adaptive
import threading

# Default value
# ntpg_infer_csv = "ntpg_inf.csv"
# htpg_infer_csv = "htpg_inf.csv"

# change accordingly
mongoDB_ip = 'localhost'
mongoDB_port = 27017

# Load the trained model
model_path = 'adaptive_A2C_big_actor.keras'

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
# Fix this to use mongoDB data
ntpg = misc.load_data_from_mongo_test01(mongoDB_ip, mongoDB_port)

# use this to test on local csv data
# ntpg = misc.load_ntpg_data("ntpg_inf.csv")

@app.route('/predict', methods=['POST'])
def predict():
    request_data = request.get_json()
    # print(request_data)
    # print(type(request_data))
    network_state = request_data['network_state']
    num_honeypots = request_data['num_honeypots']
    
    start_time = time.time()
    
    # saving state for continuous learning
    rt_buffer.append(network_state)
    
    
    normal_nodes = len(network_state)
    deception_nodes_amount = num_honeypots
    totalpermutation = misc.calculate_permutation(normal_nodes, deception_nodes_amount)

    # agent = Agent.get_instance(model=model_infer, ntpg_dir=ntpg_infer_csv, htpg_dir=htpg_infer_csv, honeypotAvailable=num_honeypots)
    env = misc.create_environment_from_baseEnv(ntpg, num_honeypots, 0.1, 0.1, 0.7, 5)
    agent = a2c_adaptive.PPOAgent('adaptiveA2C-01_actor', env, 0.99, 0.1, 200, normal_nodes, totalpermutation, 0.2, 0.14)
    

    action = agent.selectActionInference(network_state, model_infer)
    
    # saving action for continuous learning
    rt_action_buffer.append(action)
    
    deployment_targets = action

    subnet_targets = [0] * 4
    for node in deployment_targets:
        subnet = 0 if node in range(0, 2) else 1 if node in range(2, 5) else 2 if node in range(5, 8) else 3
        subnet_targets[subnet] = 1
        
    # Check if at least 2 subnets have '1'
    num_subnet_targets = sum(subnet_targets)
    if num_subnet_targets < 2:
        # Find the subnets with '0' and randomly select one to turn to '1'
        subnets_with_zero = [i for i, subnet in enumerate(subnet_targets) if subnet == 0]
        subnet_to_turn = random.choice(subnets_with_zero)
        subnet_targets[subnet_to_turn] = 1

    with open('../output.tmp', 'w') as file:
        for target in subnet_targets:
            file.write(str(target) + '\n')
            
    
    # Check for hits
    hit = False
    for node in deployment_targets:
        subnet = 0 if node in range(0, 2) else 1 if node in range(2, 5) else 2 if node in range(5, 8) else 3
        if subnet_targets[subnet] == 1:
            hit = True
            break
            
            
    # Run an asynchronous task to update the model
    # update_model.delay(rt_buffer, rt_action_buffer)
    def update_model_sync(rt_buffer, rt_action_buffer):
        print("Starting the learning from acquired experience")
        agent.trainingInferenceSync(rt_buffer, rt_action_buffer)
        
    def update_model_async(rt_buffer, rt_action_buffer):
        print("Starting the learning from acquired experience")
        agent.trainingInferenceAsync(rt_buffer, rt_action_buffer)

    # Start a new thread to run the update_model function
    # update_thread = threading.Thread(target=update_model_async, args=(rt_buffer, rt_action_buffer))
    
    # Wait for the update_thread to finish before starting a new thread
    # if not update_thread.is_alive():
    #     update_thread.start()
    
    # Uncomment for synchronous test (will get some lag in prediction)
    # update_model_sync(rt_buffer, rt_action_buffer)
    
    # Uncomment everything for a pure inference
    
    elapsed_time = time.time() - start_time
    print("Elapsed time:", elapsed_time)
    
    

    return jsonify({'deployment_targets': deployment_targets, 'subnet': subnet_targets, 'elapsed_time': elapsed_time, 'hit': hit, 'network_state': network_state})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35025)