import os
import re
import numpy as np
import pandas as pd
from uncertainties import ufloat, UFloat

def parse_solver_output(filepath="output.txt"):
    """
    Parse the output from the solver to extract aggregated metrics for each processor.
    Returns:
        A list of dictionaries containing parsed metrics.
    """
    metrics = []

    with open(filepath, "r") as file:
        lines = file.readlines()

    current_data = {}
    for line in lines:
        # Parse exchange time
        match_exchange = re.search(r"\((\d+)\) Exchange time:\s+([\d\.]+)", line)
        if match_exchange:
            proc_id = int(match_exchange.group(1))
            exchange_time = float(match_exchange.group(2))
            if proc_id not in current_data:
                current_data[proc_id] = {"exchange_times": []}
            current_data[proc_id]["exchange_times"].append(exchange_time)

        # Parse total data transferred
        match_total_data = re.search(r"Total Data Transferred:\s+([\d\.]+)", line)
        if match_total_data:
            total_data = float(match_total_data.group(1))
            for proc in current_data.values():
                proc["total_data"] = total_data

        # Parse elapsed time
        match_elapsed = re.search(r"\((\d+)\) Elapsed Wtime\s+([\d\.]+)", line)
        if match_elapsed:
            proc_id = int(match_elapsed.group(1))
            elapsed_time = float(match_elapsed.group(2))
            current_data[proc_id]["elapsed_time"] = elapsed_time

        # Parse bandwidth
        match_bandwidth = re.search(r"Average Bandwidth:\s+([\d\.]+)", line)
        if match_bandwidth:
            bandwidth = float(match_bandwidth.group(1))
            for proc in current_data.values():
                proc["bandwidth"] = bandwidth

    metrics.append(current_data)
    return metrics


def aggregate_metrics(metrics, topology, grid):
    """
    Aggregate metrics across processors.
    Args:
        metrics: Parsed metrics from all processors.
        topology: The topology (e.g., (2, 2)).
        grid: The grid size (e.g., (200, 200)).
    Returns:
        Aggregated metrics as a dictionary.
    """
    exchange_times = []
    elapsed_times = []
    total_data = None
    bandwidths = []

    for proc_data in metrics[0].values():
        exchange_times.extend(proc_data["exchange_times"])
        elapsed_times.append(proc_data["elapsed_time"])
        bandwidths.append(proc_data["bandwidth"])
        if total_data is None:
            total_data = proc_data["total_data"]

    avg_exchange_time = np.mean(exchange_times)
    std_exchange_time = np.std(exchange_times)
    avg_elapsed_time = np.mean(elapsed_times)
    std_elapsed_time = np.std(elapsed_times)
    avg_bandwidth = np.mean(bandwidths)
    std_bandwidth = np.std(bandwidths)

    fraction_latency = avg_exchange_time / avg_elapsed_time * 100

    return {
        "topology": f"{topology[0]}x{topology[1]}",
        "grid": f"{grid[0]}x{grid[1]}",
        "latency_ms": ufloat(avg_exchange_time, std_exchange_time) * 1000,
        "latency_percent": ufloat(fraction_latency, 0),  # Percent is derived, so no error
        "bandwidth": ufloat(avg_bandwidth, std_bandwidth),
        "total_data": total_data,
    }


def save_latex_table(data, filename):
    """
    Save aggregated data as a LaTeX table using siunitx for uncertainty formatting.
    Args:
        data: List of dictionaries containing aggregated data.
        filename: File path to save the LaTeX table.
    """
    # Prepare the DataFrame
    df = pd.DataFrame(data)

    # Custom formatting for siunitx-compatible uncertainty columns
    def format_siunitx(value):
        if isinstance(value, UFloat) and value.s != 0:
            return f"{value.n:.3f}({value.s:.3f})"
        return f"{value:.3f}"


    # Format specific columns
    df["latency_ms"] = df["latency_ms"].apply(format_siunitx)
    df["latency_percent"] = df["latency_percent"].apply(format_siunitx)
    df["bandwidth"] = df["bandwidth"].apply(format_siunitx)
    df["total_data"] = df["total_data"].apply(lambda x: f"{x:.0f}")  # No uncertainties for total_data

    # Convert to LaTeX
    latex_table = df.to_latex(
        index=False,
        escape=False,  # Ensure LaTeX math formatting is preserved
        column_format="l|l|S[table-format=3.3]|S[table-format=3.1]|S[table-format=8.2]|S[table-format=8.0]",
    )

    # Add siunitx requirements at the top of the table
    latex_table = (
        "\\begin{table}[H]\n\\centering\n\\caption{Exchange Borders Metrics}\n"
        "\\begin{tabular}{l|l|S[table-format=3.3]|S[table-format=3.1]|S[table-format=8.2]|S[table-format=8.0]}\n"
        "Topology & Grid Size & {Latency (ms)} & {Latency (\%)} & {Bandwidth (\\si{\\byte\\per\\second})} & {Total Data (\\si{\\byte})} \\\\\n"
        + latex_table.split("\\midrule\n")[1].replace("\\\\", "\\\\\\hline")  # Keep only the table content
        + "\\end{table}\n"
    )
    # remove all rule lines 
    latex_table = re.sub(r"\\(top|mid|bottom)rule", "", latex_table)


    # Save to file
    with open(filename, "w") as f:
        f.write(latex_table)

    print(f"LaTeX table saved to {filename}")



if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)

    # Configurations
    topologies = [(4, 1), (2, 2), (3,3)]
    grids = [(200, 200), (400, 400), (800, 800)]

    all_results = []
    basepath = "/home/etschgi1/REPOS/HPC/02_lab1/scripts/output/1211"
    for topology in topologies:
        for grid in grids:
            print(f"Processing topology={topology}, grid={grid}")
            # os.system(f"mpirun -np {topology[0] * topology[1]} ./MPI_Poisson.out {topology[0]} {topology[1]} > output.txt")
            # metrics = parse_solver_output()
            metrics = parse_solver_output(os.path.join(basepath, f"{topology[0]}_{topology[1]}", f"{grid[0]}x{grid[1]}", "output.txt"))
            aggregated = aggregate_metrics(metrics, topology, grid)
            all_results.append(aggregated)

    # Save as LaTeX table
    save_latex_table(all_results, "../../lab_report/fig/lab1/exchange_metrics.tex")
