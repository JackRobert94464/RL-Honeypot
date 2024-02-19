# Assuming the csv file is stored as 'data.csv' in the same directory as this code
import csv

class TPG-Converter():
    def __init__(self):
        self._ntpg = None

    def csv_to_ntpg(self, csv_file):
        # Initialize an empty dictionary
        self._ntpg = {}

        # Open the csv file and read the rows
        with open(csv_file) as f:
            reader = csv.reader(f)
            # Skip the header row
            next(reader)
            # Loop through the remaining rows
            for row in reader:
                # Extract the source, target, user_prob and root_prob values
                source = row[0]
                target = row[1]
                user_prob = float(row[2])
                root_prob = float(row[3])
                # Check if the source is already in the dictionary
                if source in self._ntpg:
                    # Append the target and the probabilities as a tuple to the existing list
                    self._ntpg[source].append((target, user_prob, root_prob))
                else:
                    # Create a new list with the target and the probabilities as a tuple
                    self._ntpg[source] = [(target, user_prob, root_prob)]
                # Check if the target is already in the dictionary
                if target not in self._ntpg:
                    # Create an empty list for the target
                    self._ntpg[target] = []

        # Print the dictionary
        print(self._ntpg)

        return self._ntpg
    
    def csv_to_htpg(self, htpg):
        

