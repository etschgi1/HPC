import numpy as np
import matplotlib.pyplot as plt

import os
import matplotlib as mpl
from uncertainties import ufloat

os.chdir(os.path.dirname(__file__))


mpl.rc('text', usetex=True)
mpl.rc('font', family='serif', size=14)

plot_path = "../../lab_report/fig/lab2"
# grid points
iterations_1000 = 1241
grid_size = [100,200,400]
grid_nodes = [x**2 for x in grid_size]
comp = [18.6,150.6,1357.8] #ms
exchange = [1.3+1.7,3.6*6.8,10.1+26.4] #ms

fit_comp = np.polyfit(grid_nodes, comp, 2)
fit_exchange = np.polyfit(grid_nodes, exchange, 1)
R_2_comp = np.corrcoef(grid_nodes, comp)[0,1]**2
R_2_exchange = np.corrcoef(grid_nodes, exchange)[0,1]**2
print(f"Compute time fit: y = {fit_comp[0]:.2e}x + {fit_comp[1]:.2f}, R^2 = {R_2_comp:.3f}")
print(f"Exchange time fit: y = {fit_exchange[0]:.2e}x + {fit_exchange[1]:.2f}, R^2 = {R_2_exchange:.3f}")
x = np.linspace(0, 400**2, int(max(grid_nodes))//100)
argmin_bet_fits = np.argmin(abs(np.polyval(fit_comp, x) - np.polyval(fit_exchange, x)))
min_x_side = np.sqrt(x[argmin_bet_fits])
plt.plot(grid_nodes, comp, 'o', label="Compute time")
plt.plot(grid_nodes, exchange, 'o', label="Exchange time")
plt.plot(x, np.polyval(fit_comp, x),'blue', label="Compute time fit")
plt.plot(x, np.polyval(fit_exchange, x),'orange', label="Exchange time fit")
plt.grid()
plt.vlines(min_x_side**2, 0, max(comp), linestyles='dashed', label=f"Comm. = Comp.\nat x = {min_x_side**2:.1f} $\\rightarrow$ {min_x_side:.0f}x{min_x_side:.0f} grid")
plt.legend()
plt.xscale("log")
plt.xlabel("Grid points")
plt.ylabel("Time (ms)")
plt.savefig(f"{plot_path}/estimate25.png")

plt.close()

# stencil part

def t_data(ex, n_sqrt, P, it): 
    return ex / (2 * n_sqrt * it * P)

def t_op(comp, n, it): 
    return comp / (4*n**2 * it)
iterations = [141, 274, 529]
t_ops = [t_op(c, n, i) for c, n, i in zip(comp, grid_size, iterations)]
t_op_mean = ufloat(np.mean(t_ops), np.std(t_ops))
print(f"Time for one operation: {t_op_mean:.2e} ms")
comp_1000 = t_op_mean * 4 * 1000**2 * iterations_1000
print(f"Compute time for n=1000: {comp_1000:.2e} ms")

# fit exchange linear
coefficients = np.polyfit(grid_size, exchange, 1)
x = np.linspace(grid_size[0], 1000, 100)
poly = lambda x: coefficients[0]*x + coefficients[1]
R2 = np.corrcoef(grid_size, exchange)[0,1]**2
print(f"Exchange time fit: y = {coefficients[0]:.2e}x + {coefficients[1]:.2f}, R^2 = {R2:.3f}")
plt.plot(grid_size, exchange, 'o', label="Exchange time")
plt.plot(x, poly(x), label=f"y = ${coefficients[0]:.2e}x + {coefficients[1]:.2f}$")
plt.grid()
plt.xlabel("Grid points")
plt.ylabel("Time (ms)")
plt.legend()
plt.savefig(f"{plot_path}/estimate25_stencil.png")
plt.close()

t_comm_1000 = poly(1000**2)
print(f"Communication time for n=1000: {t_comm_1000:.2e} ms")
P = t_data(np.mean(exchange), min_x_side, t_op_mean, iterations_1000)
print(f"Number of processors for n=1000: {P}")