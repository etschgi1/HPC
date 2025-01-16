import numpy as np
import matplotlib.pyplot as plt
import os
from uncertainties import ufloat
FIG_PATH = "../lab_report/fig/lab3"
os.chdir(os.path.dirname(__file__))

# Step 3 for N = 5000 and 32 threads per block 

cpu_speed = np.array([1.476385, 1.527617, 1.468183, 1.480447, 1.479499])
gpu_speed_no_mem = np.array([0.006212, 0.048133, 0.010623, 0.018042, 0.031192])
gpu_speed_w_mem = np.array([0.063645, 0.035523, 0.063917, 0.032279, 0.111496])

speedup_no_mem = cpu_speed / gpu_speed_no_mem
speedup_w_mem = cpu_speed / gpu_speed_w_mem

speedup_no_mem_mean = cpu_speed.mean() / gpu_speed_no_mem.mean()
speedup_w_mem_mean = cpu_speed.mean() / gpu_speed_w_mem.mean()

speedup_no_mem_mean_u = ufloat(speedup_no_mem_mean, np.var(cpu_speed/gpu_speed_no_mem))
speedup_w_mem_mean_u = ufloat(speedup_w_mem_mean, np.var(cpu_speed/gpu_speed_w_mem))

# Scatter plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=18)

plt.figure(figsize=(15, 4))
plt.scatter( speedup_no_mem,np.zeros(len(speedup_no_mem)), label="Speedup w/o Memory", color="blue", alpha=0.7)
plt.scatter( speedup_w_mem, np.zeros(len(speedup_no_mem)),label="Speedup with Memory", color="orange", alpha=0.7)

# Mittelwerte hervorheben
plt.scatter(speedup_no_mem_mean , 0, color="blue", edgecolor="black", s=100, label="Mean w/o Memory")
plt.scatter(speedup_w_mem_mean,0, color="orange", edgecolor="black", s=100, label="Mean with Memory")

plt.ylim(-0.01, 0.01)
plt.yticks([])
plt.xticks(np.arange(0,max(speedup_no_mem)+25, 25))
plt.xlabel("Speedup")
plt.legend(bbox_to_anchor=(0.38, 1))
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(os.path.join(FIG_PATH,"step3.png"))
print(f"Mean speedup (no mem): {speedup_no_mem_mean_u} ")
print(f"Mean speedup (w mem): {speedup_w_mem_mean_u}")
