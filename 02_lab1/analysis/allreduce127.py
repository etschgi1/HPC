import numpy as np
from uncertainties import ufloat

time = {"1": [21.14, 21.8, 19.4], "10": [22.91, 19.6, 19.88], "100": [18.1,19.3,26]}
allreduce_time= {"1": [1.45, 1.52, 1.42], "10": [0.19875, 0.362, 0.175], "100": [0.021,0.024,0.026]}

time = {key: ufloat(np.mean(val), np.std(val)) for key, val in time.items()}
allreduce_time = {key: ufloat(np.mean(val), np.std(val)) for key, val in allreduce_time.items()}
baseline_ratio = allreduce_time["1"]/time["1"]*100
baseline_time = allreduce_time["1"]
for key, time, all_time in zip(time.keys(), time.values(), allreduce_time.values()):
    print(f"Time for {key} iterations: {time} s")
    print(f"Time for allreduce for {key} iterations: {all_time} s")
    print(f"Speedup: {baseline_time/all_time}")
    print(f"Overall speedup: {baseline_ratio - baseline_ratio/(baseline_time/all_time)}")
    print()