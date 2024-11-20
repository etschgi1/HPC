import os, re
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

orig_input = """nx: 100
ny: 100
precision goal: 0.0001
max iterations: 5000
source: 0.35 0.70 4.0
source: 0.625 0.75 4.0
source: 0.375 0.25 4.0"""

def scaling(togologies, grids, omega = 1.95):
    exec_line_base = "mpirun -np=4 ./MPI_Poisson.out "
    input_file = "input.dat"
    results = {}  # Dictionary to store omega and corresponding number of iterations
    
    for top in togologies:
        gridres = {}
        for grid in grids: 

        # Construct the command line with the current omega
            exec_line = exec_line_base + f"{top[0]} {top[1]} {omega}"
        
        # alter the input file
            with open(input_file, "w") as file:
                file.write(f"nx: {grid[0]}\nny: {grid[1]}\nprecision goal: 0.0001\nmax iterations: 5000\nsource: 0.35 0.70 4.0\nsource: 0.625 0.75 4.0\nsource: 0.375 0.25 4.0")
            
            # Execute the MPI program
            os.system(exec_line + " > output.txt")
            elapsed_times = []   
            iterations = None     
            # Read the output file and extract the number of iterations
            with open("output.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    match_iterations = re.search(r"Number of iterations\s*:\s*(\d+)", line)
                    if match_iterations:
                        iterations = int(match_iterations.group(1))
                    match_time = re.search(r"Elapsed Wtime\s*([\d\.]+)\s*s", line)
                    if match_time:
                        elapsed_times.append(float(match_time.group(1)))
            avg_time_per_it = np.mean(elapsed_times) / iterations * 1000
            stderr_time_per_it = np.std(elapsed_times) / iterations * 1000
            print(f"Topology: {top}, Grid: {grid}, Omega: {omega}, Avg time: {avg_time_per_it} ms, Stderr time: {stderr_time_per_it} ms, Iterations: {iterations}")
            gridres[grid] = {"iterations": iterations, "avg_time_per_it": avg_time_per_it, "stderr_time_per_it": stderr_time_per_it}
        
        results[top] = gridres
        
    # delete the output file
    os.system("rm output.txt")
    # restore the original input file
    with open(input_file, "w") as file:
        file.write(orig_input)
    return results


def visualise(res, tops, grids):
    # LaTeX font setup
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=14)
    lab2_path = "../../lab_report/fig/lab1"

    for top in tops:
        # Extract grid sizes and average times from the results for the given topology
        grid_sizes = [grid[0]*grid[1] for grid in grids]  # Use only one dimension (square grids)
        avg_times = [res[top][grid]["avg_time_per_it"] for grid in grids]
        stderr_times = [res[top][grid]["stderr_time_per_it"] for grid in grids]

        # Perform a linear fit
        slope, intercept, r_value, p_value, std_err = linregress(grid_sizes, avg_times)

        # Generate linear fit values for plotting
        fit_times = [slope * size + intercept for size in grid_sizes]

        # Plot the data and the linear fit
        plt.figure(figsize=(8, 6))
        plt.errorbar(grid_sizes, avg_times, yerr=stderr_times, fmt="o", label="Data with stderr")
        plt.plot(grid_sizes, fit_times, "r--", label=f"Fit: $y = {slope:.2e}x + {intercept:.2e}$, R$^2$ = {r_value**2:.3f}")

        # Add the equation and stderr as text on the plot
        # plt.text(
        #     0.05 * max(grid_sizes), 
        #     0.8 * max(avg_times), 
        #     f"Slope: {slope:.2f} $\pm$ {std_err:.2f}\nIntercept: {intercept:.2f}",
        #     fontsize=12,
        #     bbox=dict(facecolor="white", alpha=0.8)
        # )

        # Labels and title
        plt.xlabel("Grid size (nx * ny)")
        plt.ylabel("Average Time per Iteration (ms)")
        plt.title(f"Scaling for Topology {top}")
        plt.legend()
        plt.grid()

        # Save the figure
        output_path = os.path.join(lab2_path, f"scaling_topology_{top[0]}x{top[1]}.png")
        plt.savefig(output_path)
        print(f"Saved plot for topology {top} at {output_path}")

        # Close the figure to free memory
        plt.close()


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    tops = [(4, 1), (2, 2)]
    grids = [(10, 10), (25, 25), (50, 50), (100, 100), (200, 200), (400, 400), (800, 800), (1600, 1600)]
    res = scaling(tops, grids)
    visualise(res, tops, grids)