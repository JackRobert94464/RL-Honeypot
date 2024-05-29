import itertools
action_spec = {
            'type': 'multi_discrete',
            'nvec': list(itertools.combinations(range(1, 7+1), 2))
        }
print("Action spec:", action_spec)