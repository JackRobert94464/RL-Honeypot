def ntpg_to_connection_matrix(ntpg):
  """
  Converts a Node Threat Penetration Graph (_ntpg) dictionary to a K*K connection matrix.

  Args:
      ntpg: A dictionary representing the Node Threat Penetration Graph.

  Returns:
      A K*K numpy matrix representing the connections between nodes (1 for connection, 0 for no connection).
  """
  nodes = list(ntpg.keys())
  K = len(nodes)
  connection_matrix = [[0 for _ in range(K)] for _ in range(K)]

  for node_i, neighbors in ntpg.items():
    i = nodes.index(node_i)
    for neighbor, _, _ in neighbors:
      j = nodes.index(neighbor)
      connection_matrix[i][j] = 1  # Mark connection (one-way)

  return connection_matrix

# Example usage
_ntpg = {'192.168.1.3': [('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0),('192.168.2.3', 0,0.9756)],
                      '192.168.2.3': [('192.168.1.3', 0,0.0009),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.2.4': [('192.168.2.3', 0,0.9756),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.3.3': [],
                      '192.168.3.4': [('192.168.3.5', 0,0.0009)],
                      '192.168.3.5': [('192.168.4.3', 0,0.9756)],
                      '192.168.4.3': [('192.168.3.4', 0,0.9756),('192.168.3.5', 0,0.0009),('192.168.3.3', 0.9746,0)],}

connection_matrix = ntpg_to_connection_matrix(_ntpg)

# Print the epss matrix (replace with your preferred output method)
# Define a formatting string with spacing and newlines
format_string = "{:.4f} " * len(connection_matrix[0]) + "\n"

for row in connection_matrix:
  print(format_string.format(*row))