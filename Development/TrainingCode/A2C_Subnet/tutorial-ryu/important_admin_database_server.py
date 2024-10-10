import socket

def is_ip_allowed(ip):
    # Placeholder function to check if IP is allowed
    # In a real scenario, this would check against a list of known IPs or network topology
    allowed_ips = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    return ip in allowed_ips

def handle_client_connection(client_socket, client_address):
    client_ip = client_address[0]
    if is_ip_allowed(client_ip):
        response = "Welcome to the important service."
    else:
        response = "Unauthorized access detected. This incident will be reported."
    
    client_socket.send(response.encode())
    client_socket.close()

def start_important_service(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Important service listening on port {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        handle_client_connection(client_socket, client_address)

if __name__ == "__main__":
    important_service_port = 15000  # Port number greater than 10000
    start_important_service(important_service_port)