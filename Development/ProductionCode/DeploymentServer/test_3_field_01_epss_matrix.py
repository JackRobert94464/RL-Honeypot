def ntpg_to_epss_matrix(ntpg):
  """
  Converts a Node Threat Penetration Graph (_ntpg) dictionary to a K*K epss matrix.

  Args:
      ntpg: A dictionary representing the Node Threat Penetration Graph.

  Returns:
      A K*K numpy matrix representing the epss scores between nodes.
  """
  nodes = list(ntpg.keys())
  K = len(nodes)
  epss_matrix = [[0 for _ in range(K)] for _ in range(K)]

  for i, node_i in enumerate(nodes):
    for neighbor, user_epss, root_epss in ntpg[node_i]:
      j = nodes.index(neighbor)
      # Average the user_epss and root_epss values
      avg_epss = (user_epss + root_epss) / 2
      epss_matrix[i][j] = avg_epss

  # Fill the lower triangle (symmetric matrix)
  for i in range(K):
    for j in range(i + 1, K):
      epss_matrix[j][i] = epss_matrix[i][j]

  return epss_matrix

# Example usage
_ntpg = {'192.168.1.3': [('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0),('192.168.2.3', 0,0.9756)],
                      '192.168.2.3': [('192.168.1.3', 0,0.0009),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.2.4': [('192.168.2.3', 0,0.9756),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.3.3': [],
                      '192.168.3.4': [('192.168.3.5', 0,0.0009)],
                      '192.168.3.5': [('192.168.4.3', 0,0.9756)],
                      '192.168.4.3': [('192.168.3.4', 0,0.9756),('192.168.3.5', 0,0.0009),('192.168.3.3', 0.9746,0)],}

epss_matrix = ntpg_to_epss_matrix(_ntpg)

# Print the epss matrix (replace with your preferred output method)
# Define a formatting string with spacing and newlines
format_string = "{:.4f} " * len(epss_matrix[0]) + "\n"

for row in epss_matrix:
  print(format_string.format(*row))
