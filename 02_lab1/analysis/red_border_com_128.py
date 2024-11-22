import os, re
import numpy as np
import matplotlib.pyplot as plt
from util import update_input_file, reset_input_file
from uncertainties import ufloat

def border_com(togologies, grids, skips, omega=1.95, max_iter=15000):
    input_file = "input.dat"
    results = {}  # Dictionary to store omega and corresponding number of iterations
    reset_input_file()
    for top in togologies:
        gridres = {}
        for grid in grids: 
            if grid not in gridres:  # Initialize the grid key
                gridres[grid] = []
            for skip in skips:
                # Construct the command line with the current omega
                # print(f"Current path: {os.getcwd()}")
                print(f"use skip {skip}")
                exec_line = f"mpirun -np 4 ./MPI_Poisson.out {top[0]} {top[1]} {omega} {skip}"
                
                # alter the input file
                update_input_file(nx=grid[0], ny=grid[1], max_iter=max_iter)
                # Execute the MPI program
                os.system(exec_line + " > output.txt")
                iterations = None
                elapsed_times = []
                # Read the output file and extract the number of iterations
                with open("output.txt", "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        match_iterations = re.search(r"Number of iterations\s*:\s*(\d+)", line)
                        if match_iterations:
                            iterations = int(match_iterations.group(1))
                            print(f"Took {iterations} iterations for grid {grid} and topology {top} and skips {skip}")
                        match_time = re.search(r"Elapsed Wtime\s*([\d\.]+)\s*s", line)
                        if match_time:
                            elapsed_times.append(float(match_time.group(1)))
                elapsed_time = ufloat(np.mean(elapsed_times), np.std(elapsed_times))
                gridres[grid] += [(iterations, elapsed_time)]
        results[top] = gridres
        
    # delete the output file
    os.system("rm output.txt")
    # restore the original input file
    reset_input_file()
    return results

def visualise(res, tops, grids, skips):
    # LaTeX font setup
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=14)
    lab2_path = "../../lab_report/fig/lab1"

    for top in tops:
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()  # Create twin axes only once per topology

        for grid in grids:
            grid_label = f"{grid[0]}x{grid[1]}"
            skips_list = []
            iterations_list = []
            times_list = []

            # Extract data for the current topology and grid
            for c, skip in enumerate(skips):
                result = res[top][grid][c]
                iterations, elapsed_time = result
                skips_list.append(skip)
                iterations_list.append(iterations)
                times_list.append(elapsed_time.nominal_value)  # Use nominal value for plotting

            # Plot iterations and elapsed time for this grid
            ax1.plot(
                skips_list,
                iterations_list,
                label=f"Iterations ({grid_label})",
                linestyle="--",
                marker="o"
            )
            ax2.plot(
                skips_list,
                times_list,
                label=f"Time ({grid_label})",
                linestyle="-",
                marker="x"
            )

        # Add labels and customize axes
        ax1.set_xlabel("Number of Skips Between Border Exchanges")
        ax1.set_ylabel("Iterations", color="blue")
        ax2.set_ylabel("Elapsed Time (s)", color="orange")

        # Add a title and a combined legend
        plt.title(f"Performance vs Skips for Topology {top}")
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")
        plt.grid()

        # Save the figure for the current topology
        plt.tight_layout()
        plt.savefig(os.path.join(lab2_path, f"performance_skips_topology_{top[0]}x{top[1]}.png"))
        plt.close()


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    tops = [(4, 1)]
    grids = [(10,10),(25,25),(50,50),(100,100)]#, (200,200), (800,800)]#, (200,200), (800, 800)]#, (3200, 3200)]
    skips = [1,2,3,4,5,7,10]#,15,25,50,100]
    res = border_com(tops, grids, skips)
    visualise(res, tops, grids, skips)