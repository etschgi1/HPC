import os, re
import numpy as np


def best_omega_122(omegas):
    exec_line_base = "mpirun -np=4 ./MPI_Poisson.out 4 1 "
    results = {}  # Dictionary to store omega and corresponding number of iterations
    
    for omega in omegas:
        # Construct the command line with the current omega
        exec_line = exec_line_base + str(omega)
        
        # Execute the MPI program
        os.system(exec_line + " > output.txt")
        
        # Read the output file and extract the number of iterations
        with open("output.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                match = re.search(r"Number of iterations\s*:\s*(\d+)", line)
                if match:
                    iterations = int(match.group(1))
                    results[omega] = iterations
                    print(f"Omega: {omega}, Number of iterations: {iterations}")
                    break  # Exit the loop after finding the iterations line
        # delete the output file
        os.system("rm output.txt")
    return results


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
    res = best_omega_122(np.linspace(1.7, 1.99, 50))
    visualise(res)