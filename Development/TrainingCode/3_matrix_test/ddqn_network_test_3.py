from keras.layers import Input, Dense, Concatenate
from keras.models import Model
from keras.optimizers import RMSprop

# import visualkeras

from ddqn_agent_3x_multi_input import DoubleDeepQLearning

import misc
import math
import keras

# observable = trang thai quan sat duoc (default input)
# epss = ma tran EPSS size nxn 
# => tinh trung binh epss cua tung canh => tao ma tran nxn => tai moi vi tri (k, l) cua ma tran => epss(k, l) = trung binh epss cua canh (k, l)
# ntpg = ma tran ntpg size nxn
# => tao ma tran nxn => tai moi vi tri (k, l) cua ma tran => ntpg(k, l) = 1 neu co canh tu k den l, nguoc lai = 0
# Reference:
# https://stackoverflow.com/questions/66786787/pytorch-multiple-branches-of-a-model
# https://stackoverflow.com/questions/33487097/feeding-neural-network-matrix-data-as-input

class Network:
    
    def __init__(self, observable_dimension, epss_dimension, ntpg_dimension, epss_edge_count, ntpg_edge_count, action_dimension):
        self.observable_dimension = observable_dimension
        self.epss_dimension = epss_dimension
        self.ntpg_dimension = ntpg_dimension
        self.epss_edge_count = epss_edge_count
        self.ntpg_edge_count = ntpg_edge_count
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
    
    
    # For low number of nodes, conv network have the same amount of filter as the input shape
    def createConvNetwork_lowperf(self):
        # Define input layers for each type of input data
        observable_input = Input(shape=(self.observable_dimension,))
        epss_input = Input(shape=(self.epss_edge_count, self.epss_edge_count,1))
        ntpg_input = Input(shape=(self.ntpg_edge_count, self.ntpg_edge_count,1))
        
        # Branch 1: Process observable matrix
        observable_branch_1 = Dense(64, activation='relu')(observable_input)
        observable_branch_2 = Dense(64, activation='relu')(observable_branch_1)
        observable_branch_3 = Dense(64, activation='relu')(observable_branch_2)
        
        # Branch 2: Process EPSS matrix
        epss_conv_1 = keras.layers.Conv2D(self.epss_edge_count, kernel_size=2, activation='softmax')(epss_input)
        epss_pool_1 = keras.layers.MaxPooling2D(pool_size=(2, 2))(epss_conv_1)
        epss_conv_2 = keras.layers.Conv2D(self.epss_edge_count, kernel_size=2, activation='softmax')(epss_pool_1)
        epss_pool_2 = keras.layers.MaxPooling2D(pool_size=(2, 2))(epss_conv_2)
        epss_flatten = keras.layers.Flatten()(epss_pool_2)
        
        # Branch 3: Process ntpg penetration graph
        ntpg_conv_1 = keras.layers.Conv2D(self.ntpg_edge_count, kernel_size=2, activation='softmax')(ntpg_input)
        ntpg_pool_1 = keras.layers.MaxPooling2D(pool_size=(2, 2))(ntpg_conv_1)
        ntpg_conv_2 = keras.layers.Conv2D(self.ntpg_edge_count, kernel_size=2, activation='softmax')(ntpg_pool_1)
        ntpg_pool_2 = keras.layers.MaxPooling2D(pool_size=(2, 2))(ntpg_conv_2)
        ntpg_flatten = keras.layers.Flatten()(ntpg_pool_2)
        
        # Concatenate the outputs of all branches
        concatenated = Concatenate()([observable_branch_3, epss_flatten, ntpg_flatten])
        
        # Interpreting the concatenated data
        hidden_1 = Dense(self.epss_dimension, activation='relu')(concatenated)
        hidden_2 = Dense(self.ntpg_dimension, activation='relu')(hidden_1)
        hidden_3 = Dense(64, activation='relu')(hidden_2)
        
        output = Dense(self.action_dimension, activation='softmax')(hidden_3)
        
        # Create model
        model = Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)
        
        # Compile model
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics=['accuracy'])
        
        print("Created network:", model.summary())
        
        
        return model
    
    
    
    # For high number of nodes, conv network have 1/2 the amount of filter as the input shape
    def createConvNetwork_hiperf(self):
        # Define input layers for each type of input data
        observable_input = Input(shape=(self.observable_dimension,1))
        epss_input = Input(shape=(self.epss_edge_count, self.epss_edge_count,1))
        ntpg_input = Input(shape=(self.ntpg_edge_count, self.ntpg_edge_count,1))
        
        
        observable_features = int(math.sqrt(self.observable_dimension))
        
        
        # TODO: Branch 1 will use LSTM for memorizing the observable matrix
        # Branch 1: Process observable matrix (using LSTM)
        observable_branch_lstm = keras.layers.LSTM(observable_features, activation='relu')(observable_input)
        
        # First interpretation model
        observable_branch_1 = Dense(observable_features, activation='relu')(observable_branch_lstm)
        
        # Second interpretation model
        observable_branch_21 = Dense(observable_features, activation='relu')(observable_branch_lstm)
        observable_branch_22 = Dense(observable_features * 2, activation='relu')(observable_branch_21)
        observable_branch_23 = Dense(observable_features, activation='relu')(observable_branch_22)
        
        # Merge the two interpretation models
        observable_concatenated = Concatenate()([observable_branch_1, observable_branch_23])
        
        # output
        observable_output = Dense(observable_features, activation='relu')(observable_concatenated)
        
        
        
        
        
        # Mathematical Params
        # If x is Greatest Common factor of 50 and ntpg_edge_count
        # kernel_size = 2^x
        # pool_size = kernel_size
        # If ntpg_edge_count > 50 => all layers filters = ntpg_edge_count/2^x
        # If 15 < ntpg_edge_count <= 50 => first layer filters = ntpg_edge_count, then filters = ntpg_edge_count/2^x
        # If ntpg_edge_count <= 15 => all layers filters = ntpg_edge_count
        
        '''
        # Branch 2: Process EPSS matrix
        x = math.gcd(50, self.epss_edge_count)
        kernel_size = 2 ** x
        pool_size = kernel_size

        if self.epss_edge_count > 50:
            filters = self.epss_edge_count / (2 ** x)
        elif 15 < self.epss_edge_count <= 50:
            filters = self.epss_edge_count
        else:
            filters = self.epss_edge_count

        epss_input = Input(shape=(self.epss_edge_count, self.epss_edge_count, 1))
        epss_conv = epss_input
        for i in range(x):
            epss_conv = keras.layers.Conv2D(filters=int(filters), kernel_size=kernel_size, activation='softmax')(epss_conv)
            epss_conv = keras.layers.MaxPooling2D(pool_size=(pool_size, pool_size))(epss_conv)
            if self.epss_edge_count > 50:
                filters /= 2
        epss_flatten = keras.layers.Flatten()(epss_conv)

        # Branch 3: Process ntpg penetration graph
        x = math.gcd(50, self.ntpg_edge_count)
        kernel_size = 2 ** x
        pool_size = kernel_size

        if self.ntpg_edge_count > 50:
            filters = self.ntpg_edge_count / (2 ** x)
        elif 15 < self.ntpg_edge_count <= 50:
            filters = self.ntpg_edge_count
        else:
            filters = self.ntpg_edge_count

        ntpg_input = Input(shape=(self.ntpg_edge_count, self.ntpg_edge_count, 1))
        ntpg_conv = ntpg_input
        for i in range(x):
            ntpg_conv = keras.layers.Conv2D(filters=int(filters), kernel_size=kernel_size, activation='softmax')(ntpg_conv)
            ntpg_conv = keras.layers.MaxPooling2D(pool_size=(pool_size, pool_size))(ntpg_conv)
            if self.ntpg_edge_count > 50:
                filters /= 2
        ntpg_flatten = keras.layers.Flatten()(ntpg_conv)
        
        '''
        
        # Branch 2: Process EPSS matrix
        epss_conv_1 = keras.layers.Conv2D(self.epss_edge_count, kernel_size=4, activation='softmax')(epss_input)
        epss_pool_1 = keras.layers.MaxPooling2D(pool_size=(2, 2))(epss_conv_1)
        epss_conv_2 = keras.layers.Conv2D(self.epss_edge_count, kernel_size=4, activation='softmax')(epss_pool_1)
        epss_pool_2 = keras.layers.MaxPooling2D(pool_size=(2, 2))(epss_conv_2)
        epss_flatten = keras.layers.Flatten()(epss_pool_2)
        
        # Branch 3: Process ntpg penetration graph
        ntpg_conv_1 = keras.layers.Conv2D(self.ntpg_edge_count, kernel_size=4, activation='softmax')(ntpg_input)
        ntpg_pool_1 = keras.layers.MaxPooling2D(pool_size=(2, 2))(ntpg_conv_1)
        ntpg_conv_2 = keras.layers.Conv2D(self.ntpg_edge_count, kernel_size=4, activation='softmax')(ntpg_pool_1)
        ntpg_pool_2 = keras.layers.MaxPooling2D(pool_size=(2, 2))(ntpg_conv_2)
        ntpg_flatten = keras.layers.Flatten()(ntpg_pool_2)
        
        
        
        # Concatenate the outputs of all branches
        concatenated = Concatenate()([observable_output, epss_flatten, ntpg_flatten])
        
        # Interpreting the concatenated data
        hidden_1 = Dense(self.epss_dimension, activation='relu')(concatenated)
        hidden_2 = Dense(self.ntpg_dimension, activation='relu')(hidden_1)
        hidden_3 = Dense(self.observable_dimension, activation='relu')(hidden_2)
        
        output = Dense(self.action_dimension, activation='softmax')(hidden_3)
        
        # Create model
        model = Model(inputs=[observable_input, epss_input, ntpg_input], outputs=output)
        
        # Compile model
        model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics=['accuracy'])
        
        print("Created network:", model.summary())
        
        
        return model
        
    
    

# Load the NTPG and HTPG dictionaries
ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_big.csv")
htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_big.csv")

# Load the topology param from TPGs
deception_nodes = misc.get_deception_nodes()
normal_nodes = misc.count_nodes(ntpg)
first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

# calculate the number of possible combinations
total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

# Sample values for the dimensions
observable_dimension = normal_nodes
epss_dimension = normal_nodes*normal_nodes
ntpg_dimension = normal_nodes*normal_nodes
epss_edge_count = normal_nodes
ntpg_edge_count = normal_nodes
action_dimension = total_permutations

# Create the network
network = Network(observable_dimension, epss_dimension, ntpg_dimension, epss_edge_count, ntpg_edge_count, action_dimension)
model = network.createConvNetwork_hiperf()
model.save("trio-net-conv-ltsm.keras")

# visualkeras.layered_view(model, legend=True).show()



