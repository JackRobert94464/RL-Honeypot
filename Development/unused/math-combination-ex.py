import itertools

# Define a list of numbers
my_list = [1, 2, 3, 4, 5, 6, 7]

# Generate all possible two-element combinations
# Convert the resulting iterator to a list
combinations = list(itertools.combinations(my_list, 2))

dict_combinations = dict(enumerate(combinations))

# Print the list of combinations to the console
print(combinations, len(combinations))


print(dict_combinations)

# Output: [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 4), (3, 5), (3, 6), (3, 7), (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7)] 21