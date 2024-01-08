# RL-Honeypot

## Description
This is an implementation of honeypot system using reinforcement learning, more specifically Deep Q Learning. The system is designed to be able to detect and mitigate APT attacks. The system is implemented using Python 3.7.4 and Tensorflow 2.0.0. Through reinforcement learning, the system is able to learn the optimal policy to mitigate attack coming from attacker by making them believe that they are successfully attacking the system. The system is able to learn the optimal policy by observing the attacker's behavior and the system's state. 

In the original article, we noticed the authors' method of using a Q-learning algorithm to solve the problem of honeypot placement. However, in an enterprise system, such strategy may not be as efficent due to the numbers of workloads being deployed. Therefore, we propose a solution of applying neural networks to the original Q-learning so that the strategy can work at scale. For future improvement, we aim to make our way to Kubernetes sector: deploying the RL-Honeypot model at scale.

You can find the original vietnamese translated article inside Documents.
## TO-DO

- [x] Implement the environment

- [x] Implement the agent

- [x] Implement the training algorithm

- [x] Train the agent

- [x] Observe the result

- [x] Fix logic faults

- [x] Design visualization (WIP)

- [ ] Run the agent on the article's network

- [ ] Dockerize the system and testing on Kubernetes

## Current Progess

- Finished implementing the environment (23/10/2023)

- Huge progress on constructing the simulation network with docker

- Some progress on the training algorithm

- Working on implementing the agent

## Installation

Clone the repository

git clone https://github.com/JackRobert94464/RL-Honeypot

Install the requirements

pip install -r requirements.txt

Run the program

python main.py

## Usage

- Nothing yet
