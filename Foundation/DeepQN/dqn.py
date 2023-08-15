# import the necessary libraries
import numpy as np
import random
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import RMSprop
from collections import deque 
from tensorflow import gather_nd
from tensorflow.keras.losses import mean_squared_error 
 

class DeepQLearning:
     
    ###########################################################################
    #   START - __init__ function
    ###########################################################################
    # INPUTS: 
    # env - Cart Pole environment
    # gamma - discount rate
    # epsilon - parameter for epsilon-greedy approach
    # numberEpisodes - total number of simulation episodes
     
             
    def __init__(self,env,gamma,epsilon,numberEpisodes):
         
         
        self.env=env
        self.gamma=gamma
        self.epsilon=epsilon
        self.numberEpisodes=numberEpisodes
         
        # state dimension
        self.stateDimension=4
        # action dimension
        self.actionDimension=2
        # this is the maximum size of the replay buffer
        self.replayBufferSize=300
        # this is the size of the training batch that is randomly sampled from the replay buffer
        self.batchReplayBufferSize=100
         
        # this sum is used to store the sum of rewards obtained during each training episode
        self.sumRewardsEpisode=[]
         
        # replay buffer
        self.replayBuffer=deque(maxlen=self.replayBufferSize)
         
        # this is the main network
        # create network
        self.mainNetwork=self.createNetwork()
         
        # this list is used in the cost function to select certain entries of the 
        # predicted and true sample matrices in order to form the loss
        self.actionsAppend=[]
     
    ###########################################################################
    #   END - __init__ function
    ###########################################################################
     
    ###########################################################################
    # START - function for defining the loss (cost) function
    # INPUTS: 
    #
    # y_true - matrix of dimension (self.batchReplayBufferSize,2) - this is the target 
    # y_pred - matrix of dimension (self.batchReplayBufferSize,2) - this is predicted by the network
    # 
    # - this function will select certain row entries from y_true and y_pred to form the output 
    # the selection is performed on the basis of the action indices in the list  self.actionsAppend
    # - this function is used in createNetwork(self) to create the network
    #
    # OUTPUT: 
    #    
    # - loss - watch out here, this is a vector of (self.batchReplayBufferSize,1), 
    # with each entry being the squared error between the entries of y_true and y_pred
    # later on, the tensor flow will compute the scalar out of this vector (mean squared error)
    ###########################################################################    
     
    def my_loss_fn(self,y_true, y_pred):
         
        s1,s2=y_true.shape
        #print(s1,s2)
         
        # this matrix defines indices of a set of entries that we want to 
        # extract from y_true and y_pred
        # s2=2
        # s1=self.batchReplayBufferSize
        indices=np.zeros(shape=(s1,s2))
        indices[:,0]=np.arange(s1)
        indices[:,1]=self.actionsAppend
         
        # gather_nd and mean_squared_error are TensorFlow functions
        loss = mean_squared_error(gather_nd(y_true,indices=indices.astype(int)), gather_nd(y_pred,indices=indices.astype(int)))
        #print(loss)
        return loss    
    ###########################################################################
    #   END - of function my_loss_fn
    ###########################################################################
     
     
    ###########################################################################
    #   START - function createNetwork()
    # this function creates the network
    ###########################################################################
     
    # create a neural network
    def createNetwork(self):
        model=Sequential()
        model.add(Dense(128,input_dim=self.stateDimension,activation='relu'))
        model.add(Dense(56,activation='relu'))
        model.add(Dense(self.actionDimension,activation='linear'))
        # compile the network with the custom loss defined in my_loss_fn
        model.compile(optimizer = RMSprop(), loss = self.my_loss_fn, metrics = ['accuracy'])
        return model
    ###########################################################################
    #   END - function createNetwork()
    ###########################################################################
             
    ###########################################################################
    #   START - function trainingEpisodes()
    #   - this function simulates the episodes and calls the training function 
    #   - trainNetwork()
    ###########################################################################

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

    ###########################################################################
    #   END - function trainingEpisodes()
    ###########################################################################
             
        
    ###########################################################################
    #    START - function for selecting an action: epsilon-greedy approach
    ###########################################################################
    # this function selects an action on the basis of the current state 
    # INPUTS: 
    # state - state for which to compute the action
    # index - index of the current episode
    def selectAction(self,state,index):
        import numpy as np
         
        # first index episodes we select completely random actions to have enough exploration
        # change this
        if index<1:
            return np.random.choice(self.actionDimension)   
             
        # Returns a random real number in the half-open interval [0.0, 1.0)
        # this number is used for the epsilon greedy approach
        randomNumber=np.random.random()
         
        # after index episodes, we slowly start to decrease the epsilon parameter
        if index>200:
            self.epsilon=0.999*self.epsilon
         
        # if this condition is satisfied, we are exploring, that is, we select random actions
        if randomNumber < self.epsilon:
            # returns a random action selected from: 0,1,...,actionNumber-1
            return np.random.choice(self.actionDimension)            
         
        # otherwise, we are selecting greedy actions
        else:
            # we return the index where Qvalues[state,:] has the max value
            # that is, since the index denotes an action, we select greedy actions
                        
            Qvalues=self.mainNetwork.predict(state.reshape(1,4))
           
            return np.random.choice(np.where(Qvalues[0,:]==np.max(Qvalues[0,:]))[0])
            # here we need to return the minimum index since it can happen
            # that there are several identical maximal entries, for example 
            # import numpy as np
            # a=[0,1,1,0]
            # np.where(a==np.max(a))
            # this will return [1,2], but we only need a single index
            # that is why we need to have np.random.choice(np.where(a==np.max(a))[0])
            # note that zero has to be added here since np.where() returns a tuple
    ###########################################################################
    #    END - function selecting an action: epsilon-greedy approach
    ###########################################################################
     
    ###########################################################################
    #    START - function trainNetwork() - this function trains the network
    ###########################################################################

    def trainNetwork(self):
        if len(self.replayBuffer) > self.batchReplayBufferSize:
            randomSampleBatch = random.sample(self.replayBuffer, self.batchReplayBufferSize)
            
            currentStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))
            nextStateBatch = np.zeros(shape=(self.batchReplayBufferSize, 4))

            for index, tupleS in enumerate(randomSampleBatch):
                currentStateBatch[index, :] = tupleS[0]
                nextStateBatch[index, :] = tupleS[3]

            QcurrentStateMainNetwork = self.mainNetwork.predict(currentStateBatch)
            QnextStateMainNetwork = self.mainNetwork.predict(nextStateBatch)

            inputNetwork = currentStateBatch
            outputNetwork = np.zeros(shape=(self.batchReplayBufferSize, self.actionDimension))

            for index, (currentState, action, reward, nextState, terminated) in enumerate(randomSampleBatch):
                self.actionsAppend.append(action)  # Append the action to the list
                target = reward

                if not terminated:
                    target += self.gamma * np.max(QnextStateMainNetwork[index])

                outputNetwork[index] = QcurrentStateMainNetwork[index]
                outputNetwork[index, action] = target

            self.mainNetwork.fit(inputNetwork, outputNetwork, batch_size=self.batchReplayBufferSize, verbose=0, epochs=1)

    ###########################################################################
    #    END - function trainNetwork() 
    ########################################################################### 