from keras.layers import Input, Dense, Concatenate
from keras.models import Model
from keras.optimizers import RMSprop

from ddqn_agent import DoubleDeepQLearning

# observable = trang thai quan sat duoc (default input)
# epss = ma tran EPSS size nxn 
# => tinh trung binh epss cua tung canh => tao ma tran nxn => tai moi vi tri (k, l) cua ma tran => epss(k, l) = trung binh epss cua canh (k, l)
# ntpg = ma tran ntpg size nxn
# => tao ma tran nxn => tai moi vi tri (k, l) cua ma tran => ntpg(k, l) = 1 neu co canh tu k den l, nguoc lai = 0

class Network:
    def __init__(self, observable_dimension, epss_dimension, ntpg_dimension, action_dimension):
        self.observable_dimension = observable_dimension
        self.epss_dimension = epss_dimension
        self.ntpg_dimension = ntpg_dimension
        self.action_dimension = action_dimension

    def createNetwork(self):
        # Define input layers for each type of input data
        observable_input = Input(shape=(self.observable_dimension,))
        epss_input = Input(shape=(self.epss_dimension,))
        ntpg_input = Input(shape=(self.ntpg_dimension,))
        
        # Branch 1: Process observable matrix
        observable_branch = Dense(64, activation='relu')(observable_input)
        
        # Branch 2: Process EPSS matrix
        epss_branch = Dense(64, activation='relu')(epss_input)
        
        # Branch 3: Process ntpg penetration graph
        ntpg_branch = Dense(64, activation='relu')(ntpg_input)
        
        # Concatenate the outputs of all branches
        concatenated = Concatenate()([observable_branch, epss_branch, ntpg_branch])
        
        # Intermediate dense layer
        concatenated = Dense(64, activation='relu')(concatenated)
        
        # Output layer
        output = Dense(self.action_dimension, activation='linear')(concatenated)
        
        # Create model
        model = Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)
        
        # Compile model
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics=['accuracy'])
        
        print("Created network:", model.summary())
        
        return model


# Sample values for the dimensions
observable_dimension = 10
epss_dimension = 100
ntpg_dimension = 10
action_dimension = 100

# Create the network
network = Network(observable_dimension, epss_dimension, ntpg_dimension, action_dimension)
model = network.createNetwork()