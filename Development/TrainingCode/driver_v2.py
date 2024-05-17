###########################################################################
#    DRIVER CODE
###########################################################################   

from tf_agents.environments import tf_py_environment
# import the environment
from NetworkHoneypotEnv_base import NetworkHoneypotEnv
# import evaluation functions
import evaluation_v2
# import miscellaneous funtions
import misc
import os

# def __init__(self, gamma, epsilon, numberEpisodes, normal_nodes, total_permutations, fnr, fpr):

# Defining parameters
gamma = 0.99  # Discount factor for future rewards
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

# FNR and FPR values as lists (todo...)
# fnr = [float(input("Enter FNR value: "))]
# fpr = [float(input("Enter FPR value: "))]

# FNR and FPR values as single input
fnr = float(input("Enter FNR value: "))
fpr = float(input("Enter FPR value: "))

# Load the TPG data
if os.name == 'nt':  # If the operating system is Windows
        ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_big.csv")
        htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_big.csv")
else:  # For other operating systems like Linux
        ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg.csv")
        htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg.csv")

normal_nodes = misc.count_nodes(ntpg)
print("Normal nodes:", normal_nodes)
# Load the TPG data


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
    LearningQDeep=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
    
    # Training the Agent with a fixed number of episodes
    for ep in range(numberEpisodes):
        LearningQDeep.updateTrainingEpisode(ep)
        # print("Episode: ", ep)
        LearningQDeep.trainingSingleEpisodes()
        
        # Every 2000 5000 10000 step, we perform evaluation        
        currentStep = LearningQDeep.getStepCount()
        
        if currentStep in [2000, 5000, 10000, 20000, 30000]:
            
            # Initialize an evalutaion instance
            evaluator = evaluation_v2.Evaluation()
            
            # Save models to folder
            LearningQDeep.saveModel()
            model_path = LearningQDeep.retrieveModelPath()
            
            # Collect the training time dict from training code
            training_time_dict.update(LearningQDeep.retrieveTraintimeDict())
            
            # Evaluate the model
            evaluator.evaluate(LearningQDeep, model_path)
            
            # Collect the DSP dict from evaluation code
            dsp_dict.update(evaluator.retrieveDSPdict())
            
            # Save the training time dict and DSP dict to a text file
            with open(f"result_fnr{fnr}_fpr{fpr}.txt", "w") as file:
                file.write(f"Training Time Dict: {training_time_dict}\n")
                file.write(f"DSP Dict: {dsp_dict}\n")
    
    

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

    #  summarize the model
    LearningQDeep.mainNetwork.summary()
    # save the model, this is important, since it takes long time to train the model 
    # and we will need model in another file to visualize the trained model performance
    if os.name == 'nt':  # If the operating system is Windows
            LearningQDeep.mainNetwork.save(f".\\TrainedModel\\weighted_random_attacker\\RL_Honeypot_weighted_attacker_1to5_decoy_win_ver{numberEpisodes}_fnrfpr_{fnr}{fpr}.keras")
    else:  # For other operating systems like Linux
            LearningQDeep.mainNetwork.save(f"./TrainedModel/weighted_random_attacker/RL_Honeypot_weighted_attacker_1to5_decoy_linux_ver{numberEpisodes}_fnrfpr_{fnr}{fpr}.keras")
        

def SingleDecoyTraining(deception_nodes, numberEpisodes, model_name):
    '''
    Short training for testing out the dsp graphing function

    For debugging purpose, uncomment this
    '''

    deception_nodes = deception_nodes # Change this to the number of deception nodes you want to test

    first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

    # Create the environment
    env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

    numberEpisodes = numberEpisodes

    # calculate the number of possible combinations
    total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

    # Initialize empty dictionaries to store the training time and DSP values
    training_time_dict = {}
    dsp_dict = {}
    
    # create an object
    LearningQDeep=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
    
    # run the learning process
    for ep in range(numberEpisodes):
        LearningQDeep.updateTrainingEpisode(ep)
        # print("Episode: ", ep)
        LearningQDeep.trainingSingleEpisodes()
        
        # Every 2000 5000 10000 step, we perform evaluation        
        currentStep = LearningQDeep.getStepCount()
        
        if currentStep in [2000, 5000, 10000, 20000, 30000]:
            
            # Initialize an evalutaion instance
            evaluator = evaluation_v2.Evaluation()
            
            # Save models to folder
            LearningQDeep.saveModel()
            model_path = LearningQDeep.retrieveModelPath()
            
            # Collect the training time dict from training code
            training_time_dict.update(LearningQDeep.retrieveTraintimeDict())
            
            # Evaluate the model
            evaluator.evaluate(model_path)
            
            # Collect the DSP dict from evaluation code
            dsp_dict.update(evaluator.retrieveDSPdict())
            
            # Save the training time dict and DSP dict to a text file
            with open(f"result_fnr{fnr}_fpr{fpr}_model_{model_name}.txt", "w") as file:
                file.write(f"Training Time Dict: {training_time_dict}\n")
                file.write(f"DSP Dict: {dsp_dict}\n")
                
            print("Training Time and DSP saved to file.")
            print(f"File name: result_fnr{fnr}_fpr{fpr}_model_{model_name}.txt")

    #  summarize the model
    LearningQDeep.mainNetwork.summary()


def MultiDecoyTraining(numberEpisodes, model_name):
    '''
    For loop for long training
    The training will start from giving the agent only 1 deception node and increase the number of deception nodes by 1 in each iteration.
    The training will stop when the number of deception nodes is equal to half of the number of normal nodes.
    '''
    for i in range(normal_nodes//2 + 1, 0, -1):
        deception_nodes = i
        
        first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

        # Create the environment
        env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)

        numberEpisodes = numberEpisodes

        # calculate the number of possible combinations
        total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

        # Initialize empty dictionaries to store the training time and DSP values
        training_time_dict = {}
        dsp_dict = {}

        # create an object
        LearningQDeep=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
        
        # run the learning process
        for ep in range(numberEpisodes):
            LearningQDeep.updateTrainingEpisode(ep)
            # print("Episode: ", ep)
            LearningQDeep.trainingSingleEpisodes()
            
            # Every 2000 5000 10000 step, we perform evaluation        
            currentStep = LearningQDeep.getStepCount()
            
            if currentStep in [2000, 5000, 10000, 20000, 30000]:
                
                # Initialize an evalutaion instance
                evaluator = evaluation_v2.Evaluation()
                
                # Save models to folder
                LearningQDeep.saveModel()
                model_path = LearningQDeep.retrieveModelPath()
                
                # Collect the training time dict from training code
                training_time_dict.update(LearningQDeep.retrieveTraintimeDict())
                
                # Evaluate the model
                evaluator.evaluate(model_path)
                
                # Collect the DSP dict from evaluation code
                dsp_dict.update(evaluator.retrieveDSPdict())
                
                # Save the training time dict and DSP dict to a text file
                with open(f"result_fnr{fnr}_fpr{fpr}_model_{model_name}.txt", "w") as file:
                    file.write(f"Training Time Dict: {training_time_dict}\n")
                    file.write(f"DSP Dict: {dsp_dict}\n")
                
                print("Training Time and DSP saved to file.")
                print(f"File name: result_fnr{fnr}_fpr{fpr}_model_{model_name}.txt")
            
        #  summarize the model
        LearningQDeep.mainNetwork.summary()
        
        

# https://blog.finxter.com/python-how-to-import-modules-from-another-folder/ ----> Method 3: Dot Notation with __init__.py
'''
You can also do the following trick—creating a new package.
# file_2.py
from application.app.folder.file_1 import func_name
However, make sure to include an empty __init__.py file in the directory.
'''

if __name__ == "__main__":
    # Ask the user which model they want to use for training
    print("Select the model for training:")
    print("1: Standard Model")
    print("2: Three Input Conv1D Model")
    print("3: FNR/FPR Rate Model (Deprecated)")
    model_choice = input("Enter the number of the model you want to train: ")
    model_name = None

    # Based on the user's choice, import the appropriate environment and agent
    if model_choice == '1':
        model_name = "Base"
        from NetworkHoneypotEnv_base import NetworkHoneypotEnv
        from ddqn_agent_headless_v2 import DoubleDeepQLearning
        print("Imported the environment and agent successfully.")
        
    elif model_choice == '2':
        model_name = "3xConv1D"
        from MatrixTest3.test_3_NetworkHoneypotEnv import NetworkHoneypotEnv
        
        print("Which input type would you like to use?")
        print("1: Single Input - quickly process observation state using one dense layer")
        print("2: Multi Input - a LTSM for observation state will be used")
        input_choice = input("Enter the number of the input type you want to use: ")
        
        if input_choice == '1':
            from MatrixTest3.ddqn_agent_3x_simple_state_fnrfpr import DoubleDeepQLearning
        elif input_choice == '2':
            from MatrixTest3.ddqn_agent_3x_multi_input_fnrfpr import DoubleDeepQLearning
        
        print("Imported the environment and agent successfully.")
        
    elif model_choice == '3':
        model_name = "FNRFPR"
        print("FNR/FPR Rate Model is deprecated. Please select another model.")
        print("15-05-2024 Both base and 3-input have been updated with fnr/fpr rates. Please select one of those.")
        exit()
        
        # from fnr_fpr_test import fnrfpr_calc
        # from fnr_fpr_test.NetworkHoneypotEnv_fnrfpr import NetworkHoneypotEnv
        # from fnr_fpr_test.ddqn_agent_headless_fnrfpr import DoubleDeepQLearning
        # print("Imported the environment and agent successfully.")
        
    else:
        print("Invalid selection. Exiting.")
        exit()

    # Proceed with the training using the selected model
    print("Which training method would you like to use?")
    print("1: Single Deception Node Training - Fixed number of Decoy Nodes")
    print("2: Multiple Deception Node Training - Decremental number of Decoy Nodes, Longer Training")
    training_choice = input("Enter the number of the training method you want to use: ")
    
    # Based on the user's choice, call the appropriate training function
    if training_choice == '1':
        print("Enter the number of episodes you want to train for:")
        numberEpisodes = int(input("Enter the number of episodes: "))
        print("And how many decoy nodes will be available?")
        deception_nodes = int(input("Enter the number of deception nodes: "))
        SingleDecoyTraining(deception_nodes, numberEpisodes, model_name)
    elif training_choice == '2':
        print("Enter the number of episodes you want to train for each number of decoy nodes:")
        print("BEWARE: Try to keep this low as the training will take a long time if there's many counts of decoy nodes.")
        numberEpisodes = int(input("Enter the number of episodes: "))
        MultiDecoyTraining(numberEpisodes, model_name)
    else:
        print("Invalid selection. Exiting.")
        exit()
    # SingleDecoyTraining()
    # MultiDecoyTraining()