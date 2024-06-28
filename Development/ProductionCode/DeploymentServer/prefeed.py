import random
import json
import subprocess
import time

# Pre-feed the agent with batches of [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
for _ in range(10):
    network_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(10):
        # Randomly add 1 to the network state
        network_state[i] = random.randint(0, 1)
        print(network_state)
        if network_state[5] == 1:
            print("Important resource Node 5 is attacked!")
            break
        
        # Create a JSON payload with the network state and num_honeypots
        payload = {
            'network_state': network_state,
            'num_honeypots': 2  # Set the number of honeypots to 0 for pre-feeding
        }
        
        # Send a POST request to the predict endpoint using curl
        curl_command = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(payload)}' http://localhost:35025/predict"
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        response = json.loads(result.stdout)
        if response.get('hit') == True:
            break
        # Wait for 20 seconds before sending the next curl
        # time.sleep(5)