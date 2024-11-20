import os, re
import numpy as np
from util import *



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


def readerr(filepath="errors_MPI.dat"):
    with open(filepath, "r") as file:
        lines = file.readlines()
        errors = [float(line.strip()) for line in lines]
    return errors


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    visualise(readerr())
    