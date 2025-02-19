

# 17/12/2023 - Tam giai quyet xong phan ham lost, dang thuc hien evaluation model

# CONTRUCTION ZONE

'''
Legacy: a simple network with 2 hidden layers of 100 units each and ReLU activation

def createNetwork(self):
    # create a neural network with two hidden layers of 100 units each and ReLU activation (must fix!)
    # the final layer is a dense layer with k!/(k-m)! units, one for each possible deployment combination
    model = Sequential()

    model.add(InputLayer(input_shape=self.stateDimension))

    
    model.add(Dense(64, activation='relu'))
    # model.add(Dense(128, activation='relu'))
    model.add(Dense(64, activation='relu'))
    
    # Thay doi lop dau ra thanh softmax de giai quyet so luong dau ra khong xac dinh
    model.add(Dense(self.actionDimension, activation='softmax'))
    
    # use mean squared error as the loss function
    # original used a custom loss one, but for this case im not sure
    
    model.compile(loss=DoubleDeepQLearning.ddqn_loss_fn, optimizer=RMSprop(), metrics = ['accuracy'])
    print("Created network:", model.summary())
    # os.system("pause")
    return model
'''


'''
Legacy
action = np.zeros((self.env.M, self.env.K))
for i in range(self.env.M):
    action[i, np.random.randint(0, self.env.K)] = 1
    # print("Deploying honeypot number", i, "in normal nodes:", action)
action = action.astype(np.int32)
# print("ACTION MATRIX exploit:", action)
return action
'''

'''
ntpg = {'192.168.1.3': [('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0),('192.168.2.3', 0,0.9756)],
                      '192.168.2.3': [('192.168.1.3', 0,0.0009),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.2.4': [('192.168.2.3', 0,0.9756),('192.168.4.3', 0,0.9756),('192.168.3.3', 0.9746,0)],
                      '192.168.3.3': [],
                      '192.168.3.4': [('192.168.3.5', 0,0.0009)],
                      '192.168.3.5': [('192.168.4.3', 0,0.9756)],
                      '192.168.4.3': [('192.168.3.4', 0,0.9756),('192.168.3.5', 0,0.0009),('192.168.3.3', 0.9746,0)],} 

htpg = {'192.168.1.3': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),
                              ('Apache', 'CVE-2014-6271', 0.9756, ('192.168.2.3', 'Root')),
                              ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],
                      '192.168.2.3': [('PHP Server', 'CVE-2020-35132', 0.0009, ('192.168.1.3', 'Root')),
                                      ('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),
                                      ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],
                      '192.168.2.4': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.2.3', 'Root')),
                                      ('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),
                                      ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],
                      '192.168.3.3': [],
                      '192.168.3.4': [('PHP Server','CVE-2020-35132','0.0009', ('192.168.3.5', 'Root')),],
                      '192.168.3.5': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.4.3', 'Root')),],
                      '192.168.4.3': [('Apache', 'CVE-2014-6271', 0.9756, ('192.168.3.4', 'Root')),
                                      ('PHP Server','CVE-2020-35132','0.0009', ('192.168.3.5', 'Root')),
                                      ('PHP Server', 'CVE-2016-10033', 0.9746, ('192.168.3.3', 'User')),],}
'''

# Add some code to generate the NTPG and HTPG based on some logic or data
# For example, you can use a loop to iterate over the nodes and add edges randomly
# Or you can use some existing library or tool to generate the graphs
# Or you can hard-code the graphs based on some predefined structure
# Here I will just use a simple loop and random numbers as an example

# 29/10/2023 - Fixed example is provided as follow, i will include image of the sample graph
# self._ntpg = {'192.168.0.2': [ ('192.168.0.3', 0.8,0.6),('192.168.0.3', 0.8,0.6)], 
#             '192.168.0.3': [ ('192.168.0.5', 0.5,0.1)], 
#             '192.168.0.4': [('192.168.0.5', 0.8,0.2),('192.168.0.6', 0.4,0.2),('192.168.0.7', 0.3,0.1),], 
#             '192.168.0.5': [('192.168.0.8', 0.2,0.1),('192.168.0.7', 0.6,0.3)],
#             '192.168.0.6': [],
#             '192.168.0.7': [('192.168.0.8', 0.2,0.9)],
#             '192.168.0.8': [],}

# self._htpg = {'192.168.0.2': [('NetBT', 'CVE-2017-0161', 0.6, ('192.168.0.4', 'User')),
#                            ('Win32k', 'CVE-2018-8120', 0.04, ('192.168.0.4', 'Root')),
#                            ('VBScript', 'CVE-2018-8174', 0.5, ('192.168.0.4', 'Root')),
#                            ('Apache', 'CVE-2017-9798', 0.8, ('192.168.0.3', 'User')),
#                            ('Apache', 'CVE-2014-0226', 0.6, ('192.168.0.3', 'Root')),], 
#            '192.168.0.3': [('Apache', 'CVE-2017-9798', 0.5, ('192.168.0.5', 'User')),
#                            ('Apache', 'CVE-2014-0226', 0.1, ('192.168.0.5', 'Root')),], 
#            '192.168.0.4': [('NetBT', 'CVE-2017-0161', 0.8, ('192.168.0.5', 'User')),
#                            ('Win32k', 'CVE-2018-8120', 0.02, ('192.168.0.5', 'Root')),
#                            ('VBScript', 'CVE-2018-8174', 0.2, ('192.168.0.5', 'Root')),
#                            ('OJVM', 'CVE-2016-5555', 0.4, ('192.168.0.6', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.2, ('192.168.0.6', 'Root')),
#                            ('HFS', 'CVE-2014-6287', 0.3, ('192.168.0.7', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.7', 'Root')),], 
#            '192.168.0.5': [('HFS', 'CVE-2014-6287', 0.6, ('192.168.0.7', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.3, ('192.168.0.7', 'Root')),
#                            ('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root')),],
#            '192.168.0.6': [],
#            '192.168.0.7': [('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root'))],
#            '192.168.0.8': [],
#}


# Regenerate the NTPG and HTPG based on some logic or data
# Here I will use the same code as in the __init__ function (12/11/2023 - reset to fixed example)
# self._ntpg = {'192.168.0.2': [ ('192.168.0.3', 0.8,0.6),('192.168.0.3', 0.8,0.6)], 
#               '192.168.0.3': [ ('192.168.0.5', 0.5,0.1)], 
#               '192.168.0.4': [('192.168.0.5', 0.8,0.2),('192.168.0.6', 0.4,0.2),('192.168.0.7', 0.3,0.1),], 
#               '192.168.0.5': [('192.168.0.8', 0.2,0.1),('192.168.0.7', 0.6,0.3)],
#               '192.168.0.6': [],
#               '192.168.0.7': [('192.168.0.8', 0.2,0.9)],
#               '192.168.0.8': [],}


# self._htpg = {'192.168.0.2': [('NetBT', 'CVE-2017-0161', 0.6, ('192.168.0.4', 'User')),
#                            ('Win32k', 'CVE-2018-8120', 0.04, ('192.168.0.4', 'Root')),
#                            ('VBScript', 'CVE-2018-8174', 0.5, ('192.168.0.4', 'Root')),
#                            ('Apache', 'CVE-2017-9798', 0.8, ('192.168.0.3', 'User')),
#                            ('Apache', 'CVE-2014-0226', 0.6, ('192.168.0.3', 'Root')),], 
#            '192.168.0.3': [('Apache', 'CVE-2017-9798', 0.5, ('192.168.0.5', 'User')),
#                            ('Apache', 'CVE-2014-0226', 0.1, ('192.168.0.5', 'Root')),], 
#            '192.168.0.4': [('NetBT', 'CVE-2017-0161', 0.8, ('192.168.0.5', 'User')),
#                            ('Win32k', 'CVE-2018-8120', 0.02, ('192.168.0.5', 'Root')),
#                            ('VBScript', 'CVE-2018-8174', 0.2, ('192.168.0.5', 'Root')),
#                            ('OJVM', 'CVE-2016-5555', 0.4, ('192.168.0.6', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.2, ('192.168.0.6', 'Root')),
#                            ('HFS', 'CVE-2014-6287', 0.3, ('192.168.0.7', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.7', 'Root')),], 
#            '192.168.0.5': [('HFS', 'CVE-2014-6287', 0.6, ('192.168.0.7', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.3, ('192.168.0.7', 'Root')),
#                            ('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root')),],
#            '192.168.0.6': [],
#            '192.168.0.7': [('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
#                            ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root'))],
#            '192.168.0.8': [],
#}


# Attacker themselves move with each "step" in the environment too
# Does this code represent that? or just a static mapping?
# 14/01/2023 Remove this function (logic fault), attacker will move with each step in the environment
# 18/02/2024 Attacker simulate code is use for training only - for production we will need to demo in some way

def __attacker_move_step(self):
    """Simulates one step of the attacker's move based on the NTPG and HTPG.
    Updates the state vector with the new attacked node.
    """
    # Get the current node information
    current_node = self._current_attacker_node
    current_node_index = int(current_node.split('.')[-1]) - 2

    # Check if the current node has possible routes
    print("NTPG:", self._ntpg)
    print("current_node:", current_node)
    print("NTPG OF CURRENT NODE:" , self._ntpg.get(current_node)[0]) if self._ntpg.get(current_node) else print("there is no NTPG for this node, something is wrong")
    # os.system("pause")
    if self._ntpg.get(current_node):
        # Iterate over the possible routes from the current node
        for route in self._ntpg.get(current_node):
            next_node = route[0]
            attack_chance = route[1]  # Use the chance to attack the node
            if np.random.random() <= attack_chance:
                self._state[current_node_index] = 1
                print("Attacked node:", current_node)
                break  # Attack successful, exit the loop

        # Move to the next node based on HTPG probability
        next_node = np.random.choice([route[0] for route in self._ntpg.get(current_node)])  # Fix: Specify a 1-dimensional array
        self._current_attacker_node = next_node
        print("Next node to attempt attack:", next_node)

    else:
        print("No more possible routes, exit the loop. State vector after the attack:", self._state)

    # Update the NIFR list based on the action matrix
    self.__update_nifr_nodes(self.nifr_nodes)
    print("NIFR list after attack:", self.nifr_nodes)
        
        
        
'''
Legacy code from the original code (action matrix K*M)

def index_to_action(self, index):
    # Initialize the action matrix with zeros
    action_matrix = np.zeros((self.env.M, self.env.K), dtype=np.int32)
    # print("action matrix to be indexed:", action_matrix)

    # Convert the index to the corresponding row and column for the action matrix
    for i in range(self.env.M):
        # Calculate the index for the current row
        row_index = index // (self.env.K ** (self.env.M - 1 - i))
        index -= row_index * (self.env.K ** (self.env.M - 1 - i))

        # Set the value in the action matrix
        action_matrix[i, row_index] = 1

    # print("index to action matrix:", action_matrix)
    return action_matrix

        # return action_matrix
'''


'''
        legacy
        # save the model, this is important, since it takes long time to train the model 
        # and we will need model in another file to visualize the trained model performance
        if os.name == 'nt':  # If the operating system is Windows
            LearningQDeep.mainNetwork.save(f".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_weighted_attacker_1to5_decoy_win_ver{numberEpisodes}_fnrfpr_{fnr}{fpr}.keras")
        else:  # For other operating systems like Linux
            LearningQDeep.mainNetwork.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_weighted_attacker_1to5_decoy_linux_ver{numberEpisodes}_fnrfpr_{fnr}{fpr}.keras")
'''


'''
# get the obtained rewards in every episode
        LearningQDeep.sumRewardsEpisode

        print(rewards)

        # DSP graphing function

        print("Total steps: ", LearningQDeep.getGlobalStepCount())
        print("Total DSP: ", LearningQDeep.getGlobalDSPCount())

        # Visualize the Defense Success Probability (DSP) of our method
        ddqn_dsp_visualizer.ddqn_dsp_visual(LearningQDeep.getGlobalStepCount(), LearningQDeep.getGlobalDSPCount())

        # Visualize the training time taken of our method
        ddqn_trainingtime_visualizer.ddqn_dsp_visual(LearningQDeep.getGlobalStepCount(), LearningQDeep.getGlobalTimeTaken())
'''


'''
import ddqn_dsp_visualizer
    import ddqn_trainingtime_visualizer


    print("Total steps: ", LearningQDeep.getGlobalStepCount())
    print("Total DSP: ", LearningQDeep.getGlobalDSPCount())
    print("Total Time: ", LearningQDeep.getGlobalTimeTaken())



    # Visualize the Defense Success Probability (DSP) of our method
    # Save the global step count and global DSP count to a text file
    with open(f"result_fnr{fnr}_fpr{fpr}.txt", "w") as file:
            file.write(f"Global Step Count: {LearningQDeep.getGlobalStepCount()}\n")
            file.write(f"Global DSP Count: {LearningQDeep.getGlobalDSPCount()}\n")
    ddqn_dsp_visualizer.ddqn_dsp_visual(LearningQDeep.getGlobalStepCount(), LearningQDeep.getGlobalDSPCount())



    # Visualize the training time taken of our method
    ddqn_trainingtime_visualizer.ddqn_dsp_visual(LearningQDeep.getGlobalStepCount(), LearningQDeep.getGlobalTimeTaken())


    # get the obtained rewards in every episode
    LearningQDeep.sumRewardsEpisode

    print(rewards)
'''

    
'''
06/04 xem + chinh lai ham nay luon
legacy code
def __is_action_valid(self, action):
    # Check if the action is a valid matrix of size m*k with values 0 or 1
    # Return True if the action is valid, False otherwise
    if action is None:
        return False
    
    # Check if the action has the correct shape
    if action.shape != (self.M, self.K):
        return False
    
    # Check if the action has the correct type
    if action.dtype != np.int32:
        return False
    
    # Check if the action has the correct values
    if not np.all(np.isin(action, [0, 1])):
        return False
    
    # Check if each row has only one 1
    if not np.all(np.sum(action, axis=1) == 1):
        return False
    
    # If all checks pass, return True
    return True
'''

# self._action_spec = array_spec.BoundedArraySpec(
#     shape=(M, K), dtype=np.int32, minimum=0, maximum=1, name='action')
# print("Action spec:", self._action_spec)


'''
New action suggestion (06/04 ngay mai nho doc lai)
[ 0 0 1 0 1 0 0 ]
1 la cho se dat honeypot
self._action_spec = array_spec.BoundedArraySpec(
    shape=(1, K), dtype=np.int32, minimum=0, maximum=1, name='action')
print("Action spec:", self._action_spec)
'''

'''
06/04 xem + chinh lai ham nay luon
Legacy code
# Updates the NIFR list based on the action matrix.
def __update_nifr_nodes(self, nifr_nodes):
    print("self._matrix to update nifr nodes:", self._matrix)
    for row in self._matrix:
        if any(row):
            print("row.argmax():", row.argmax())
            nifr_nodes.append(row.argmax())
            if len(nifr_nodes) > self.M:
                nifr_nodes.pop(0)
            print("NIFR list after update:", nifr_nodes)
'''


def TestTrain():
    '''
    Short training for testing out the dsp graphing function
    
    This func is use for the main which is now currently developing the modular trainingEpisode function (13/05/2024)
    
    For debugging purpose, uncomment this
    '''
    
    # Initialize empty dictionaries to store the training time and DSP values
    training_time_dict = {}
    dsp_dict = {}

    deception_nodes = 2 # Change this to the number of deception nodes you want to test

    first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

    # Create the environment
    env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

    # Create the environment. Since it was built using PyEnvironment, we need to wrap it in a TFEnvironment to use with TF-Agents
    tf_env = tf_py_environment.TFPyEnvironment(env)


    timestep = tf_env.reset()
    rewards = []
    numberEpisodes = 20000

    # calculate the number of possible combinations
    total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

    # create an object
    agent=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
    
    # Training the Agent with a fixed number of episodes
    for ep in range(numberEpisodes):
        agent.updateTrainingEpisode(ep)
        # print("Episode: ", ep)
        agent.trainingSingleEpisodes()
        
        # Every 2000 5000 10000 step, we perform evaluation        
        currentStep = agent.getStepCount()
        
        if currentStep in [2000, 5000, 10000, 20000, 30000]:
            
            # Initialize an evalutaion instance
            evaluator = evaluation_v2.Evaluation()
            
            # Save models to folder
            agent.saveModel()
            model_path = agent.retrieveModelPath()
            
            # Collect the training time dict from training code
            training_time_dict.update(agent.retrieveTraintimeDict())
            
            # Evaluate the model
            evaluator.evaluate(agent, model_path)
            
            # Collect the DSP dict from evaluation code
            dsp_dict.update(evaluator.retrieveDSPdict())
            
            # Save the training time dict and DSP dict to a text file
            with open(f"result_fnr{fnr}_fpr{fpr}.txt", "w") as file:
                file.write(f"Training Time Dict: {training_time_dict}\n")
                file.write(f"DSP Dict: {dsp_dict}\n")
    
    

    import ddqn_dsp_visualizer
    import ddqn_trainingtime_visualizer


    print("Total steps: ", agent.getGlobalStepCount())
    print("Total DSP: ", agent.getGlobalDSPCount())
    print("Total Time: ", agent.getGlobalTimeTaken())



    # Visualize the Defense Success Probability (DSP) of our method
    # Save the global step count and global DSP count to a text file
    with open(f"result_fnr{fnr}_fpr{fpr}.txt", "w") as file:
            file.write(f"Global Step Count: {agent.getGlobalStepCount()}\n")
            file.write(f"Global DSP Count: {agent.getGlobalDSPCount()}\n")
    ddqn_dsp_visualizer.ddqn_dsp_visual(agent.getGlobalStepCount(), agent.getGlobalDSPCount())



    # Visualize the training time taken of our method
    ddqn_trainingtime_visualizer.ddqn_dsp_visual(agent.getGlobalStepCount(), agent.getGlobalTimeTaken())


    # get the obtained rewards in every episode
    agent.sumRewardsEpisode

    print(rewards)

    #  summarize the model
    agent.mainNetwork.summary()
    # save the model, this is important, since it takes long time to train the model 
    # and we will need model in another file to visualize the trained model performance
    if os.name == 'nt':  # If the operating system is Windows
            agent.mainNetwork.save(f".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_weighted_attacker_1to5_decoy_win_ver{numberEpisodes}_fnrfpr_{fnr}{fpr}.keras")
    else:  # For other operating systems like Linux
            agent.mainNetwork.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_weighted_attacker_1to5_decoy_linux_ver{numberEpisodes}_fnrfpr_{fnr}{fpr}.keras")
        