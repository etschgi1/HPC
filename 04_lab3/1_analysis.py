import numpy as np
import matplotlib.pyplot as plt
import os
from uncertainties import ufloat
FIG_PATH = "../lab_report/fig/lab3"
os.chdir(os.path.dirname(__file__))

# Step 2

Ns = np.array([50, 500, 2000, 4000, 5000])


global_mem = np.array([0.073445, 0.118105, 0.089352, 0.026648, 0.042794, 0.043776, 0.046394, 0.054036, 0.032975, 0.048523])
shared_mem = np.array([0.044324, 0.056177, 0.043138, 0.026455, 0.047783, 0.029442, 0.085995, 0.037380, 0.027113, 0.027415])

global_mem_mean = global_mem.mean() 
shared_mem_mean = shared_mem.mean()

global_mem_u = ufloat(global_mem_mean, np.var(global_mem))
shared_mem_mean_u = ufloat(shared_mem_mean, np.var(shared_mem))


# Scatter plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=18)

plt.figure(figsize=(15, 4))
plt.scatter(1000* global_mem,np.zeros(len(global_mem)), label="Global Memory", color="blue", alpha=0.7)
plt.scatter(1000* shared_mem, np.zeros(len(global_mem)),label="Shared Memory", color="orange", alpha=0.7)

# Mittelwerte hervorheben
plt.scatter(1000*global_mem_mean , 0, color="blue", edgecolor="black", s=100, label="Mean Global Memory")
plt.scatter(1000*shared_mem_mean,0, color="orange", edgecolor="black", s=100, label="Mean Shared Memory")

plt.ylim(-0.01, 0.01)
plt.yticks([])
plt.xticks(np.arange(20,max(global_mem)+10,10))
plt.xlabel("t / ms")
plt.legend(bbox_to_anchor=(0.38, 1))
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(os.path.join(FIG_PATH,"step1.png"))
print(f"Global mem: {global_mem_u} ")
print(f"Shared mem: {shared_mem_mean_u}")
print(f"Time saving shared mem {(global_mem_u - shared_mem_mean_u) /global_mem_u}")