import numpy as np
import matplotlib.pyplot as plt

import os

os.chdir(os.path.dirname(__file__))

plot_path = "../../lab_report/fig/lab2"
# grid points
grid_size = [100,200,400]
comp = [32.5,289.1,1886.9]
exchange = [5.6+13.3,13.3+48.8,22.2+206.1]
plt.plot(comp, exchange, 'o')
# fit using least squares
coefficients = np.polyfit(comp, exchange, 2)
# quadratic fit
poly = lambda x: coefficients[0]*x**2 + coefficients[1]*x + coefficients[2]
x = np.linspace(0, max(comp), int(max(comp)))

min_id = np.argmin(abs(poly(x)-x))
print(f"Minimum at x = {x[min_id]}")
min_x = x[min_id]

ax1 = plt.gca()


ax1.plot(x, poly(x), label=f"y = {coefficients[0]:.2e}x^2 + {coefficients[1]:.2f}x + {coefficients[2]:.2f}, R^2 = {np.corrcoef(comp, exchange)[0,1]**2:.3f}")
# add twin x with grid_size - second axis
ax1.grid()
ax1.vlines(min_x, 0, max(exchange), linestyles='dashed', label=f"Minimum at x = {min_x:.2f}")

ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(comp)
ax2.set_xticklabels(grid_size)

ax2.set_xlabel("Grid size")
ax1.set_xlabel("Compute time (ms)")
ax1.set_ylabel("Exchange time (ms)")
ax2.set_xlabel("Grid size")
ax1.legend()

plt.savefig(f"{plot_path}/estimate25.png")
plt.close()
# so we found minimum at some time!

# now fit grid to time
# fit grid size to compute time using least squares
coefficients_grid = np.polyfit(grid_size, comp, 2)
# quadratic fit
poly_grid = lambda x: coefficients_grid[0]*x**2 + coefficients_grid[1]*x + coefficients_grid[2]
x_grid = np.linspace(0, max(grid_size), int(max(grid_size)))
# find point with value x_min
min_id = np.argmin(abs(poly_grid(x_grid)-min_x))
print(f"Minimum at n = {x_grid[min_id]}")
plt.figure()
plt.vlines(x_grid[min_id], 0, max(comp), linestyles='dashed', label=f"Minimum at n = {round(x_grid[min_id],2)}")
plt.plot(grid_size, comp, 'o', label='Data points')
plt.plot(x_grid, poly_grid(x_grid), label=f"y = {coefficients_grid[0]:.2e}x^2 + {coefficients_grid[1]:.2f}x + {coefficients_grid[2]:.2f}, R^2 = {np.corrcoef(grid_size, comp)[0,1]**2:.3f}")
plt.xlabel("Grid size (side length)")
plt.ylabel("Compute time (ms)")
plt.xlim()
plt.legend()
plt.grid()
plt.savefig(f"{plot_path}/grid_to_time_fit.png")