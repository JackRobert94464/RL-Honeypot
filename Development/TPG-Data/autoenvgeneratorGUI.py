import tkinter as tk
from tkinter import messagebox

from autoenvgenerator import generate_tpg

# Create main window
window = tk.Tk()
window.title("TPG Dashboard")

# Create input fields and labels
tk.Label(window, text="CVE Description CSV File:").grid(row=0, column=0, sticky="w")
cve_file_entry = tk.Entry(window)
cve_file_entry.grid(row=0, column=1)

tk.Label(window, text="EPSS CSV File:").grid(row=1, column=0, sticky="w")
epss_file_entry = tk.Entry(window)
epss_file_entry.grid(row=1, column=1)

tk.Label(window, text="Node TPG Output File:").grid(row=2, column=0, sticky="w")
ntpg_file_entry = tk.Entry(window)
ntpg_file_entry.grid(row=2, column=1)

tk.Label(window, text="Host TPG Output File:").grid(row=3, column=0, sticky="w")
htpg_file_entry = tk.Entry(window)
htpg_file_entry.grid(row=3, column=1)

tk.Label(window, text="Min Nodes:").grid(row=4, column=0, sticky="w")
min_nodes_entry = tk.Entry(window)
min_nodes_entry.grid(row=4, column=1)

tk.Label(window, text="Max Nodes:").grid(row=5, column=0, sticky="w")
max_nodes_entry = tk.Entry(window)
max_nodes_entry.grid(row=5, column=1)

tk.Label(window, text="Min CVEs per Connection:").grid(row=6, column=0, sticky="w")
min_cves_entry = tk.Entry(window)
min_cves_entry.grid(row=6, column=1)

tk.Label(window, text="Max CVEs per Connection:").grid(row=7, column=0, sticky="w")
max_cves_entry = tk.Entry(window)
max_cves_entry.grid(row=7, column=1)

# Create generate button
generate_button = tk.Button(window, text="Generate TPG", command=lambda: generate_tpg(
    cve_file_entry.get(), epss_file_entry.get(), ntpg_file_entry.get(), htpg_file_entry.get(),
    int(min_nodes_entry.get()), int(max_nodes_entry.get()), int(min_cves_entry.get()), int(max_cves_entry.get())
))
generate_button.grid(row=8, column=0, columnspan=2, pady=10)


# Start the GUI
window.mainloop()