import matplotlib.pyplot as plt
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def striped(n,P):
    return 2*n*P

def boxed(n,P):
    return 4*n*np.sqrt(P)

plt.rc('text', usetex=True)
plt.rc('font', family='serif', size=16)

x = np.linspace(1, 20, 50)
plt.plot(x,striped(100,x), label="Striped")
plt.plot(x,boxed(100,x), label="Boxed")
plt.xlabel("P (Number of Processes)")
plt.ylabel("\\# Exchanged Datapoints per Iteration")
plt.xticks(np.arange(0, 21, 2))
plt.title("Striped vs. Boxed partitioning (n=100)")
plt.scatter(4,striped(100,4), marker="x", color="red", label="P=4")
plt.grid()
plt.legend()
plt.savefig("../lab2/scale23.png")