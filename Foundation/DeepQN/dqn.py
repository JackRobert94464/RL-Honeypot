import random
from collections import deque
import numpy as np

class DQN:
    def __init__(self, model, env,
                 epsilon=0.5, epsilon_decay=0.995, epsilon_min=0.1,
                 gamma=0.995,
                 history_size=10000, epochs=10, train_size=10000, batch_size=256,
                 max_steps=5000,
                 log_every_n_steps=50,
                 evalutation_size=10,
                 target_score=500,
                 reward_func=None):
        """
        DQN - Reinforcement learning agent
        Parameters:
            model: model with fit() and predict() methods
            env: gym environment
            epsilon: probability of random actions
            epsilon_decay: decay of epsilon on the next training episode
            epsilon_min: minimum value of epsilon
            gamma: discount for the next state
            history_size: total number of stored observations among all episodes
            epochs: number of training epochs per episode
            train_size: number of obervations to train on after each episode
            batch_size: batch size for fit() method of the model
            max_steps: maximum number of steps in episode
            log_every_n_steps: output metrics every n steps
            evalutation_size: number of episodes in evaluations
            target_score: target score to finish when reached
            reward_func: function that transforms observations to rewards; use None for model-free RL
        """

        self.model = model
        self.env = env
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.gamma = gamma
        self.history_size = history_size
        self.epochs = epochs
        self.train_size = train_size
        self.batch_size = batch_size
        self.max_steps = max_steps
        self.log_every_n_steps = log_every_n_steps
        self.evalutation_size = evalutation_size
        self.target_score = target_score
        self.reward_func = reward_func

        self._epsilon = self.epsilon  # current epsilon
        self.history = deque(maxlen=self.history_size)
        self.scores = list()  # list of scores for each played episode

        assert self.model, "Model is not provided"
        model_methods = ("fit", "predict")
        for method_name in model_methods:
            assert callable(getattr(self.model, method_name, None)), "Invalid model: no %s() method" % method_name

        assert self.env, "Gym environment is not provided"
        model_methods = ("reset", "step", "render")
        for method_name in model_methods:
            assert callable(getattr(self.env, method_name, None)), "Invalid env: no %s() method" % method_name

        self.n_inputs = self.env.observation_space.shape[0]
        self.n_actions = self.env.action_space.n

        # columns offsets in a numpy row (see fit_one())
        self.STATE_idx = 0  # observation
        self.NEXT_STATE_idx = self.n_inputs  # next observation
        self.ACTION_idx = 2 * self.n_inputs
        self.DONE_idx = 2 * self.n_inputs + 1
        self.R_idx = 2 * self.n_inputs + 2
        self.MAXQ_idx = 2 * self.n_inputs + 3

    def get_action(self, observation):
        """
        Policy function: returns action for the given observation
        """

        return np.argmax(self.model.predict(observation.reshape(1,-1))[0])


    def fit_one(self):
        """
        Train the model on a single episode
        """

        score = 0
        observation = self.env.reset()
        done = False

        for _ in range(self.max_steps):
            if random.random() < self._epsilon:
                # explore - take random action
                action = self.env.action_space.sample()
            else:
                # exploit - take predicted action
                action = self.get_action(observation)

            next_observation, reward, done, info = self.env.step(action)

            if self.reward_func:  # redefine reward if reward_func is set
                reward_ = self.reward_func(next_observation)
            else:
                reward_ = reward

            # append row for further training
            self.history.append(list(observation) + list(next_observation) + \
                [action, done, reward_, 0] + [0] * self.n_actions)

            score += reward
            if done:
                break
            observation = next_observation

        # append last episode score to list of scores
        self.scores.append(score)

        # prepare training data:
        data = np.array(random.sample(self.history, min(self.train_size, len(self.history))))

        # predict max(Q'):
        data[:, self.MAXQ_idx] = np.max(self.model.predict(data[:, self.NEXT_STATE_idx:self.NEXT_STATE_idx+self.n_inputs]), axis=1)

        # predict Q:
        data[:, -self.n_actions:] = self.model.predict(data[:, :self.n_inputs])

        for i in range(self.n_actions):
            # Q(s,a) = r + gamma * max(Q(s',a'))
            data[data[:, self.ACTION_idx] == i, -self.n_actions+i] = \
                data[data[:, self.ACTION_idx] == i, self.R_idx] + \
                self.gamma * data[data[:, self.ACTION_idx] == i, self.MAXQ_idx]

            # set Q(s,a) to 1 if done:
            data[(data[:, self.DONE_idx] == 1) & (data[:, self.ACTION_idx] == i), -self.n_actions + i] = 1

        self.model.fit(
            data[:, :self.n_inputs],
            data[:, -self.n_actions:],
            batch_size=self.batch_size,
            epochs=10,
            verbose=0)
        self._epsilon = max(self.epsilon_min, self._epsilon*self.epsilon_decay)

    def fit(self, episodes=2000):
        """
        Fit the model
        """

        for i in range(1, episodes + 1):
            self.fit_one()
            
            if i % self.log_every_n_steps==0:
                score = self.evaluate()
                print("Episode %i/%i: avg. score=%.1f, epsilon=%.2f, history_size=%i, train_size=%i" % (
                    i, episodes, score, self._epsilon, len(self.history), min(self.train_size, len(self.history))))
                if score >= self.target_score:
                    print("Target score achieved: target=%.1f, actual=%.1f" % (self.target_score, score))
                    return

        print("Target score is not reached")

    def evaluate(self, render_games=1):
        """
        Evaluate the model's performance without random actions

        render_games: number of games withing evaluation_size to render on screen
        """

        scores = list()
        for _ in range(self.evalutation_size):
            score = 0
            observation = self.env.reset()

            for j in range(self.max_steps):
                if _ < render_games:  # render only `render_games` episodes
                    self.env.render()
                action = self.get_action(observation)
                next_observation, reward, done, info = self.env.step(action)
                score += reward
                if done: break
                observation = next_observation
            scores.append(score)
        return np.mean(scores)