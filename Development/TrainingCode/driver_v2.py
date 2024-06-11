###########################################################################
#    DRIVER CODE
###########################################################################   

from tf_agents.environments import tf_py_environment
# import the environment
from NetworkHoneypotEnv_base_fnrfprtest_v3 import NetworkHoneypotEnv
# import evaluation functions
import evaluation_headless_v2
# import miscellaneous funtions
import misc
import os

# def __init__(self, gamma, epsilon, numberEpisodes, normal_nodes, total_permutations, fnr, fpr):

# Defining parameters
gamma = 0.99  # Discount factor for future rewards
# Epsilon parameter for the epsilon-greedy approach
epsilon = 0.1

# For SARSA
max_steps_sarsa = 100
alpha_sarsa = 0.1


# FNR and FPR values as lists (todo...)
# fnr = [float(input("Enter FNR value: "))]
# fpr = [float(input("Enter FPR value: "))]

# FNR and FPR values as single input
fnr = float(input("Enter FNR value: "))
fpr = float(input("Enter FPR value: "))

# Attack rate for attacker (To determine whether to take the node or not)
attack_rate = float(input("Enter the attack rate for the attacker: "))

# Load the TPG data
if os.name == 'nt':  # If the operating system is Windows
        ntpg = misc.create_dictionary_ntpg(".\\Development\\TPG-Data\\ntpg_40.csv")
        htpg = misc.create_dictionary_htpg(".\\Development\\TPG-Data\\htpg_40.csv")
else:  # For other operating systems like Linux
        ntpg = misc.create_dictionary_ntpg("./Development/TPG-Data/ntpg_40.csv")
        htpg = misc.create_dictionary_htpg("./Development/TPG-Data/htpg_40.csv")

normal_nodes = misc.count_nodes(ntpg)
print("Normal nodes:", normal_nodes)
# Load the TPG data


def SingleDecoyTraining(deception_nodes, numberEpisodes, model_name, model_type):
    '''
    Short training for testing out the dsp graphing function

    For debugging purpose, uncomment this
    '''

    deception_nodes = deception_nodes # Change this to the number of deception nodes you want to test

    first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

    # Create the environment
    env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg, fnr, fpr, attack_rate)

    numberEpisodes = numberEpisodes

    # calculate the number of possible combinations
    total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

    # Initialize empty dictionaries to store the training time and DSP values
    training_time_dict = {}
    dsp_dict = {}
    
    # create an object
    if(model_type == 1):
        # DQN
        agent=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
    if(model_type == 2):
        # SARSA
        agent=SarsaLearning(env, epsilon, numberEpisodes, max_steps_sarsa, alpha_sarsa, gamma, total_permutations, fnr, fpr)
    if(model_type == 3):
        # PPO
        agent = PPOAgent(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
    
    
    # run the learning process
    for ep in range(numberEpisodes):
        agent.updateTrainingEpisode(ep)
        # print("Episode: ", ep)
        agent.trainingSingleEpisodes()
        
        # Every 2000 5000 10000 step, we perform evaluation        
        currentStep = agent.getStepCount()
        print("Current Step: ", currentStep)
        
        if currentStep in [250, 500, 750, 1000, 2000, 5000, 10000, 20000, 30000, 50000]:
            
            # Initialize an evalutaion instance
            evaluator = evaluation_headless_v2.Evaluation()
            
            # Save models to folder
            agent.saveModel()
            model_path = agent.retrieveModelPath()
            
            # Collect the training time dict from training code
            training_time_dict.update(agent.retrieveTraintimeDict())
            
            # Evaluate the model
            evaluator.evaluate(agent, model_path, model_type)
            
            # Collect the DSP dict from evaluation code
            dsp_dict.update(evaluator.retrieveDSPdict(currentStep))
            
            # Save the training time dict and DSP dict to a text file
            output_folder = "output_dsp_trainingtime/"
            if os.name == 'nt':
                output_folder = ".\\output_dsp_trainingtime\\"
            else:
                output_folder = "./output_dsp_trainingtime/"
            
            # Create the output folder if it doesn't exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                
            with open(output_folder + f"result_fnr{fnr}_fpr{fpr}_model_{model_name}_{currentStep}_honeypotAmount_{deception_nodes}.txt", "w") as file:
                file.write(f"Training Time Dict: {training_time_dict}\n")
                file.write(f"DSP Dict: {dsp_dict}\n")
                
            print("Training Time and DSP saved to file.")
            print(f"File name: result_fnr{fnr}_fpr{fpr}_model_{model_name}.txt")

    #  summarize the model
    if(model_type == 1):
        agent.mainNetwork.summary()
        agent.saveModel()
        
    if(model_type == 2):
        agent.mainNetwork.model.summary()
        agent.saveModel()

def MultiDecoyTraining(numberEpisodes, model_name, model_type):
    '''
    For loop for long training
    The training will start from giving the agent only 1 deception node and increase the number of deception nodes by 1 in each iteration.
    The training will stop when the number of deception nodes is equal to half of the number of normal nodes.
    '''
    for i in range(normal_nodes//2 + 1, 0, -1):
        deception_nodes = i
        
        first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)

        # Create the environment
        env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg, fnr, fpr, attack_rate)

        numberEpisodes = numberEpisodes

        # calculate the number of possible combinations
        total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)

        # Initialize empty dictionaries to store the training time and DSP values
        training_time_dict = {}
        dsp_dict = {}
        
        # create an object
        if(model_type == 1):
            # DQN
            agent=DoubleDeepQLearning(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
        if(model_type == 2):
            # SARSA
            agent=SarsaLearning(env, epsilon, numberEpisodes, max_steps_sarsa, alpha_sarsa, gamma, total_permutations, fnr, fpr)
        if(model_type == 3):
            # PPO
            agent = PPOAgent(env,gamma,epsilon,numberEpisodes,normal_nodes,total_permutations, fnr, fpr)
        
        
        # run the learning process
        for ep in range(numberEpisodes):
            agent.updateTrainingEpisode(ep)
            # print("Episode: ", ep)
            agent.trainingSingleEpisodes()
            
            # Every 2000 5000 10000 step, we perform evaluation        
            currentStep = agent.getStepCount()
            print("Current Step: ", currentStep)
            
            if currentStep in [250, 500, 750, 1000, 2000, 5000, 10000, 20000, 30000, 50000]:
                
                # Initialize an evalutaion instance
                evaluator = evaluation_headless_v2.Evaluation()
                
                # Save models to folder
                agent.saveModel()
                model_path = agent.retrieveModelPath()
                
                # Collect the training time dict from training code
                training_time_dict.update(agent.retrieveTraintimeDict())
                
                # Evaluate the model
                evaluator.evaluate(agent, model_path, model_type)
                
                # Collect the DSP dict from evaluation code
                dsp_dict.update(evaluator.retrieveDSPdict(currentStep))
                
                # Save the training time dict and DSP dict to a text file
                output_folder = "output_dsp_trainingtime/"
                if os.name == 'nt':
                    output_folder = ".\\output_dsp_trainingtime\\"
                else:
                    output_folder = "./output_dsp_trainingtime/"
                
                # Create the output folder if it doesn't exist
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                    
                with open(output_folder + f"result_fnr{fnr}_fpr{fpr}_model_{model_name}_{currentStep}_honeypotAmount_{deception_nodes}.txt", "w") as file:
                    file.write(f"Training Time Dict: {training_time_dict}\n")
                    file.write(f"DSP Dict: {dsp_dict}\n")
                    
                print("Training Time and DSP saved to file.")
                print(f"File name: result_fnr{fnr}_fpr{fpr}_model_{model_name}.txt")

        #  summarize the model
        if(model_type == 1):
            agent.mainNetwork.summary()
            agent.saveModel()
            
        if(model_type == 2):
            agent.mainNetwork.model.summary()
            agent.saveModel()
        
        

# https://blog.finxter.com/python-how-to-import-modules-from-another-folder/ ----> Method 3: Dot Notation with __init__.py
'''
You can also do the following trick—creating a new package.
# file_2.py
from application.app.folder.file_1 import func_name
However, make sure to include an empty __init__.py file in the directory.
'''

if __name__ == "__main__":
    
    model_type = 1 # Default to DQN
    
    # Ask the user which model they want to use for training
    print("Select the model for training:")
    print("1: Standard Model")
    print("2: Three Input Conv1D Model")
    print("3: FNR/FPR Rate Model (Deprecated)")
    print("4: SARSA Model")
    print("5: A2C Model")
    model_choice = input("Enter the number of the model you want to train: ")
    model_name = None

    # Based on the user's choice, import the appropriate environment and agent
    if model_choice == '1':
        model_name = "Base"
        model_type = 1
        from NetworkHoneypotEnv_base_fnrfprtest_v3 import NetworkHoneypotEnv
        from ddqn_agent_headless_v2 import DoubleDeepQLearning
        print("Imported the environment and agent successfully.")
        
    elif model_choice == '2':
        
        model_type = 1
        from NetworkHoneypotEnv_base_fnrfprtest_v3 import NetworkHoneypotEnv
        
        print("Which input type would you like to use?")
        print("1: Single Input v1 - quickly process observation state using one dense layer")
        print("2: Single Input v2 - reduce to 1 conv1D and apply batch normailzation - 29/05/2024")
        print("3: Multi Input - a LTSM for observation state will be used")
        input_choice = input("Enter the number of the input type you want to use: ")
        
        if input_choice == '1':
            model_name = "3xConv1D_v1"
            from MatrixTest3.ddqn_agent_3x_simple_state_fnrfpr import DoubleDeepQLearning
        elif input_choice == '2':
            model_name = "3xConv1D_v2"
            from MatrixTest3.ddqn_agent_3x_simple_state_fnrfpr_v2 import DoubleDeepQLearning
        elif input_choice == '3':
            model_name = "3xConv1D_LTSM"
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
        
    elif model_choice == '4':
        model_name = "SARSA"
        from NetworkHoneypotEnv_base_fnrfprtest_v3 import NetworkHoneypotEnv
        from sarsa.sarsa_agent_3input import SarsaLearning
        model_type = 2
        print("Imported the environment and agent successfully.")

    elif model_choice == '5':
        model_name = "A2C"
        model_type = 3  # Set a new model type for PPO
        from NetworkHoneypotEnv_base_fnrfprtest_v3 import NetworkHoneypotEnv
        from PPO.a2c_3input import PPOAgent
        print("Imported the environment and A2C agent successfully.")
        
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
        SingleDecoyTraining(deception_nodes, numberEpisodes, model_name, model_type)
    elif training_choice == '2':
        print("Enter the number of episodes you want to train for each number of decoy nodes:")
        print("BEWARE: Try to keep this low as the training will take a long time if there's many counts of decoy nodes.")
        numberEpisodes = int(input("Enter the number of episodes: "))
        MultiDecoyTraining(numberEpisodes, model_name, model_type)
    else:
        print("Invalid selection. Exiting.")
        exit()
    # SingleDecoyTraining()
    # MultiDecoyTraining()
