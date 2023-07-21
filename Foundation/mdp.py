import numpy as np

class MDP:
    # I'm trying to implement Markov Decision Process (MDP) with the Cartpole environment
    # The MDP is a tuple (S, A, P, R, gamma)
    # S: set of states
    # A: set of actions
    # P: transition probability matrix
    # R: reward function
    # gamma: discount factor

    def __init__(self, env):
        self.env = env
        self.S = env.observation_space
        self.A = env.action_space
        self.P = np.zeros((self.S, self.A, self.S))
        self.R = np.zeros((self.S, self.A, self.S))
        self.gamma = 0.99

    
    


def main():
    print("Hello World!")

if __name__ == "__main__":
    main()