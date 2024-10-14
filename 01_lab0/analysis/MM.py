import matplotlib.pyplot as plt
import re
import numpy as np

import os
import re
RES_PATH = "../res/"
PLOT_PATH = "../../lab_report/fig/lab0/"
cur_path = os.path.dirname(__file__)
os.chdir(cur_path)
# Extract times from files

# latex matplotlib
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

times = {}
cpu_counts = ["01", "02", "04", "08", "16", "24", "32", "48", "64"]

# Regular expression to match the time in the format: took: <time> s
time_pattern = re.compile(r"took: ([\d.]+) s")

# Process each file and extract time
for cpu_count in cpu_counts:
    filename = f"MM{cpu_count}.txt"
    filepath = os.path.join(RES_PATH, filename)
    try:
        with open(filepath, "r") as file:
            for line in file:
                match = time_pattern.search(line)
                if match:
                    times[cpu_count] = float(match.group(1))
                    break
    except FileNotFoundError:
        print(f"File {filename} not found.")

# Sort the extracted data by CPU count (numeric sorting of keys)
sorted_times = [(int(k), v) for k, v in times.items()]
sorted_times.sort()

# Extract x (CPU counts) and y (times) for plotting
x_vals = [item[0] for item in sorted_times]
y_vals = [item[1] for item in sorted_times]
speedup = y_vals[0]/np.array(y_vals)
print(f"X values: {x_vals}")
print(f"Y values: {y_vals}")
print(f"Speedup: {y_vals[0]/np.array(y_vals)}")

# Plot the data
plt.figure(figsize=(10, 6))

fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel('Core Count')
ax1.set_ylabel('Time (seconds)', color=color)
ax1.plot(x_vals, y_vals, marker="o", linestyle="-", color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True)  # Enable grid on both x and y for ax1

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'
ax2.set_ylabel('Speedup', color=color)  # we already handled the x-label with ax1
ax2.plot(x_vals, speedup, marker="o", linestyle="-", color=color)
ax2.tick_params(axis='y', labelcolor=color)
ax2.grid(True)  # Enable grid on both x and y for ax2
ax1.plot(48, 1.919, marker="x", linestyle="", color="black")
ax2.plot(48, y_vals[0]/1.919, marker="x", linestyle="", color="black")
plt.title("Execution Time vs Core Count")
plt.xticks(x_vals)
plt.savefig(f"{PLOT_PATH}MM_plot.png")