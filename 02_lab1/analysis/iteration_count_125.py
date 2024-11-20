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

def scaling(togologies, grids, omegas):
    exec_line_base = "mpirun -np=4 ./MPI_Poisson.out "
    input_file = "input.dat"
    results = {}  # Dictionary to store omega and corresponding number of iterations
    
    for top in togologies:
        omega_res = {}
        for omega in omegas:
            print("--> omega: ", str(omega))
            gridres = {}
            for grid in grids: 

            # Construct the command line with the current omega
                exec_line = exec_line_base + f"{top[0]} {top[1]} {omega}"
            
            # alter the input file
                with open(input_file, "w") as file:
                    file.write(f"nx: {grid[0]}\nny: {grid[1]}\nprecision goal: 0.0001\nmax iterations: 5000\nsource: 0.35 0.70 4.0\nsource: 0.625 0.75 4.0\nsource: 0.375 0.25 4.0")
                
                # Execute the MPI program
                os.system(exec_line + " > output.txt")
                iterations = None     
                # Read the output file and extract the number of iterations
                with open("output.txt", "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        match_iterations = re.search(r"Number of iterations\s*:\s*(\d+)", line)
                        if match_iterations:
                            iterations = int(match_iterations.group(1))
                gridres[grid] = iterations
            omega_res[omega] = gridres
        results[top] = omega_res
        
    # delete the output file
    os.system("rm output.txt")
    # restore the original input file
    with open(input_file, "w") as file:
        file.write(orig_input)
    return results


def visualise(res, tops, grids, omegas):
    # LaTeX font setup
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=14)
    lab2_path = "../../lab_report/fig/lab1"

    for top in tops:
        # Extract grid sizes and average times from the results for the given topology
        grid_sizes = [grid[0]*grid[1] for grid in grids]  # Use only one dimension (square grids)
        grid_lengths = [grid[0] for grid in grids]
        plt.title(f"Number of iterations vs Grid size for topology {top}")
        for omega in omegas:
            iterations = [res[top][omega][grid] for grid in grids]
            print(f"Iterations for topology {top} and omega {omega}: {iterations}")
            
            plt.plot(grid_lengths, iterations, marker="o", label=r"$\omega$ = "+ str(omega))

            plt.xlabel("Grid length (nx)")
            plt.ylabel("Number of iterations")
            # plt.xscale("log", base=2)
            plt.grid()
            plt.legend()
        plt.savefig(os.path.join(lab2_path, f"iteration_count_{top}_125.png"))
        plt.close()


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    tops = [(4, 1)]
    grids = [(10, 10), (25, 25), (50, 50), (100, 100), (200, 200), (400, 400), (800, 800), (1600, 1600)]#, (3200, 3200)]
    omegas = [1.9, 1.93, 1.95]
    res = scaling(tops, grids, omegas)
    visualise(res, tops, grids, omegas)