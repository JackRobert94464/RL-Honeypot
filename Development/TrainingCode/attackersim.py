'''
Attacker class for the attacker simulation.
Here we define the attacker class and its methods to simulate the attacker's movement and attack.
First method - Training:
- Random 1 so -> so sanh voi tat ca cac duong, neu lon hon se lua duong dau tien duoc chon
- Luu y tim ham random voi xac suat co san
Second method - Testing:
'''

import numpy as np
import random
import misc

# Random 1 so -> so sanh voi tat ca cac duong, neu lon hon se lua duong dau tien duoc chon
# https://pynative.com/python-weighted-random-choices-with-probability/
# https://stackoverflow.com/questions/55847638/how-to-generate-a-random-number-with-a-known-probability

# Luu y tim ham random voi xac suat co san

# train with no gradient

# ghi nhan state vao csv roi moi xuat hinh -> nhanh hon xuat hinh tai tung state

class Attacker:
    """Class for the attacker simulation.
    """
    def __init__(self, ntpg, htpg):
        """Initializes the attacker object with the NTPG, HTPG, state vector, and NIFR list.
        """
        self._ntpg = ntpg
        self._htpg = htpg
        self._current_attacker_node = list(self._ntpg.keys())[0]


    def attacker_move_step(self):
        """Simulates one step of the attacker's move based on the NTPG and HTPG.
           Updates the state vector with the new attacked node.
        """

        # Get the current node information
        current_node = self._current_attacker_node
        current_node_index = list(self._ntpg.keys()).index(current_node)
        print("Current node index:", current_node_index)

        # Check if the current node has possible routes
        print("NTPG:", self._ntpg)
        print("current_node:", current_node)
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
            next_node = random.choices(
                population=[route[0] for route in self._ntpg.get(current_node)],
                weights=[route[1] for route in self._ntpg.get(current_node)],
                k=1
            )[0]
            self._current_attacker_node = next_node
            print("Next node to attempt attack:", next_node)

        else:
            print("No more possible routes, exit the loop. State vector after the attack:", self._state)




    def __truong_attacker_move(self):
        # Simulates the attacker's move based on Truong's fixed flow.

        print("Work In Progress - WIP")

        # Fix the current_node to the very first node

    def __NMS_alert_based_attacker_movement(self):
        # Receive alert from NMS and update the observation space based on the alert.
        # API code to receive alert from NMS and digest it into the observation space and reward.

        # Fix the current_node to the very first node
        print("Work In Progress - WIP")

# Load the NTPG and HTPG dictionaries
ntpg = misc.create_dictionary_ntpg("ntpg_eval.csv")
htpg = misc.create_dictionary_htpg("htpg_eval.csv")

att = Attacker(ntpg, htpg)
att.attacker_move_step()