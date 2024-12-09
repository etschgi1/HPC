import os
import re
import numpy as np
import matplotlib.pyplot as plt
from util import update_input_file, reset_input_file
from uncertainties import ufloat

def measure_exchange_time(topologies, grids, omega=1.95, max_iter=50000, num_repeats=3):
    """
    Measure exchange times and compute mean over multiple repetitions.
    
    Args:
        topologies: List of topologies (e.g., [(2, 2), (3, 3)]).
        grids: List of grid sizes (e.g., [(100, 100), (200, 200)]).
        omega: Relaxation factor for the solver.
        max_iter: Maximum iterations for the solver.
        num_repeats: Number of repetitions for each configuration.

    Returns:
        Dictionary containing measured results.
    """
    input_file = "input.dat"
    results = {}  # Dictionary to store results
    reset_input_file()

    for topology in topologies:
        gridres = {}
        processors = topology[0] * topology[1]  # Calculate the number of processors
        for grid in grids:
            if grid not in gridres:  # Initialize the grid key
                gridres[grid] = []
            print(f"Running with grid={grid}, topology={topology}, processes={processors}")
            
            # Initialize storage for repetitions
            all_exchange_times = []
            all_elapsed_times = []
            all_iterations = []

            for _ in range(num_repeats):
                exec_line = f"mpirun -np {processors} ./MPI_Poisson.out {topology[0]} {topology[1]} {omega}"
                
                # Update input file for the current grid
                update_input_file(nx=grid[0], ny=grid[1], max_iter=max_iter)
                
                # Run the solver and capture the output
                os.system(exec_line + " > output.txt")
                iterations = None
                exchange_times = []
                elapsed_times = []

                # Parse the output file
                with open("output.txt", "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        # Parse iterations
                        match_iterations = re.search(r"Number of iterations\s*:\s*(\d+)", line)
                        if match_iterations:
                            iterations = int(match_iterations.group(1))

                        # Parse exchange times
                        match_exchange = re.search(r"Exchange time:\s+([\d\.]+)", line)
                        if match_exchange:
                            exchange_times.append(float(match_exchange.group(1)))

                        # Parse elapsed times
                        match_elapsed = re.search(r"Elapsed Wtime\s+([\d\.]+)", line)
                        if match_elapsed:
                            elapsed_times.append(float(match_elapsed.group(1)))

                # Compute average values for the current run
                avg_exchange_time = np.mean(exchange_times)
                avg_elapsed_time = np.mean(elapsed_times)
                all_exchange_times.append(avg_exchange_time)
                all_elapsed_times.append(avg_elapsed_time)
                all_iterations.append(iterations)

            # Compute the overall mean and std for exchange time and elapsed time
            mean_exchange_time = np.mean(all_exchange_times)
            std_exchange_time = np.std(all_exchange_times)
            mean_elapsed_time = np.mean(all_elapsed_times)
            std_elapsed_time = np.std(all_elapsed_times)
            fraction_exchange = mean_exchange_time / mean_elapsed_time

            print(f"Grid: {grid}, Topology: {topology}, Iterations: {np.mean(all_iterations):.2f}")
            print(f"Mean Exchange Time: {mean_exchange_time:.6f} ± {std_exchange_time:.6f}")
            print(f"Mean Elapsed Time: {mean_elapsed_time:.6f} ± {std_elapsed_time:.6f}")
            print(f"Fraction Exchange: {fraction_exchange:.6f}")

            # Store results
            gridres[grid].append((processors, np.mean(all_iterations), 
                                  mean_exchange_time, std_exchange_time, 
                                  mean_elapsed_time, std_elapsed_time, 
                                  fraction_exchange))
        results[topology] = gridres

    # Clean up
    os.system("rm output.txt")
    reset_input_file()
    return results

def measure_exchange_time_from_files(basefolder, topologies, grids, omega=1.95, max_iter=50000):
    """
    Measure exchange times and compute mean from pre-existing files.

    Args:
        basefolder: Path to the folder containing the output files.
        topologies: List of topologies (e.g., [(2, 2), (3, 3)]).
        grids: List of grid sizes (e.g., [(100, 100), (200, 200)]).
        omega: Relaxation factor for the solver.
        max_iter: Maximum iterations for the solver.

    Returns:
        Dictionary containing measured results.
    """
    results = {}  # Dictionary to store results

    for topology in topologies:
        gridres = {}
        processors = topology[0] * topology[1]  # Calculate the number of processors
        topology_folder = os.path.join(basefolder, f"{topology[0]}_{topology[1]}")

        for grid in grids:
            if grid not in gridres:  # Initialize the grid key
                gridres[grid] = []
            grid_folder = os.path.join(topology_folder, f"{grid[0]}x{grid[1]}")
            if not os.path.exists(grid_folder):
                print(f"Warning: Grid folder {grid_folder} does not exist. Skipping.")
                continue

            print(f"Processing grid={grid}, topology={topology}, processes={processors}")
            all_exchange_times = []
            all_elapsed_times = []
            all_iterations = []

            for file in os.listdir(grid_folder):
                if not file.endswith(".txt"):
                    continue

                filepath = os.path.join(grid_folder, file)
                iterations = None
                exchange_times = []
                elapsed_times = []

                # Read the output file and parse the data
                with open(filepath, "r") as f:
                    for line in f:
                        # Parse iterations
                        match_iterations = re.search(r"Number of iterations\s*:\s*(\d+)", line)
                        if match_iterations:
                            iterations = int(match_iterations.group(1))

                        # Parse exchange times
                        match_exchange = re.search(r"Exchange time:\s+([\d\.]+)", line)
                        if match_exchange:
                            exchange_times.append(float(match_exchange.group(1)))

                        # Parse elapsed times
                        match_elapsed = re.search(r"Elapsed Wtime\s+([\d\.]+)", line)
                        if match_elapsed:
                            elapsed_times.append(float(match_elapsed.group(1)))

                # If no valid data was found in the file, skip it
                if not exchange_times or not elapsed_times or iterations is None:
                    print(f"Warning: No valid data in {filepath}. Skipping.")
                    continue

                # Compute average values for the current file
                avg_exchange_time = np.mean(exchange_times)
                avg_elapsed_time = np.mean(elapsed_times)
                all_exchange_times.append(avg_exchange_time)
                all_elapsed_times.append(avg_elapsed_time)
                all_iterations.append(iterations)

            # Compute the overall mean and std for exchange time and elapsed time
            if all_exchange_times:
                mean_exchange_time = np.mean(all_exchange_times)
                std_exchange_time = np.std(all_exchange_times)
                mean_elapsed_time = np.mean(all_elapsed_times)
                std_elapsed_time = np.std(all_elapsed_times)
                fraction_exchange = mean_exchange_time / mean_elapsed_time

                print(f"Grid: {grid}, Topology: {topology}, Iterations: {np.mean(all_iterations):.2f}")
                print(f"Mean Exchange Time: {mean_exchange_time:.6f} ± {std_exchange_time:.6f}")
                print(f"Mean Elapsed Time: {mean_elapsed_time:.6f} ± {std_elapsed_time:.6f}")
                print(f"Fraction Exchange: {fraction_exchange:.6f}")

                # Store results
                gridres[grid].append((processors, np.mean(all_iterations), 
                                  mean_exchange_time, std_exchange_time, 
                                  mean_elapsed_time, std_elapsed_time, 
                                  fraction_exchange))

        results[topology] = gridres

    return results

def visualize_exchange_time(results, grids):

    # LaTeX font setup
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=16)
    lab2_path = "../../lab_report/fig/lab1"

    # Fraction of exchange time
    plt.figure(figsize=(12, 8))

    for grid in grids:
        processors_list = []
        fractions_list = []

        # Extract data for the current grid across all topologies
        for topology, gridres in results.items():
            if grid in gridres:
                for result in gridres[grid]:
                    # Updated unpacking
                    processors, _, _, _, _, _, fraction_exchange = result
                    processors_list.append(processors)
                    fractions_list.append(fraction_exchange)

        # Sort data by processor count to ensure a smooth line
        sorted_indices = np.argsort(processors_list)
        processors_list = np.array(processors_list)[sorted_indices]
        fractions_list = np.array(fractions_list)[sorted_indices]

        # Plot the connected line for this grid
        plt.plot(
            processors_list,
            fractions_list,
            marker="o",
            linestyle="-",
            label=f"{grid[0]}x{grid[1]}"
        )

    # Customize the plot
    plt.xlabel("Number of Processes")
    plt.ylabel("Fraction of Time in Exchange")
    plt.title("Fraction of Time in Exchange (All Configurations)")
    plt.legend(loc="best", fontsize=10)
    plt.xticks(processors_list)
    plt.grid()

    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(lab2_path, f"fraction_exchange_comparison_connected.png"))
    plt.close()

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    
    # Configurations
    topologies = [(i, i) for i in range(2, 7)]  # Generate (2,2), (3,3), ..., (6,6)
    topologies += [(2,3), (2,4), (3,4), (2,5)]  # Add (4,1) and (1,4)
    grids = [(100, 100), (200, 200), (400, 400), (800, 800)]

    # Measure and visualize
    results = measure_exchange_time_from_files("/home/etschgi1/REPOS/HPC/02_lab1/scripts/output/1210",topologies, grids)
    # results = measure_exchange_time(topologies, grids)
    print(results)
    visualize_exchange_time(results, grids)
