import pandas as pd

class Miscellaneous:
    def __init__(self):
        pass
    
    def create_dictionary_ntpg(self):
        # Read the CSV file into a pandas dataframe
        df = pd.read_csv("ntpg.csv")

        # Create an empty dictionary
        ntpg = {}

        # Iterate through each row in the dataframe
        for index, row in df.iterrows():
            source = row["source"]
            target = row["target"]
            user_prob = row["user_prob"]
            root_prob = row["root_prob"]
        
            # If the source is not already a key in the dictionary, add it as a key with an empty list as the value
            if source not in ntpg:
                ntpg[source] = []
            
            # Append a tuple containing the target, user_prob, and root_prob to the list associated with the source key
            ntpg[source].append((target, user_prob, root_prob))

            # Print the dictionary
            print(ntpg)

        return ntpg

    def create_dictionary_htpg(self):
        # Read the CSV file into a pandas dataframe
        df = pd.read_csv("htpg.csv")

        # Create an empty dictionary
        htpg = {}

        # Define a function to process each row
        def process_row(row):
            source = row["source"]
            service = row["service"]
            cve = row["cve"]
            exploit_prob = float(row["exploit_prob"])  # Convert exploit_prob to float
            target = row["target"]
            privilege = row["privilege"]
            return (service, cve, exploit_prob, (target, privilege))

        # Iterate through each row in the dataframe
        for index, row in df.iterrows():
            source = row["source"]
            
            # Process the row using the defined function
            service, cve, exploit_prob, target_info = process_row(row)
            
            # If the source is not already a key in the dictionary, add it as a key with an empty list as the value
            if source not in htpg:
                htpg[source] = []
            
            # Append a tuple containing the service, cve, exploit_prob, and target_info to the list associated with the source key
            htpg[source].append((service, cve, exploit_prob, target_info))

        # Print the dictionary
        print(htpg)

        return htpg

# create_dict = Miscellaneous()
# create_dict.create_dictionary()
# create_dict.create_dictionary_htpg()
