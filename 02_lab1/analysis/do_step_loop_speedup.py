import os, re
import numpy as np
import matplotlib.pyplot as plt
from util import update_input_file, reset_input_file
from uncertainties import ufloat
from uncertainties import unumpy as unp

# 800x 800 grid speedup: 
time_no_loop_improvement = np.array([5.64,5.52,5.63,5.55,5.62])
time_loop_improvement = np.array([4.57, 4.58, 4.67, 4.61, 4.75])
print("800x800 grid speedup:")
avg_no_imp = ufloat(np.mean(time_no_loop_improvement), np.std(time_no_loop_improvement))
avg_imp = ufloat(np.mean(time_loop_improvement), np.std(time_loop_improvement))
print(f"Average time without loop improvement: {avg_no_imp}")
print(f"Average time with loop improvement: {avg_imp}")

# print("No compile flags:")
# time_no_loop_improvement = np.array([5.58, 5.61, 5.67, 5.66, 5.81])
# time_loop_improvement = np.array([])
# print("800x800 grid speedup:")
# avg_no_imp = ufloat(np.mean(time_no_loop_improvement), np.std(time_no_loop_improvement))
# avg_imp = ufloat(np.mean(time_loop_improvement), np.std(time_loop_improvement))
# print(f"Average time without loop improvement: {avg_no_imp}")
# print(f"Average time with loop improvement: {avg_imp}")