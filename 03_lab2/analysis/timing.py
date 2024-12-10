import os, re
import numpy as np
import pandas as pd
import re
lab_2_path = "../../lab_report/fig/lab2"

def setup(topology, grid_size):
    # compile code
    print("----------------- Compiling  (topology: {}, grid_size: {}) -----------------".format(topology, grid_size))
    os.system("make all")
    # run GridDist
    os.system(f"./GridDist.out {topology[0]} {topology[1]} {grid_size[0]} {grid_size[1]}")

def clean():
    print("----------------- Cleaning -----------------")
    os.system("make clean")

def getTimes(data):
    pattern = r"\((\d)\) - Compute time: ([\d.]+)\n.*neighbors\): ([\d.]+)\n.*global\): ([\d.]+)\n.*local\)): ([\d.]+)\n.*Total time: ([\d.]+)"
    
import re
from collections import defaultdict

# Example function to parse MPI output
def parse_mpi_output(output):
    times_dict = defaultdict(dict)

    for line in output.splitlines():
        # Extract Elapsed time
        elapsed_match = re.match(r"\((\d+)\) Elapsed Wtime:\s+([\d.]+)", line)
        if elapsed_match:
            rank, elapsed_time = elapsed_match.groups()
            times_dict[rank]["elapsed_time"] = float(elapsed_time)
        
        # Extract Compute time
        compute_match = re.match(r"\((\d+)\) - Compute time:\s+([\d.]+)", line)
        if compute_match:
            rank, compute_time = compute_match.groups()
            times_dict[rank]["compute_time"] = float(compute_time)
        
        # Extract Exchange time (neighbors)
        exchange_neighbors_match = re.match(r"\((\d+)\) - Exchange time \(neighbors\):\s+([\d.]+)", line)
        if exchange_neighbors_match:
            rank, exchange_neighbors_time = exchange_neighbors_match.groups()
            times_dict[rank]["exchange_neighbors_time"] = float(exchange_neighbors_time)

        # Extract Exchange time (global)
        exchange_global_match = re.match(r"\((\d+)\) - Exchange time \(global\):\s+([\d.]+)", line)
        if exchange_global_match:
            rank, exchange_global_time = exchange_global_match.groups()
            times_dict[rank]["exchange_global_time"] = float(exchange_global_time)

        # Extract Sum of times
        sum_times_match = re.match(r"\((\d+)\) - Sum of times.*:\s+([\d.]+)", line)
        if sum_times_match:
            rank, sum_times = sum_times_match.groups()
            times_dict[rank]["sum_times"] = float(sum_times)

        # Extract Total time
        total_time_match = re.match(r"\((\d+)\) - Total time:\s+([\d.]+)", line)
        if total_time_match:
            rank, total_time = total_time_match.groups()
            times_dict[rank]["total_time"] = float(total_time)
    # calculate idle time for each rank
    slowest = max([times["total_time"] for times in times_dict.values()])
    for rank, times in times_dict.items():
        times["idle_time"] = slowest - times["total_time"]
    
    # create average
    average = defaultdict(float)
    for rank, times in times_dict.items():
        for key, value in times.items():
            average[key] += value
    for key in average.keys():
        if key != "rank":
            average[key] /= len(times_dict)
    times_dict["average"] = average


    return times_dict

def run_scenarios(topologies, grid_sizes, use_files=True):
    res = {}
    for topology in topologies: 
        res[topology] = {}
        for grid_size in grid_sizes: 

            if not use_files:
                setup(topology, grid_size)
                # run Solver
                print("----------------- Running Solver (topology: {}, grid_size: {}) -----------------".format(topology, grid_size))
                output = os.popen(f"mpirun -np {topology[0]*topology[1]} ./MPI_Fempois.out").read()
                times = getTimes(output)
                clean()
                print(output)
            else: 
                with open(f"/home/etschgi1/REPOS/HPC/03_lab2/scripts/output/22/{topology[0]}_{topology[1]}/{grid_size[0]}x{grid_size[1]}/output.txt", "r") as f:
                    output = f.read()
            res[topology][grid_size] = parse_mpi_output(output)
    return res




def latex(res):
    import pandas as pd
    import matplotlib.pyplot as plt
    import os

    # Initialize an empty list for table rows
    table_rows = []

    # Iterate through the topologies and grid sizes
    for topology, grid_data in res.items():
        for grid_size, metrics in grid_data.items():
            average_metrics = metrics['average']
            row = {
                "Topology": f"{topology[0]}x{topology[1]}",
                "Grid Size": f"{grid_size[0]}x{grid_size[1]}",
                "Elapsed Time": 1000 * average_metrics["elapsed_time"],
                "Compute Time": 1000 * average_metrics["compute_time"],
                "Exchange Neighbors Time": 1000 * average_metrics["exchange_neighbors_time"],
                "Exchange Global Time": 1000 * average_metrics["exchange_global_time"],
                "Idle Time": 1000 * average_metrics["idle_time"],
            }
            table_rows.append(row)

    # Convert to a DataFrame
    df = pd.DataFrame(table_rows)

    # Convert DataFrame to LaTeX table
    latex_table = df.to_latex(index=False, float_format="%.1f", escape=False)

    # Print to stdout
    print(latex_table)

    # Plot stacked bar chart

    # Extract components for stacking

    # latex rc
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=16)
    fig, ax = plt.subplots(figsize=(10, 6))
    components = ["Compute Time", "Exchange Neighbors Time", "Exchange Global Time", "Idle Time"]
    df.set_index(["Topology", "Grid Size"])[components].plot(kind="bar", stacked=True, ax=ax)

    # Customization
    ax.set_title("Stacked Bar Plot of Average Times (ms)")
    ax.set_ylabel("Time (ms)")
    ax.set_xlabel("Topology and Grid Size")
    ax.legend(loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(os.path.join(lab_2_path, "average_times_stacked_bar_22.png"))
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 6))

    # Extract components for stacking
    components = ["Exchange Neighbors Time", "Exchange Global Time", "Idle Time"]
    df.set_index(["Topology", "Grid Size"])[components].plot(kind="bar", stacked=True, ax=ax, color=["tab:orange", "tab:green", "tab:red"])

    # Customization
    ax.set_title("Stacked Bar Plot of Average Times (ms) [w/o compute]")
    ax.set_ylabel("Time (ms)")
    ax.set_xlabel("Topology and Grid Size")
    ax.legend(loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(os.path.join(lab_2_path, "average_times_stacked_bar_no_comp_22.png"))
    plt.close()

    return latex_table



if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    res = run_scenarios([(1,4),(2,2)], [(100,100), (200,200), (400,400)], use_files=True)
    latex(res)