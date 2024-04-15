import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import subprocess
import os, sys
import pycolour
import asyncio
import threading



def venvCheck():
    if os.environ.get('VIRTUAL_ENV'):
        # The VIRTUAL_ENV environment variable is set
        print('You are in a virtual environment:', pycolour.green + os.environ['VIRTUAL_ENV'] + pycolour.end)
    elif sys.prefix != sys.base_prefix:
        # sys.base_prefix and sys.prefix are different, this is a virtual environment
        # https://stackoverflow.com/questions/1871549/determine-if-python-is-running-inside-virtualenv
        print('You are in a virtual environment:', pycolour.green + sys.prefix + pycolour.end)
    else:
        # Not in a virtual environment
        print(pycolour.red + 'You are not in a virtual environment' + pycolour.end)



root = tk.Tk()
terminal = scrolledtext.ScrolledText(root)


def train_new_model():
    terminal.insert(tk.END, "Training new model...\n")
    if os.name == 'nt':  # If the operating system is Windows
        terminal.insert(tk.END, "Running on Windows...\n")
        terminal.insert(tk.END, "Training model...\n")
        threading.Thread(target=os.system, args=("python .\\Development\\TrainingCode\\driver.py",)).start()
    else:
        terminal.insert(os.system("python ./Development/TrainingCode/driver.py"))
    terminal.insert(tk.END, "Model training completed.\n")

def evaluate_existing_model():
    terminal.insert(tk.END, "Evaluating existing model...\n")

def train_and_evaluate_with_dsp_scoring():
    terminal.insert(tk.END, "Training & evaluating with DSP scoring...\n")

def future_function_template():
    terminal.insert(tk.END, "This is a template for future functions...\n")






# Main function. Will have to be isolated later

def main():
    # Check if user is in virtual environment
    venvCheck()

    # Run websocket client
    print("Running...")

    root.title("Model Operations")

    train_new_model_button = tk.Button(root, text="Train New Model", command=train_new_model)
    train_new_model_button.pack()

    evaluate_existing_model_button = tk.Button(root, text="Evaluate Existing Model", command=evaluate_existing_model)
    evaluate_existing_model_button.pack()

    train_and_evaluate_with_dsp_scoring_button = tk.Button(root, text="Train & Evaluate with DSP Scoring", command=train_and_evaluate_with_dsp_scoring)
    train_and_evaluate_with_dsp_scoring_button.pack()

    future_function_template_button = tk.Button(root, text="Future Function Template", command=future_function_template)
    future_function_template_button.pack()

    # Create a ScrolledText widget
    terminal.pack()

    root.mainloop()

if __name__ == "__main__":

    # flask_webGUI.run_flask_server()  # Run Flask server in the main thread

    # Create a separate thread for your main function
    main_thread = threading.Thread(target=asyncio.run, args=(main(),))
    main_thread.start()
