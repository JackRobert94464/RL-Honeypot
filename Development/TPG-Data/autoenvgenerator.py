# Import the csv module to read and write csv files
import csv

# Import the random module to generate random numbers
import random

# Define the path of the cve description csv file
cve_file = "Development\\TPG-Data\\300-entries-epss.csv"

# Define the path of the epss csv file
epss_file = "Development\\TPG-Data\\epss_scores-2024-02-25.csv"

# Define the path of the output csv file for the Node TPG
ntpg_file = "Development\\TPG-Data\\ntpg_mini.csv"

# Define the path of the output csv file for the Host TPG
htpg_file = "Development\\TPG-Data\\htpg_mini.csv"

# Define the minimum and maximum number of nodes in the network
min_nodes = 5
max_nodes = 10

# Define the minimum and maximum number of CVEs per connection
min_cves = 2
max_cves = 4

# Define a list to store the CVEs and their EPSS scores
cve_list = []

# Define a list to store the nodes and their IP addresses
node_list = []

# Define a list to store the connections and their probabilities
conn_list = []

# Define a list to store the exploits and their details
exploit_list = []

# Read the cve description csv file and store the CVEs and their EPSS scores in the cve_list
with open(cve_file, "r") as cve_csv:
    cve_reader = csv.reader(cve_csv)
    next(cve_reader) # Skip the header row
    for row in cve_reader:
        print(row)
        # Get the CVE name and the description from the row
        cve_name = row[0]
        cve_desc = row[2]

        # Read the epss csv file and find the EPSS score for the CVE
        with open(epss_file, "r") as epss_csv:
            epss_reader = csv.reader(epss_csv)
            next(epss_reader) # Skip the info row
            next(epss_reader) # Skip the header row
            for line in epss_reader:
                # Get the CVE name and the EPSS score from the line
                epss_cve = line[0]
                # print(line)
                epss_score = float(line[1])

                # If the CVE names match, store the CVE, the EPSS score, and the description in the cve_list
                if cve_name == epss_cve:
                    cve_list.append((cve_name, epss_score, cve_desc))
                    break # Stop searching for the EPSS score

                
# Generate a random number of nodes in the network
num_nodes = random.randint(min_nodes, max_nodes)

# Generate random IP addresses for the nodes and store them in the node_list
for i in range(num_nodes):
    # Generate a random IP address in the form of 192.168.x.y
    ip_address = "192.168." + str(random.randint(0, 255)) + "." + str(random.randint(0, 255))

    # Check if the IP address is already in the node_list
    if ip_address in node_list:
        # If yes, generate a new IP address until it is unique
        while ip_address in node_list:
            ip_address = "192.168." + str(random.randint(0, 255)) + "." + str(random.randint(0, 255))
    
    # Store the IP address in the node_list
    node_list.append(ip_address)

# Generate random connections between the nodes and store them in the conn_list
for i in range(num_nodes):
    # Get the source node from the node_list
    source = node_list[i]

    # Generate a random number of connections for the source node
    num_conns = random.randint(1, num_nodes - 1)

    # Create a set to store the target nodes for the source node
    target_set = set()

    # Generate random target nodes for the source node
    for j in range(num_conns):
        # Get a random index from the node_list
        index = random.randint(0, num_nodes - 1)

        # Get the target node from the node_list
        target = node_list[index]

        # Check if the target node is the same as the source node or already in the target_set
        if target == source or target in target_set:
            # If yes, generate a new target node until it is different and unique
            while target == source or target in target_set:
                index = random.randint(0, num_nodes - 1)
                target = node_list[index]
        
        # Add the target node to the target_set
        target_set.add(target)

        # Generate a random number of CVEs for the connection
        num_cves = random.randint(min_cves, max_cves)

        # Create a list to store the CVEs and their EPSS scores for the connection
        cve_conn = []

        # Generate random CVEs for the connection
        for k in range(num_cves):
            # Get a random index from the cve_list
            index = random.randint(0, len(cve_list) - 1)

            # Get the CVE and its EPSS score from the cve_list
            cve = cve_list[index][0]
            epss = cve_list[index][1]

            # Check if the CVE is already in the cve_conn
            if cve in cve_conn:
                # If yes, generate a new CVE until it is unique
                while cve in cve_conn:
                    index = random.randint(0, len(cve_list) - 1)
                    cve = cve_list[index][0]
                    epss = cve_list[index][1]
            
            # Add the CVE and its EPSS score to the cve_conn
            cve_conn.append((cve, epss))

        # Calculate the user and root probabilities for the connection
        user_prob = 0
        root_prob = 0
        user_count = 0
        root_count = 0

        print(cve_conn)

        # Loop through the CVEs in the cve_conn
        for cve, epss in cve_conn:
            # Find the description of the CVE from the cve_list
            for cve_name, epss_score, cve_desc in cve_list:
                # If the CVE names match, get the description
                if cve == cve_name:
                    description = cve_desc
                    break # Stop searching for the description
            
            # Check if the description contains the word "root"
            if "root" in description.lower():
                # If yes, add the EPSS score to the root probability and increment the root count
                root_prob += epss
                root_count += 1
            else:
                # If no, add the EPSS score to the user probability and increment the user count
                user_prob += epss
                user_count += 1
        
        # Calculate the average user and root probabilities for the connection
        user_prob = user_prob / user_count if user_count > 0 else 0
        print(user_prob)
        print(user_count)
        print(root_prob)
        print(root_count)
        root_prob = root_prob / root_count if root_count > 0 else 0

        # Store the source, target, user probability, and root probability in the conn_list
        conn_list.append((source, target, user_prob, root_prob))

        # Loop through the CVEs in the cve_conn
        for cve, epss in cve_conn:
            # Find the description and the privilege of the CVE from the cve_list
            for cve_name, epss_score, cve_desc in cve_list:
                # If the CVE names match, get the description and the privilege
                if cve == cve_name:
                    description = cve_desc
                    # Check if the description contains the word "root"
                    if "root" in description.lower():
                        # If yes, set the privilege to Root
                        privilege = "Root"
                    else:
                        # If no, set the privilege to User
                        privilege = "User"
                    break # Stop searching for the description and the privilege
            
            # Store the source, description, CVE, EPSS score, target, and privilege in the exploit_list
            exploit_list.append((source, description, cve, epss, target, privilege))

# Write the Node TPG to the output csv file
with open(ntpg_file, "w") as ntpg_csv:
    ntpg_writer = csv.writer(ntpg_csv)
    # Write the header row
    ntpg_writer.writerow(["source", "target", "user_prob", "root_prob"])
    # Write the data rows
    for row in conn_list:
        ntpg_writer.writerow(row)

# Write the Host TPG to the output csv file
with open(htpg_file, "w") as htpg_csv:
    htpg_writer = csv.writer(htpg_csv)
    # Write the header row
    htpg_writer.writerow(["source", "service", "cve", "exploit_prob", "target", "privilege"])
    # Write the data rows
    for row in exploit_list:
        htpg_writer.writerow(row)

# Print a message to indicate the completion of the code
print("The code has finished running and the output files have been created.") 
