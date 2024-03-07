# Simple Python Windows Dialogs Program
# TODO: Web Dashboard

import tkinter as tk
import os

root = tk.Tk()
root.title("Demo Dashboard - RL Honeypot Deployment System")


def prepare_data():
    os.startfile("prepare_data.py")

def start_network():
    os.startfile("start_network.py")

def start_nms_retrieval():
    os.startfile("start_nms_retrieval.py")

def start_models():
    os.startfile("start_models.py")

def start_deployment_action():
    os.startfile("start_deployment_server.py")

btn_webgui = tk.Button(root, text="Prepare Data", command=prepare_data)
btn_webgui.pack()

btn_discord = tk.Button(root, text="Start Simulation Network", command=start_network)
btn_discord.pack()

btn_metrics = tk.Button(root, text="Start NMS Retrieval and Analysis", command=start_nms_retrieval)
btn_metrics.pack()

btn_system = tk.Button(root, text="Start models", command=start_models)
btn_system.pack()

btn_system = tk.Button(root, text="Start Deployment Action", command=start_deployment_action)
btn_system.pack()

root.mainloop()
