import numpy as np
import matplotlib.pyplot as plt

import os
import matplotlib as mpl

os.chdir(os.path.dirname(__file__))

# grid points
iterations_1000 = 1241
grid_size = [100,200,400]
iterations = [141, 274, 529]
N = 4
comp = [32.5,289.1,1886.9]
exchange = [5.6+13.3,13.3+48.8,22.2+206.1]

striped_ex_per_P = [2*n for n in grid_size]
print(f"Striped exchange comm per Proc.: {striped_ex_per_P}")
times_per_dp_ex = [e/(8*n*i) for e,n,i in zip(exchange, grid_size, iterations)]
print(times_per_dp_ex)
print("Time for one op:")
time_one_op = [c / (4*n**2*i) for c,n,i in zip(comp, grid_size, iterations)]
print(time_one_op)

print("For n=1000")
t_1000_comp = np.array(time_one_op).mean() * 4 * 1000**2 * iterations_1000
print(t_1000_comp)


