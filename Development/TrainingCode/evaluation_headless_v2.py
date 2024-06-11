import pandas as pd
import tensorflow as tf
import numpy as np
import misc
import os
from visualizer import visualize_steps
import ddqn_dsp_visualizer

# Import loss function
from ddqn_loss_fn import ddqn_loss_fn

# Import environment
from NetworkHoneypotEnv_base import NetworkHoneypotEnv


import matplotlib.pyplot as plt

class Evaluation:
    def __init__(self):
        self.eval_episodes = 50
        self.eval_rewards = []
        self.eval_steps = []
        self.visualization_data = pd.DataFrame(columns=['episode', 'steps', 'step_entities'])
        self.step_globalcounter = []
        self.dsp_globalcounter = []
        self.step_counter = 0
        self.episodeWon = 0

    def load_trained_model(self, model_path):
        trained_model = tf.keras.models.load_model(model_path, custom_objects={'loss': ddqn_loss_fn})
        return trained_model

    def load_tpg_data(self):
        ##########################
        
        ########################
        
        # MUST FIX MUST FIX
        
        #######################
        if os.name == 'nt':
            ntpg_path = ".\\Development\\TPG-Data\\ntpg_40.csv"
            htpg_path = ".\\Development\\TPG-Data\\htpg_40.csv"
        else:
            ntpg_path = "./Development/TPG-Data/ntpg_40.csv"
            htpg_path = "./Development/TPG-Data/htpg_40.csv"
        ntpg = misc.create_dictionary_ntpg(ntpg_path)
        htpg = misc.create_dictionary_htpg(htpg_path)
        return ntpg, htpg

    def create_environment(self, ntpg, htpg):
        deception_nodes = 2 # misc.get_deception_nodes()
        normal_nodes = misc.count_nodes(ntpg)
        first_parameter = misc.calculate_first_parameter(deception_nodes, normal_nodes)
        total_permutations = misc.calculate_permutation(normal_nodes, deception_nodes)
        eval_env = NetworkHoneypotEnv(first_parameter, deception_nodes, normal_nodes, ntpg, htpg)
        return eval_env

    def evaluate_episodes(self, eval_env, agent, trained_model):
        for episode in range(self.eval_episodes):
            episode_reward = 0
            episode_steps = 0
            # print("------------------------------------------------------------------------------------------------------------------------")
            # print("Evaluating episode number: ", episode)
            # print("------------------------------------------------------------------------------------------------------------------------")
            steps_entity = []
            eval_time_step = eval_env.reset()
            while not eval_time_step.is_last():
                action = agent.selectActionEval(eval_time_step.observation, episode, trained_model)
                # print("ACTION SELECTED:", action)
                if action is None:
                    # print("No action selected. Skipping this step.")
                    continue
                eval_time_step = eval_env.step(action)
                # print("EVAL TIME STEP:", eval_time_step)
                steps_entity.append({'attacker_node': eval_env._current_attacker_node, 
                                     'nifr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nifr_nodes], 
                                     'nicr_nodes': [list(eval_env._ntpg.keys())[node_index-1] for node_index in eval_env.nicr_nodes],})
                episode_reward += eval_time_step.reward
                # print("EPISODE REWARD:", episode_reward)
                episode_steps += 1
                # print("EPISODE STEPS:", episode_steps)
                self.visualization_data = self.visualization_data._append({'episode': episode, 'steps': episode_steps, 'step_entities': steps_entity}, ignore_index=True)
                steps_entity = []
            if episode_reward > 0:
                self.episodeWon += 1
                print("Episode Won Counter: ", self.episodeWon)
                os.system('pause')
            self.step_counter += episode_steps
            
            self.step_globalcounter.append(self.step_counter)


            
            dsp = self.episodeWon / self.eval_episodes

            self.dsp_globalcounter.append(dsp)
            
            # print(f"DSP Global Counter after episode {episode}: ", self.dsp_globalcounter)
            
            # Write dsp_globalcounter to a temporary file
            with open('dsp_globalcounter.tmp', 'w') as file:
                for item in self.dsp_globalcounter:
                    file.write(str(item) + '\n')
                    # print(f"Writing DSP Global Counter: {item}")
            
            self.eval_rewards.append(episode_reward)
            self.eval_steps.append(episode_steps)

    def visualize_dsp(self):
        ddqn_dsp_visualizer.ddqn_dsp_visual(self.step_globalcounter, self.dsp_globalcounter)

    def save_visualization_data(self):
        self.visualization_data.to_csv('visualization_data.csv', index=False)

    def visualize_steps(self, ntpg):
        your_nodes_list = list(ntpg.keys())
        your_edges_list = [(node, edge[0]) for node in ntpg for edge in ntpg[node]]
        visualize_steps(your_nodes_list, your_edges_list, 'visualization_data.csv')

    def calculate_evaluation_results(self):
        avg_eval_reward = np.mean(self.eval_rewards)
        avg_eval_steps = np.mean(self.eval_steps)
        num_successful_defense = sum(reward > 0 for reward in self.eval_rewards)
        dsp = (num_successful_defense / self.eval_episodes)
        max_len = max(len(self.eval_rewards), len(self.eval_steps), self.eval_episodes)
        rewards = self.eval_rewards + [0] * (max_len - len(self.eval_rewards))
        steps = self.eval_steps + [0] * (max_len - len(self.eval_steps))
        episodes = list(range(1, self.eval_episodes + 1)) + [0] * (max_len - self.eval_episodes)
        results = {
            "Episode": episodes,
            "Reward": rewards,
            "Steps": steps,
        }
        df = pd.DataFrame(results)
        return df, avg_eval_reward, avg_eval_steps, dsp


    def plot_rewards_and_steps(self):
        plt.figure(figsize=(30, 30))
        plt.subplot(1, 2, 1)
        plt.plot(self.eval_rewards)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title("Rewards per Episode")
        plt.subplot(1, 2, 2)
        plt.plot(self.eval_steps)
        plt.xlabel("Episode")
        plt.ylabel("Steps")
        plt.title("Steps per Episode")
        plt.tight_layout()
        plt.show()
        
    # Read dsp_globalcounter from the temporary file in retrieveDSPdict
    def retrieveDSPdict(self, currentStep):
        dsp_globalcounter = []
        with open('dsp_globalcounter.tmp', 'r') as file:
            for line in file:
                dsp_globalcounter.append(float(line.strip()))
                
        # print(f"Retrieved DSP Global Counter: {dsp_globalcounter}")
        final_dsp = sum(dsp_globalcounter) / len(dsp_globalcounter)
        
        # Delete the temporary file
        os.remove('dsp_globalcounter.tmp')
        
        return {currentStep: final_dsp}

    def evaluate(self, agent, model_path, model_type):
        evaluation = Evaluation()
        evalAgent = agent
        if model_type == 1 or model_type == 2 or model_type == 3:
            trained_model = evaluation.load_trained_model(model_path)
            # print("Trained model:", trained_model.summary())
        ntpg, htpg = evaluation.load_tpg_data()
        eval_env = evaluation.create_environment(ntpg, htpg)
        if model_type == 1 or model_type == 2:
            evaluation.evaluate_episodes(eval_env, evalAgent, trained_model)
        elif model_type == 3:
            evaluation.evaluate_episodes(eval_env, evalAgent, trained_model)
        
        # TODO: MAKE THE TPG DATA LOAD CUSTOM TOO
        ntpg, htpg = evaluation.load_tpg_data()
        eval_env = evaluation.create_environment(ntpg, htpg)
        evaluation.evaluate_episodes(eval_env, evalAgent, trained_model)
        # evaluation.visualize_dsp()
        evaluation.save_visualization_data()
        # evaluation.visualize_steps(ntpg)
        df, avg_eval_reward, avg_eval_steps, dsp = evaluation.calculate_evaluation_results()
        # evaluation.plot_rewards_and_steps()
        # print(df)
        # print("Evaluation Results:")
        # print("Number of Episodes:", evaluation.eval_episodes)
        # print("Total Reward:", np.sum(evaluation.eval_rewards))
        # print("Reward per Episode:", evaluation.eval_rewards)
        # print("Total Steps:", np.sum(evaluation.eval_steps))
        # print("Steps per Episode:", evaluation.eval_steps)
        # print("Average Reward per Episode:", avg_eval_reward)
        # print("Average Steps per Episode:", avg_eval_steps)
        # print("Defense Success Probability (DSP):", dsp)
        
        

        

        
        
        

