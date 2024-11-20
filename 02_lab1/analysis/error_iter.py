import os, re
import numpy as np
from util import *
from scipy.optimize import curve_fit



def visualise(res):
    from matplotlib import pyplot as plt
    # latex rc
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif', size=14)
    lab2_path = "../../lab_report/fig/lab1"
    # exp fit
    # def func(x, a, b):
    #     return a * np.exp(b * x)
    # popt, pcov = curve_fit(func, np.arange(len(res)), res)
    # print(popt)
    # print(pcov)
    # fity = func(np.arange(len(res)), *popt)
    # plt.plot(fity, label="Fit")
    plt.plot(res)
    # plt.legend()
    plt.grid()
    plt.xlabel("Iteration")
    # plt.xscale("log")
    plt.yscale("log")
    plt.ylabel("Error")
    plt.savefig(os.path.join(lab2_path, "errors_126.png"))
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
