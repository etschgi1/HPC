import os, re
import numpy as np
import pandas as pd
import re
from uncertainties import ufloat
lab_2_path = "../../lab_report/fig/lab2"
res_path = "../scripts/output/25/4_1"
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


    return times_dict

def getratios(paths): 
    data_ = {}
    for path in paths: 
        with open(os.path.join(path, "output.txt"), 'r') as f: 
            output = f.read()
        times_dict = parse_mpi_output(output)
        ratios = [times["ratio_time"] for times in times_dict.values() if "ratio_time" in times.keys()]
        ratio = ufloat(np.mean(ratios), np.std(ratios))
        label = int(path.split("/")[-1].split("x")[0])
        data_[label] = ratio
    # ascending print out according to label
    for label, ratio in sorted(data_.items()):
        print(f"{label}x{label} & \\num{{{ratio.nominal_value:.2f}({ratio.std_dev:.2f})}} \\\\\\hline")
    

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    res_path = os.path.join(path,res_path)
    print(res_path)
    subfolders = [f.path for f in os.scandir(res_path) if f.is_dir()]
    getratios(subfolders)
    print("---------PART B 1000x1000--------")
    res_pathb = os.path.join(path, "../scripts/output/25b/")
    res_paths = [os.path.join(res_pathb, x) for x in ["30_1/1000x1000"]]
    getratios(res_paths)    