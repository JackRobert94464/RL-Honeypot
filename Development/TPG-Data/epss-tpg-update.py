import csv

def update_probabilities():
    """Updates exploit_prob in htpg based on cve-epss and user/root probs in ntpg based on htpg."""

    # Load cve-epss data
    cve_epss = {}
    with open("cve-epss.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            cve_epss[row[0]] = float(row[1])

    # Update exploit_prob in htpg
    with open("htpg.csv", "r") as infile, open("htpg_updated.csv", "w", newline="") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        header = next(reader)  # Preserve header row
        writer.writerow(header)

        for row in reader:
            cve = row[2]
            if cve in cve_epss:
                row[3] = cve_epss[cve]  # Update exploit_prob
            writer.writerow(row)

    # Update user/root probs in ntpg
    with open("htpg_updated.csv", "r") as htpg_file, open("ntpg.csv", "r") as infile, open("ntpg_updated.csv", "w", newline="") as outfile:
        htpg_reader = csv.reader(htpg_file)
        ntpg_reader = csv.reader(infile)
        ntpg_writer = csv.writer(outfile)
        header = next(ntpg_reader)  # Preserve header row
        ntpg_writer.writerow(header)

        htpg_data = {tuple(row[:2]): row[-1] for row in htpg_reader}  # Create a dictionary for efficient htpg lookup

        for row in ntpg_reader:
            source_target = tuple(row[:2])
            privilege = htpg_data.get(source_target)  # Get privilege from htpg
            if privilege:
                if privilege == "User":
                    row[2] = 1.0  # Set user_prob to 1.0 if privilege is User
                else:
                    row[3] = 1.0  # Set root_prob to 1.0 if privilege is Root
            ntpg_writer.writerow(row)

if __name__ == "__main__":
    update_probabilities()
