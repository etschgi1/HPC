import numpy as np
import matplotlib.pyplot as plt
import os
from uncertainties.unumpy import uarray
FIG_PATH = "../lab_report/fig/lab3"
os.chdir(os.path.dirname(__file__))

# Step 2

Ns = np.array([50, 500, 2000, 4000, 5000])
t_per_block_32 = np.array([[0.000906, 0.001006, 0.006965, 0.047339, 0.040060],
                           [0.000765, 0.001075, 0.006573, 0.021165, 0.058950],
                           [0.000860, 0.000657, 0.006655, 0.032329, 0.044888]])
t_per_block_64 = np.array([[0.000436, 0.001018, 0.010970, 0.029569, 0.028081],
                           [0.000354, 0.000880, 0.004945, 0.033257, 0.050533],
                           [0.000351, 0.000879, 0.005805, 0.021880, 0.029751]])
t_per_block_100 = np.array([[0.000406, 0.001021, 0.006532, 0.027483, 0.043187],
                           [0.000404, 0.000880, 0.006133, 0.023168, 0.048368],
                           [0.000506, 0.000988, 0.007787, 0.025319, 0.034700]])
t_per_block_96 = np.array([[0.000775, 0.000973, 0.008396, 0.027167, 0.057904],
                          [0.000924, 0.001036, 0.006609, 0.043755, 0.033635],
                          [0.000902, 0.001068, 0.010535, 0.031782, 0.035701]])

vars_96 = np.var(t_per_block_96, axis=0) *1000

t_per_block_32  = 1000 * np.mean(t_per_block_32, axis=0)
t_per_block_64  = 1000 * np.mean(t_per_block_64, axis=0)
t_per_block_100 = 1000 * np.mean(t_per_block_100, axis=0)
t_per_block_96 = 1000 * np.mean(t_per_block_96, axis=0)

t_per_block_96_u = uarray(t_per_block_96, vars_96)
print(t_per_block_96_u)

plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=14)

plt.plot(Ns, t_per_block_32, label="32 threads per block")
plt.plot(Ns, t_per_block_64, label="64 threads per block")
plt.plot(Ns, t_per_block_96, label="96 threads per block")
plt.plot(Ns, t_per_block_100, label="100 threads per block")
plt.xlabel(r"N / \#")
plt.ylabel("t / ms")
plt.grid()
plt.legend()
plt.savefig(os.path.join(FIG_PATH,"step2.png"))