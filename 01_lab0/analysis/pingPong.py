import numpy as np
import matplotlib.pyplot as plt
import re

data = []
# Load data from res
with open('01_lab0/res/pingPong.txt') as f:
    data = f.readlines()

num_elements = [int(re.search(r'Received \d+', l).group()[9:]) for l in data]
time = [float(re.search(r'took \d+\.\d+', l).group()[5:]) for l in data]


plt.plot(num_elements, time)
plt.xlabel('Number of elements')
plt.ylabel('Time (s)')
plt.title('Ping Pong')
plt.xscale('log')
plt.show()
