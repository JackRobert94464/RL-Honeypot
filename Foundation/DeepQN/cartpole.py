#!/usr/bin/env python3

import time
from keras.models import Sequential
from keras.layers import Dense, Dropout
# from keras.optimizers import Adam
from keras.optimizers.legacy import Adam
import gym
from dqn import DQN


if __name__ == "__main__":
    # create environment
    env = gym.make('CartPole-v1')
    n_inputs = env.observation_space.shape[0]
    n_actions = env.action_space.n
    max_theta = env.observation_space.high[2]
    def cartpole_reward(observation):
        return max_theta - abs(observation[2])

    # create model
    model = Sequential()
    model.add(Dense(units=24, activation="tanh", input_dim=n_inputs))
    model.add(Dense(units=24, activation="tanh"))
    model.add(Dense(units=n_actions, activation="linear"))
    model.compile(loss="mse", optimizer=Adam(lr=0.1, decay=0.03))

    agent = DQN(model, env)
    start = time.time()
    agent.fit()
    print("Elapsed time: %.1f seconds" % (time.time()-start))