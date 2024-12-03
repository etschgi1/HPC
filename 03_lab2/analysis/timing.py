import os, re
import numpy as np
import pandas as pd

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
    

def run_scenarios(topologies, grid_sizes):
    res = {}
    for topology in topologies: 
        for grid_size in grid_sizes: 
            setup(topology, grid_size)
            # run Solver
            print("----------------- Running Solver (topology: {}, grid_size: {}) -----------------".format(topology, grid_size))
            output = os.popen(f"mpirun -np {topology[0]*topology[1]} ./MPI_Fempois.out").read()
            times = getTimes(output)
            clean()
            print(output)
            break
        break




def visualise(res):
    from matplotlib import pyplot as plt
    # latex rc
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=14)
    lab2_path = "../../lab_report/fig/lab1"
    omegas = list(res.keys())
    iterations = list(res.values())
    min_ = min(iterations)
    min_idx = iterations.index(min_)
    plt.plot(omegas, iterations, marker="o")
    plt.plot(omegas[min_idx], min_, marker="x", color="red", label="Min iterations")
    plt.xlabel("Omega")
    plt.ylabel("Number of iterations")
    plt.title("Number of iterations vs Omega")
    plt.grid()
    plt.savefig(os.path.join(lab2_path, "best_omega_122.png"))
    # plt.show()


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    run_scenarios([(1,4),(2,2)], [(100,100), (200,200), (400,400)])
    