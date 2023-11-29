import random
import numpy as np

def trainNetwork(self):
    if len(self.replayBuffer) < self.replayBufferSize:
        return

    randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
    inputNetwork = np.zeros((self.batchReplayBufferSize, 4))
    outputNetwork = np.zeros((self.batchReplayBufferSize, 2))
    self.actionsAppend = []
    self.actionsAppend = []


    for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
        # parameter for the current state-action pair
        alpha = self.computeAlpha(currentState, action)

        QcurrentStateMainNetwork = self.mainNetwork.predict(currentState.reshape(1, 4))
        QnextStateMainNetwork = self.mainNetwork.predict(nextState.reshape(1, 4))

        # if the next state is the terminal state
        if terminated:
            y = reward
        # if the next state is not the terminal state
        else:
            y = reward + self.gamma * np.max(QnextStateMainNetwork[0])

        # this is necessary for defining the cost function
        self.actionsAppend.append(action)  # this actually does not matter since we do not use all the entries in the cost function
        outputNetwork[index] = QcurrentStateMainNetwork[0]  # this is what matters
        outputNetwork[index, action] = y  # scale the output by the alpha parameter
        outputNetwork[index] = outputNetwork[index] * alpha

        # assign the current state to the input
        inputNetwork[index] = currentState

    self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, epochs=1, verbose=0)
    self.counterUpdateTargetNetwork = self.counterUpdateTargetNetwork + 1

    if self.counterUpdateTargetNetwork == self.updateTargetNetworkPeriod:
        self.targetNetwork.set_weights(self.mainNetwork.get_weights())
        self.counterUpdateTargetNetwork = 0
        print("Target network updated!")
