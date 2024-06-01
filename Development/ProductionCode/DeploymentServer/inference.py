import tensorflow as tf
import numpy as np
import json
import socket

# Import necessary components
from ddqn_loss_fn import ddqn_loss_fn
from NetworkHoneypotEnv_base import NetworkHoneypotEnv

class Inference:
    def __init__(self, model_path, deployment_server_ip, deployment_server_port, num_honeypots):
        self.model_path = model_path
        self.deployment_server_ip = deployment_server_ip
        self.deployment_server_port = deployment_server_port
        self.num_honeypots = num_honeypots
        self.trained_model = self.load_trained_model(model_path)
    
    def load_trained_model(self, model_path):
        trained_model = tf.keras.models.load_model(model_path, custom_objects={'loss': ddqn_loss_fn})
        return trained_model

    def listen_for_state_updates(self):
        # This is a mock function to simulate listening to NMS updates.
        # Replace it with actual socket server/client code or other IPC mechanisms.
        while True:
            # Simulating receiving a state update
            network_state = self.receive_state_update()
            if network_state is not None:
                print(f"Received network state: {network_state}")
                honeypot_placement = self.predict_honeypot_placement(network_state)
                self.send_placement_to_deployment_server(honeypot_placement)
    
    def receive_state_update(self):
        # Placeholder for receiving state update, should be replaced with actual implementation
        # Simulating receiving state [0, 1, 0, 0, 1, 0]
        # return np.random.choice([0, 1], size=(6,), replace=True)
        return np.array([0, 1, 0, 0, 1, 0])

    def predict_honeypot_placement(self, network_state):
        # Get the model's prediction
        network_state = np.expand_dims(network_state, axis=0)  # Add batch dimension
        predictions = self.trained_model.predict(network_state)
        # Select top-N nodes based on the model's predictions
        predicted_indices = np.argsort(predictions[0])[-self.num_honeypots:]
        return predicted_indices.tolist()

    def send_placement_to_deployment_server(self, honeypot_placement):
        message = json.dumps({"honeypot_placement": honeypot_placement})
        print(f"Sending honeypot placement: {honeypot_placement}")
        
        # Send the JSON message to the deployment server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.deployment_server_ip, self.deployment_server_port))
            sock.sendall(message.encode('utf-8'))
            response = sock.recv(1024)
            print(f"Deployment server response: {response.decode('utf-8')}")
    
    def start_inference(self):
        self.listen_for_state_updates()

if __name__ == "__main__":
    model_path = ".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_1to5_obsdense_decoy_linux_ver30000.keras"
    deployment_server_ip = "127.0.0.1"  # Replace with actual IP
    deployment_server_port = 8080  # Replace with actual port
    num_honeypots = 2  # Number of honeypots to deploy

    inference = Inference(model_path, deployment_server_ip, deployment_server_port, num_honeypots)
    inference.start_inference()
