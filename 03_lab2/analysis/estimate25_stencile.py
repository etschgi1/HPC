import numpy as np
import matplotlib.pyplot as plt
import sympy
import os
import matplotlib as mpl

os.chdir(os.path.dirname(__file__))

# grid points
iterations_1000 = 1241
grid_size = [100,200,400]
iterations = [141, 274, 529]
N = 4
comp = [18.6,150.6,1357.8]
exchange = [1.3+1.7,3.6*6.8,10.1+26.4]

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

def P(ex, t_data, n, iter): 
    return ex / (t_data * 2 * n**2 * iter)

P_1000 = P(np.array(exchange).mean(), t_1000_comp, 1000, iterations_1000)
print(P_1000)