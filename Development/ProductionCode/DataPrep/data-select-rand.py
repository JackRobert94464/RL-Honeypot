import pandas as pd

# Read your CSV file (replace 'my_data.csv' with your actual file path)
df = pd.read_csv('handclean-entry-processed.csv')

# Randomly sample 300 rows
random_sample = df.sample(n=300)

# Save the sampled data to a new CSV file
random_sample.to_csv('selected-300-entries.csv', index=False)
