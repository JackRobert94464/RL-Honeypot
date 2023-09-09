import numpy as np
import random
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import RMSprop
from collections import deque
from tensorflow import gather_nd
from tensorflow.keras.losses import mean_squared_error
from tensorflow import keras

class DoubleDeepQLearning:
    def __init__(self, env, gamma, epsilon, numberEpisodes):
        self.env = env
        self.gamma = gamma
        self.epsilon = epsilon
        self.numberEpisodes = numberEpisodes
        self.stateDimension = 4
        self.actionDimension = 2
        self.replayBufferSize = 300
        self.batchReplayBufferSize = 100
        self.updateTargetNetworkPeriod = 100
        self.counterUpdateTargetNetwork = 0
        self.sumRewardsEpisode = []
        self.replayBuffer = deque(maxlen=self.replayBufferSize)
        self.mainNetwork = self.createNetwork()
        self.targetNetwork = self.createNetwork()
        self.targetNetwork.set_weights(self.mainNetwork.get_weights())
        self.actionsAppend = []

    @staticmethod
    @keras.saving.register_keras_serializable()
    def my_loss_fn(self, y_true, y_pred):
        s1, s2 = y_true.shape
        indices = np.zeros(shape=(s1, s2))
        indices[:, 0] = np.arange(s1)
        indices[:, 1] = self.actionsAppend
        loss = mean_squared_error(gather_nd(y_true, indices=indices.astype(int)), gather_nd(y_pred, indices=indices.astype(int)))
        return loss

    def createNetwork(self):
        model = Sequential()
        model.add(Dense(128, input_dim=self.stateDimension, activation='relu'))
        model.add(Dense(56, activation='relu'))
        model.add(Dense(self.actionDimension, activation='linear'))
        model.compile(optimizer=RMSprop(), loss=self.my_loss_fn, metrics=['accuracy'])
        return model

    def trainingEpisodes(self):
        for indexEpisode in range(self.numberEpisodes):
            rewardsEpisode = []
            print("Simulating episode {}".format(indexEpisode))
            (currentState, _) = self.env.reset()
            terminalState = False
            while not terminalState:
                action = self.selectAction(currentState, indexEpisode)
                (nextState, reward, terminalState, _, _) = self.env.step(action)
                rewardsEpisode.append(reward)
                self.replayBuffer.append((currentState, action, reward, nextState, terminalState))
                self.trainNetwork()
                currentState = nextState
            print("Sum of rewards {}".format(np.sum(rewardsEpisode)))
            self.sumRewardsEpisode.append(np.sum(rewardsEpisode))

    def selectAction(self, state, index):
        if index < 1:
            return np.random.choice(self.actionDimension)
        randomNumber = np.random.random()
        if index > 200:
            self.epsilon = 0.999 * self.epsilon
        if randomNumber < self.epsilon:
            return np.random.choice(self.actionDimension)
        else:
            Qvalues = self.mainNetwork.predict(state.reshape(1, 4))
            return np.random.choice(np.where(Qvalues[0, :] == np.max(Qvalues[0, :]))[0])

    def trainNetwork(self):
        if len(self.replayBuffer) > self.batchReplayBufferSize:
            randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
            currentStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))
            nextStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))
            for index, tupleS in enumerate(randomSampleBatch):
                currentStateBatch[index, :] = tupleS[0]
                nextStateBatch[index, :] = tupleS[3]
            QnextStateTargetNetwork = self.targetNetwork.predict(nextStateBatch)
            QcurrentStateMainNetwork = self.mainNetwork.predict(currentStateBatch)
            inputNetwork = currentStateBatch
            outputNetwork = np.zeros(shape=(self.batchReplayBufferSize, 2))
            self.actionsAppend = []
            for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                if terminated:
                    y = reward
                else:
                    y = reward + self.gamma * np.max(QnextStateTargetNetwork[index])
                self.actionsAppend.append(action)
                outputNetwork[index] = QcurrentStateMainNetwork[index]
                outputNetwork[index, action] = y
            self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, verbose=0, epochs=100)
            self.counterUpdateTargetNetwork += 1
            if self.counterUpdateTargetNetwork > (self.updateTargetNetworkPeriod - 1):
                self.targetNetwork.set_weights(self.mainNetwork.get_weights())
                print("Target network updated!")
                print("Counter value {}".format(self.counterUpdateTargetNetwork))
                self.counterUpdateTargetNetwork = 0
