

# 17/12/2023 - Tam giai quyet xong phan ham lost, dang thuc hien evaluation model

# CONTRUCTION ZONE



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