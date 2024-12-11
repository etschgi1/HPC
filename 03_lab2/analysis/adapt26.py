import os, re
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
from uncertainties import ufloat
lab_2_path = "../../lab_report/fig/lab2"
res_path = "../scripts/output/26/2_2"
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
        
        total_exchange = re.match(r"\((\d+)\) - Exchange time \(total\):\s+([\d.]+)", line)
        if total_exchange:
            rank, total_exchange_time = total_exchange.groups()
            times_dict[rank]["total_exchange_time"] = float(total_exchange_time)
        ratio = re.match(r"\((\d+)\) - Exchange time - comp ratio:\s+([\d.]+)", line)
        if ratio:
            rank, ratio_time = ratio.groups()
            times_dict[rank]["ratio_time"] = float(ratio_time)
        

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


    prec = []
    for line in output.splitlines():
        if "Precision:" in line:
            prec.append(float(line.split(": ")[-1]))
        elif "Number of iterations : " in line:
            times_dict["iterations"] = int(line.split(": ")[-1])
    times_dict["precision"] = prec
    return times_dict

def adapt(paths): 
    data_ = {}
    for path in paths:
        label = path.split("/")[-1]
        data_[label] = {}
        with open(os.path.join(path, "ref_output.txt"), 'r') as file: 
            data = file.read()
            data_[label]["ref"] = parse_mpi_output(data)
        with open(os.path.join(path, "adapt_output.txt"), 'r') as file: 
            data = file.read()
            data_[label]["adapt"] = parse_mpi_output(data)
    # make plots :)))
    labels = list(data_.keys())
    label_nr = [int(label.split("x")[0]) for label in labels]
    # gather iterations: 
    iterations_ref = [data_[label]["ref"]["iterations"] for label in labels]
    iterations_adapt = [data_[label]["adapt"]["iterations"] for label in labels]
    # iteration count
    for i, label_nr in enumerate(label_nr): 
        print(f"{label_nr}, Reference: {iterations_ref[i]}, Adaptive: {iterations_adapt[i]}")
    
    # time data
    time_conv_ref = [data_[label]["ref"]["average"]["total_time"] for label in labels]
    time_conv_adapt = [data_[label]["adapt"]["average"]["total_time"] for label in labels]

    # latex plot
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif", "font.size": 14
    })

    print(time_conv_adapt)
    print(time_conv_ref)
    bar_width = 0.4
    x = np.arange(len(labels))
    plt.bar(x-bar_width/2, time_conv_ref, width=bar_width,color="#F05956", label="Reference")
    plt.bar(x+bar_width/2, time_conv_adapt, width=bar_width,color="#54B6A5", label="Adaptive")
    plt.xticks(x, labels)
    plt.grid()
    plt.xlabel("Grid size (n)")
    plt.ylabel("Convergence time (s)")
    plt.legend()
    plt.savefig(f"{lab_2_path}/adapt_time.png")
    plt.close()

    comp_time_ref = [data_[label]["ref"]["average"]["compute_time"] for label in labels]
    comp_time_adapt = [data_[label]["adapt"]["average"]["compute_time"] for label in labels]
    rest_time_ref = [data_[label]["ref"]["average"]["sum_times"] for label in labels]
    rest_time_adapt = [data_[label]["adapt"]["average"]["sum_times"] for label in labels]
    rest_time_ref = [x - y for x, y in zip(rest_time_ref, comp_time_ref)]
    rest_time_adapt = [x - y for x, y in zip(rest_time_adapt, comp_time_adapt)]

    # plot stacked compute 
    plt.bar(x, comp_time_ref, width=bar_width, color="#F05956", label="Compute time (ref)")
    plt.bar(x, rest_time_ref, width=bar_width, color="#F7A2A1", label="Communication time (ref)", bottom=comp_time_ref)
    plt.bar(x+bar_width, comp_time_adapt, width=bar_width, color="#54B6A5", label="Compute time (adapt)")
    plt.bar(x+bar_width, rest_time_adapt, width=bar_width, color="#A9DAD2", label="Communication time (adapt)", bottom=comp_time_adapt)
    plt.xticks(x, labels)
    plt.grid()
    plt.xlabel("Grid size (n)")
    plt.ylabel("Time (s)")
    plt.legend()
    plt.savefig(f"{lab_2_path}/adapt_stacked_time.png")
    plt.close()


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    res_path = os.path.join(path,res_path)
    paths = [os.path.join(res_path, f) for f in os.listdir(res_path)]
    adapt(paths)
    