# Visualize the environment
import os
import imageio
import matplotlib.pyplot as plt
import networkx as nx

def visualize_steps(steps, your_nodes_list, your_edges_list, output_folder, output_movie, episode):
    G = nx.Graph()
    G.add_nodes_from(your_nodes_list)
    G.add_edges_from(your_edges_list)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = []

    for i, step in enumerate(steps):
        plt.figure()
        colors = []
        text = ""
        for node in G.nodes:
            if node == step['attacker_node']:
                if node in step['nifr_nodes']:
                    colors.append('purple')
                    text = "NIFR has been attacked. Defender wins."
                elif node in step['nicr_nodes']:
                    colors.append('yellow')
                    text = "NICR has been attacked. Defender loses."
                else:
                    colors.append('red')
            elif node in step['nifr_nodes']:
                colors.append('blue')
            elif node in step['nicr_nodes']:
                colors.append('orange')  # Color for NICR node
            else:
                colors.append('green')

        nx.draw(G, with_labels=True, node_color=colors)
        plt.figtext(0.1, 0.02, f"Episode: {episode}", transform=plt.gca().transAxes)
        plt.figtext(0.1, 0.04, text, transform=plt.gca().transAxes)
        image_path = os.path.join(output_folder, f'{episode}_step_{i}.png')
        plt.savefig(image_path)
        images.append(imageio.imread(image_path))
        plt.close()

    imageio.mimsave(output_movie, images, duration=500)