from collections import defaultdict
from bson import ObjectId


def process_topology(mongo_data):
    # Initialize the NTPG dictionary
    ntpg = defaultdict(list)

    # Create a lookup for switches and their connections
    switch_connections = {}
    for switch in mongo_data['switch']:
        switch_name = switch['switch_name']
        switch_connections[switch_name] = [conn['connected_to'] for conn in switch['switch_connections']]

    # Create a lookup for nodes by their connected switch
    nodes_by_switch = defaultdict(list)
    node_data = mongo_data['nodes']

    for node in node_data:
        nodes_by_switch[node['node_subnet']].append(node)

    # Traverse through nodes and determine connectivity
    for node in node_data:
        node_name = node['node_name']
        current_switch = node['node_subnet']

        # Gather all nodes connected within the current switch
        connected_switches = switch_connections.get(current_switch, [])
        directly_connected_nodes = nodes_by_switch[current_switch]

        # Nodes connected to other switches, if switches are interconnected
        for connected_switch in connected_switches:
            directly_connected_nodes += nodes_by_switch.get(connected_switch, [])

        for connected_node in directly_connected_nodes:
            # Avoid self-loop and only add if the node isn't blocked from accessing the other node
            if connected_node['node_name'] != node_name and node_name not in connected_node['blocked_from']:
                # Add to NTPG: (connected_node_name, EPSS, subnet)
                ntpg[node_name].append(
                    (connected_node['node_name'], (node['node_EPSS'] + connected_node['node_EPSS']) / 2, connected_node['node_subnet'])
                )

    return dict(ntpg)

# Example usage with the given MongoDB data:
mongo_data = {'nodes': [{'node_name': 'h1', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.1', 'node_connections': [{'connected_to': 's1'}], 'node_subnet': 's1', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4cf9')}, 
                        {'node_name': 'h2', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.2', 'node_connections': [{'connected_to': 's1'}], 'node_subnet': 's1', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4cfa')}, 
                        {'node_name': 'h3', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.3', 'node_connections': [{'connected_to': 's2'}], 'node_subnet': 's2', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4cfb')}, 
                        {'node_name': 'h4', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.4', 'node_connections': [{'connected_to': 's2'}], 'node_subnet': 's2', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4cfc')}, 
                        {'node_name': 'h5', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.5', 'node_connections': [{'connected_to': 's2'}], 'node_subnet': 's2', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4cfd')}, {'node_name': 'h6', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.6', 'node_connections': [{'connected_to': 's3'}], 'node_subnet': 's3', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4cfe')}, {'node_name': 'h7', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.7', 'node_connections': [{'connected_to': 's3'}], 'node_subnet': 's3', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4cff')}, {'node_name': 'h8', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.8', 'node_connections': [{'connected_to': 's3'}], 'node_subnet': 's3', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4d00')}, {'node_name': 'h9', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.9', 'node_connections': [{'connected_to': 's4'}], 'node_subnet': 's4', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4d01')}, {'node_name': 'h10', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.10', 'node_connections': [{'connected_to': 's4'}], 'node_subnet': 's4', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4d02')}, {'node_name': 'h32', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.11', 'node_connections': [{'connected_to': 's111'}], 'node_subnet': 's111', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4d03')}, {'node_name': 'h1337', 'node_EPSS': 0.5, 'node_ipv4': '10.0.0.12', 'node_connections': [{'connected_to': 's111'}], 'node_subnet': 's111', 'blocked_from': [], '_id': ObjectId('670350e2b6981a1015af4d04')}], 
              'switch': [{'switch_name': 's1', 'switch_EPSS': 0.5, 'switch_connections': [{'connected_to': 's111'}], '_id': ObjectId('670350e2b6981a1015af4d05')}, {'switch_name': 's2', 'switch_EPSS': 0.5, 'switch_connections': [{'connected_to': 's111'}], '_id': ObjectId('670350e2b6981a1015af4d06')}, {'switch_name': 's3', 'switch_EPSS': 0.5, 'switch_connections': [{'connected_to': 's111'}], '_id': ObjectId('670350e2b6981a1015af4d07')}, {'switch_name': 's4', 'switch_EPSS': 0.5, 'switch_connections': [{'connected_to': 's111'}], '_id': ObjectId('670350e2b6981a1015af4d08')}, {'switch_name': 's111', 'switch_EPSS': 0.5, 'switch_connections': [{'connected_to': 's1'}, {'connected_to': 's2'}, {'connected_to': 's3'}, {'connected_to': 's4'}], '_id': ObjectId('670350e2b6981a1015af4d09')}]}
ntpg = process_topology(mongo_data)
print(ntpg)
