ORIG_CONTENT = """nx: 100
ny: 100
precision goal: 0.0001
max iterations: 5000
source: 0.35 0.70 4.0
source: 0.625 0.75 4.0
source: 0.375 0.25 4.0"""
DEFAULT_NX = 100
DEFAULT_NY = 100
DEFAULT_MAX_ITER = 5000
DEFAULT_PRECISION_GOAL = 0.0001
DEFAULT_SOURCES = [(0.35, 0.70, 4.0), (0.625, 0.75, 4.0), (0.375, 0.25, 4.0)]

class bcolors: 
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

def update_input_file(nx=DEFAULT_NX, ny=DEFAULT_NY, max_iter=DEFAULT_MAX_ITER, precision_goal=DEFAULT_PRECISION_GOAL, sources=DEFAULT_SOURCES):
    """
    Updates the input.dat file with the given parameters.
    
    Parameters:
        nx (int): Number of grid points in the x-direction.
        ny (int): Number of grid points in the y-direction.
        max_iter (int): Maximum number of iterations.
        precision_goal (float): Desired precision goal.
        sources (list of tuples): Source terms, each as a tuple (x, y, value).
    """
    input_content = f"nx: {nx}\nny: {ny}\nprecision goal: {precision_goal}\nmax iterations: {max_iter}\n"
    for source in sources:
        input_content += f"source: {source[0]} {source[1]} {source[2]}\n"
    
    with open("input.dat", "w") as file:
        file.write(input_content)
    print(f"Updated input.dat with nx={nx}, ny={ny}, max_iter={max_iter}, precision_goal={precision_goal}")


def reset_input_file(orig_content = ORIG_CONTENT):
    """
    Resets the input.dat file to its original content.
    
    Parameters:
        orig_content (str): The original content of the input.dat file.
    """
    with open("input.dat", "w") as file:
        file.write(orig_content)
    print("Reset input.dat to its original state.")

if __name__ == "__main__":
    import os
    path = os.path.dirname(os.path.abspath(__file__))
    src = "../src"
    path = os.path.join(path, src)
    os.chdir(path)
    reset_input_file()