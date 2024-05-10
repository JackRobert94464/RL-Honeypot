'''
This file is used to visualize the training time taken of our method.
Assuming your total steps are stored in a list named total_steps and training times taken at various points
in a list named timetaken, you can proceed with plotting.
'''

import matplotlib.pyplot as plt

# Function to visualize the Defense Success Probability (DSP)
def sarsa_dsp_visual(total_steps, timetaken):
    plt.plot(total_steps, timetaken)  # Plot DSP vs total steps

    # Add labels and title
    plt.xlabel("Training steps of the DDQN model")
    plt.ylabel("Time(s)")
    plt.title("Training time needed for our method")

    # Set grid
    plt.grid(True)

    # Show the plot
    plt.show()
    
    # Save the plot
    plt.savefig('ddqn_trainingtime_visual.png')
