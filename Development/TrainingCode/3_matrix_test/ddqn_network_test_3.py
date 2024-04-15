from keras.layers import Input, Dense, Concatenate
from keras.models import Model
from keras.optimizers import RMSprop

# import visualkeras

from ddqn_agent_3x_multi_input import DoubleDeepQLearning

import misc
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
    def __init__(self, observable_dimension, epss_dimension, ntpg_dimension, action_dimension):
        self.observable_dimension = observable_dimension
        self.epss_dimension = epss_dimension
        self.ntpg_dimension = ntpg_dimension
        self.action_dimension = action_dimension
        
        
    ###########################################################################
    # START - function for defining the loss (cost) function
    # FIX THIS ASAP
    # Status: FIX THIS ASAP
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
    
    @keras.saving.register_keras_serializable()
    def ddqn_loss_fn(y_true, y_pred):
        # print("LOSS FUNCTION - Y_TRUE:", y_true)
        s1, s2 = y_true.shape
        # print("LOSS FUNCTION - S1 AND S2:", s1, s2)
        # print("LOSS FUNCTION - ACTIONS APPEND:", actionsAppend)

        # count the amount of actions in actionsAppend
        countact = len(actionsAppend)
        # print("LOSS FUNCTION - COUNTACT:", countact)


        # Calculate the number of actions
        num_actions = len(actionsAppend[0])

        # Reshape indices to have shape (batch_size * num_actions, 2)
        indices = np.zeros(shape=(s1 * num_actions, 2))
        indices[:, 0] = np.repeat(np.arange(s1), num_actions)
        indices[:, 1] = np.tile(np.arange(num_actions), s1)


        loss = keras.losses.mean_squared_error(keras.backend.gather(y_true, indices=indices.astype(int)),
                                            keras.backend.gather(y_pred, indices=indices.astype(int)))
        return loss

    ###########################################################################
    #   END - of function my_loss_fn
    ###########################################################################    


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
    
    

'''

# Load the NTPG and HTPG dictionaries
ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_eval.csv")
htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_eval.csv")

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
action_dimension = total_permutations

# Create the network
network = Network(observable_dimension, epss_dimension, ntpg_dimension, action_dimension)
model = network.createNetwork()
model.save("trio-net.keras")

# visualkeras.layered_view(model, legend=True).show()
'''


