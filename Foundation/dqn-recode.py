import numpy as np
import gym

# INPUTS: 
# env - Cart Pole environment
# gamma - discount rate
# epsilon - parameter for epsilon-greedy approach
# numberEpisodes - total number of simulation episodes

class DeepQLearning:
    def __init__(self,env,gamma,epsilon,numberEpisodes):
        self.env=env
        self.gamma=gamma
        self.epsilon=epsilon
        self.numberEpisodes=numberEpisodes

        # state dimension - in this case 4 (cart position, cart velocity, pole angle, pole angular velocity)
        # self.stateDim=env.observation_space.shape[0]
        self.stateDim=4
        # action dimension - in this case 2 (left, right)
        # self.actionDim=env.action_space.n
        self.actionDim=2
        # maximum size of replay buffer
        self.replaybufferSize=300
        # batch size for training random sample from replay buffer
        self.batchSize=100

        # number of training episodes it takes to update the target network parameters
        # that is, every updateTargetNetworkPeriod we update the target network parameters
        self.updateTargetNetworkPeriod=10

        # this is the counter for updating the target network 
        # if this counter exceeds (updateTargetNetworkPeriod-1) we update the network 
        # parameters and reset the counter to zero, this process is repeated until the end of the training process
        self.updateTargetNetworkCounter=0

        # store the sum of rewards in every episode
        self.sumRewardsEpisode=[]

        # create the replay buffer
        self.replayBuffer=deque(maxlen=self.replayBufferSize)

        # create the main network
        self.mainNetwork=self.createNetwork()

        # create the target network
        self.targetNetwork=self.createNetwork()

        # copy the initial main network parameters to the target network
        self.targetNetwork.set_weights(self.mainNetwork.get_weights())

        # this list is used in the cost function to select certain entries of the 
        # predicted and true sample matrices in order to form the loss
        self.actionsAppend=[]

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

    def customLoss(self,y_true,y_pred):
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
    
    # END - function for defining the loss (cost) function
    
    # Create the network
    # This function creates the neural network for deep Q-learning
    def createNetwork(self):
        # Sequential mean that we gonna have a sequence of layers (layer upon layer)
        model=Sequential()
        # we gonna have three layers
        # first layer - input layer. This layer accept the 4 state dimensions as input
        model.add(Dense(128,input_dim=self.stateDim,activation='relu'))
        # second layer - hidden layer
        model.add(Dense(56,activation='relu'))
        # third layer - output layer. This layer has two neurons, one for each action
        model.add(Dense(self.actionDim,activation='linear'))

        # compile the network with the custom loss function defined above
        model.compile(optimizer = RMSprop(), loss = self.customLoss, metrics = ['accuracy'])

        return model
    
    # This function selects the action based on the epsilon-greedy approach
    
    
    