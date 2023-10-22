import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.environments import suite_gym
from tf_agents.trajectories import time_step as ts

N = 10 # Total amount of nodes (n)
M = 3  # Number of deception nodes (m)
K = N - M  # Number of normal nodes (k)
P = 0.8 # Probability of attacker moving to the next node
Q = 0.2 # Probability of attacker moving to a random node

print(array_spec.BoundedArraySpec(
            shape=(N,), dtype=np.int32, minimum=0, maximum=1, name='observation'))