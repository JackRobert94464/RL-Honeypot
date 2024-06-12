from flask import Flask, render_template, request, redirect, url_for
import os
from NetworkHoneypotEnv_base_fnrfprtest_v3 import NetworkHoneypotEnv
import evaluation_headless_v2
import misc

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train():
    gamma = 0.99
    epsilon = 0.1
    max_steps_sarsa = 100
    alpha_sarsa = 0.1

    fnr = float(request.form['fnr'])
    fpr = float(request.form['fpr'])
    attack_rate = float(request.form['attack_rate'])
    tpg_dir = request.form['tpg_dir']
    ntpg_name = request.form['ntpg_name']
    htpg_name = request.form['htpg_name']
    
    ntpg_path = os.path.join(tpg_dir, ntpg_name)
    htpg_path = os.path.join(tpg_dir, htpg_name)
    
    ntpg = misc.create_dictionary_ntpg(ntpg_path)
    htpg = misc.create_dictionary_htpg(htpg_path)
    normal_nodes = misc.count_nodes(ntpg)
    
    model_choice = request.form['model_choice']
    training_choice = request.form['training_choice']
    number_episodes = int(request.form['number_episodes'])
    deception_nodes = int(request.form['deception_nodes'])
    
    model_type, model_name, agent_class = get_model_details(model_choice)
    
    if training_choice == '1':
        SingleDecoyTraining(deception_nodes, number_episodes, model_name, model_type, agent_class, ntpg, htpg, normal_nodes, fnr, fpr, attack_rate)
    else:
        MultiDecoyTraining(number_episodes, model_name, model_type, agent_class, ntpg, htpg, normal_nodes, fnr, fpr, attack_rate)
    
    return redirect(url_for('result'))

@app.route('/result')
def result():
    return render_template('result.html')

def get_model_details(model_choice):
    if model_choice == '1':
        return 1, "Base", "ddqn_agent_headless_v2.DoubleDeepQLearning"
    elif model_choice == '2':
        input_choice = request.form['input_choice']
        if input_choice == '1':
            return 1, "3xConv1D_v1", "MatrixTest3.ddqn_agent_3x_simple_state_fnrfpr.DoubleDeepQLearning"
        elif input_choice == '2':
            return 1, "3xConv1D_v2", "MatrixTest3.ddqn_agent_3x_simple_state_fnrfpr_v2.DoubleDeepQLearning"
        elif input_choice == '3':
            return 1, "3xConv1D_LTSM", "MatrixTest3.ddqn_agent_3x_multi_input_fnrfpr.DoubleDeepQLearning"
    elif model_choice == '4':
        return 2, "SARSA", "sarsa.sarsa_agent_3input.SarsaLearning"
    elif model_choice == '5':
        return 3, "A2C", "PPO.a2c_3input.PPOAgent"
    else:
        return None, None, None

if __name__ == "__main__":
    app.run(debug=True)
