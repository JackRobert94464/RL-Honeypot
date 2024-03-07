import pandas as pd

# Read the CSV file
df = pd.read_csv('handclean-entryonly.csv')

# Create a new column 'NewColumn' with default value 'user'
df['Priviledge'] = 'user'

# Check each cell for the word 'root'
for index, row in df.iterrows():
    for cell in row:
        if 'root' in str(cell).lower():
            df.at[index, 'Priviledge'] = 'root'

# Save the updated DataFrame back to CSV
df.to_csv('handclean-entry-processed.csv', index=False)