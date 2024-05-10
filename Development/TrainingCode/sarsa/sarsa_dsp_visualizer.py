'''
This file is used to visualize the Defense Success Probability (DSP) of our method.
Assuming your total steps are stored in a list named total_steps and defense success probability 
(DSP) in a list named dsp, you can proceed with plotting.
'''

import matplotlib.pyplot as plt

# Function to visualize the Defense Success Probability (DSP)
def sarsa_dsp_visual(total_steps, dsp):
    plt.plot(total_steps, dsp)  # Plot DSP vs total steps

    # Add labels and title
    plt.xlabel("Training steps")
    plt.ylabel("Defense Success Probability (DSP)")
    plt.title("Defense Success Probability of Our Method")

    # Set grid
    plt.grid(True)

    # Show the plot
    plt.show()
    
    # Save the plot
    plt.savefig('ddqn_dsp_visual.png')
