import socket
import json

def start_server(ip_address='0.0.0.0', port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip_address, port))
        server_socket.listen(1)
        print(f"Server listening on {ip_address}:{port}")

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"Connection from {client_address}")
                data = client_socket.recv(100000)
                if data:
                    try:
                        json_data = data.decode('utf-8',"ignore")
                        cleaned_data = json_data.replace('\\u0000', '')
                        print("Cleaned data:", cleaned_data)  # Log cleaned data
                        # print("Raw data received:", json_data)  # Log raw data
                        # alert_data = json.loads(json_data)
                        # print("Received JSON data:", alert_data)
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON data: {e}")
                    except UnicodeDecodeError as e:
                        print(f"Failed to decode data to UTF-8: {e}")

if __name__ == "__main__":
    start_server()