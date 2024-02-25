import csv
from epss_api import EPSS

# EPSS probabilities retrieval function (modified for robustness)
def epss_retrieval(cve):
    """Retrieves EPSS probabilities for a given CVE, handling errors.

    Args:
        cve (str): The CVE identifier.

    Returns:
        dict: A dictionary containing the EPSS probabilities if successful,
              or None if an error occurs.
    """

    try:
        # Create an EPSS object
        epss_cli = EPSS()

        # Get the probabilities
        probabilities = epss_cli.epss(cve)

        return probabilities
    except Exception as e:
        print(f"Error retrieving probabilities for {cve}: {e}")
        return None


def main():
    """Reads CVE data from a CSV file, retrieves EPSS data, and writes the results to a new file."""

    input_file = "selected-300-entries.csv"
    output_file = "300-entries-epss.csv"

    with open(input_file, "r") as csvfile, open(output_file, "w") as outputfile:
        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(outputfile, fieldnames=reader.fieldnames + ["EPSS Probabilities"])

        writer.writeheader()

        for row in reader:
            cve = row["Name"]
            probabilities = epss_retrieval(cve)

            row["EPSS Probabilities"] = probabilities or "Error retrieving data"
            print(f"Retrieved EPSS data for {cve}")
            writer.writerow(row)

    print(f"Output file with EPSS data: {output_file}")


if __name__ == "__main__":
    main()