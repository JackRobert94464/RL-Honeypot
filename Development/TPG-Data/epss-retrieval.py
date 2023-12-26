# Import csv module
import csv

# Import epss module
from epss_api import EPSS

# EPSS probabilties retrieval function
def epss_retrieval(cve):
    # Create an EPSS object
    epss_cli = EPSS()

    # Get the probabilities
    probabilities = epss_cli.epss(cve)

    # Return the probabilities
    return probabilities

# sample
print(epss_retrieval('CVE-2012-0002'))

# Read the csv file
with open("cve.csv", "r") as cvefile:
    # Create a csv reader object
    reader = csv.reader(cvefile)

    # Open the csv file in write mode
    with open("cve-epss.csv", "w") as outputfile:
        # Create a csv writer object
        writer = csv.writer(outputfile)

        # Create a set to store unique rows
        unique_rows = set()

        # Loop through the rows
        for row in reader:
            # Get the probabilities
            probabilities = epss_retrieval(row[0])

            # Append the probabilities to the row
            row.append(probabilities)

            # Convert the row to a tuple for set comparison
            row_tuple = tuple(row)

            # Check if the row is unique
            if row_tuple not in unique_rows:
                # Write the updated row to the csv file
                writer.writerow(row)

                # Add the row to the set of unique rows
                unique_rows.add(row_tuple)
    
