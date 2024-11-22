import os, re
import numpy as np
import matplotlib.pyplot as plt
from util import update_input_file, reset_input_file
from uncertainties import ufloat
from uncertainties import unumpy as unp

# 800x 800 grid speedup: 
time_no_loop_improvement = np.array([5.48, 5.63, 5.67, 5.60, 5.76, 5.74, 5.77, 5.73, 5.66, 5.60])
time_loop_improvement = np.array([5.52, 5.67, 5.57, 5.70, 5.55, 5.54, 5.73, 5.64, 5.60, 5.76])
print("800x800 grid speedup:")
avg_no_imp = ufloat(np.mean(time_no_loop_improvement), np.std(time_no_loop_improvement))
avg_imp = ufloat(np.mean(time_loop_improvement), np.std(time_loop_improvement))
print(f"Average time without loop improvement: {avg_no_imp}")
print(f"Average time with loop improvement: {avg_imp}")

print("No compile flags:")
time_no_loop_improvement = np.array([5.66, 5.66, 5.70, 5.66, 5.64])
time_loop_improvement = np.array([5.67, 5.72, 5.58, 5.73, 5.74])
print("800x800 grid speedup:")
avg_no_imp = ufloat(np.mean(time_no_loop_improvement), np.std(time_no_loop_improvement))
avg_imp = ufloat(np.mean(time_loop_improvement), np.std(time_loop_improvement))
print(f"Average time without loop improvement: {avg_no_imp}")
print(f"Average time with loop improvement: {avg_imp}")