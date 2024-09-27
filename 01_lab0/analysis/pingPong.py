import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import re
from sklearn.metrics import r2_score

# latex presets
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=12)


def getdata(filename, base_dir= "01_lab0/res/"): 
    data = []
    # Load data from res
    with open(f'{base_dir}{filename}') as f:
        data = f.readlines()[1:]

    num_elements = [int(re.search(r'Received \d+', l).group()[9:]) for l in data]
    time = [float(re.search(r'took \d+\.\d+', l).group()[5:])*1000 for l in data] # time in ms
    return num_elements, time

# get all 5 samples
samples = [getdata(f'pingPong{i}.txt') for i in range(1, 6)]
samples_n2 = [getdata(f'pingPong{i}_2_nodes.txt') for i in range(1, 6)]
def plot(samples, samples_n2, fit_samples, fit_samples_n2):
    num_elements = samples[0][0]
    time = np.mean([s[1] for s in samples], axis=0)
    time_n2 = np.mean([s[1] for s in samples_n2], axis=0)
    plt.figure(figsize=(10, 6))
    for i, sample in enumerate(samples):
        plt.scatter(num_elements, sample[1],  color='skyblue')
    plt.plot(num_elements, time, label='Ping Pong (mean)', color="skyblue", linestyle='--') 
    
    for i, sample in enumerate(samples_n2):
        plt.scatter(num_elements, sample[1], color='burlywood')
    plt.plot(num_elements, time_n2, label='Ping Pong (mean) (2 nodes)', color="burlywood", linestyle='--')

    # add fits
    small_fit = fit_samples['small']
    large_fit = fit_samples['large']
    small_fit_n2 = fit_samples_n2['small']
    large_fit_n2 = fit_samples_n2['large']
    plt.plot(small_fit['elements'], small_fit['fit'](small_fit['elements']), label=f"Small fit: y = {small_fit['fit'].coeffs[0]:.2e}x + {small_fit['fit'].coeffs[1]:.2e} (r2={small_fit['r2']:.2f})", color='dodgerblue', linestyle=':', linewidth=2)
    plt.plot(large_fit['elements'], large_fit['fit'](large_fit['elements']), label=f"Large fit: y = {large_fit['fit'].coeffs[0]:.2e}x + {large_fit['fit'].coeffs[1]:.2e} (r2={large_fit['r2']:.2f})", color='dodgerblue', linestyle='-.', linewidth=2)
    plt.plot(small_fit_n2['elements'], small_fit_n2['fit'](small_fit_n2['elements']), label=f"Small fit (2 nodes): y = {small_fit_n2['fit'].coeffs[0]:.2e}x + {small_fit_n2['fit'].coeffs[1]:.2e} (r2={small_fit_n2['r2']:.2f})", color='darkorange', linestyle=':', linewidth=2)
    plt.plot(large_fit_n2['elements'], large_fit_n2['fit'](large_fit_n2['elements']), label=f"Large fit (2 nodes): y = {large_fit_n2['fit'].coeffs[0]:.2e}x + {large_fit_n2['fit'].coeffs[1]:.2e} (r2={large_fit_n2['r2']:.2f})", color='darkorange', linestyle='-.', linewidth=2)


    plt.xlabel('Number of bytes sent')
    plt.ylabel('Time (ms)')
    plt.title('Ping Pong')
    plt.xticks(np.linspace(0, 1000000, 11))
    # plt.xscale('log')
    plt.legend()
    plt.tight_layout()
    plt.savefig('lab_report/fig/lab0/pingPong.png')
    # plt.show()


def analyze(samples, small_threshold=33000):
    elements_flat, times_flat = [], []
    for sample in samples: 
        elements_flat += sample[0]
        times_flat += sample[1]

    # sort elements
    elements, times = zip(*sorted(zip(elements_flat, times_flat)))
    elements = np.array(elements)
    times = np.array(times)

    small_index = np.max(np.where(elements < small_threshold))

    small_elements = elements[:small_index+1]
    small_times = times[:small_index+1]
    large_elements = elements[small_index:] 
    large_times = times[small_index:]  

    
    # fit to small 
    small_fit = np.polyfit(small_elements, small_times, 1)
    small_fit_fn = np.poly1d(small_fit)
    small_r2 = r2_score(small_times, small_fit_fn(small_elements))
    print(f"Small fit: {small_fit_fn}")
    print(f"Small r2: {small_r2}")
    # fit to large
    large_fit = np.polyfit(large_elements, large_times, 1)
    large_fit_fn = np.poly1d(large_fit)
    large_r2 = r2_score(large_times, large_fit_fn(large_elements))
    print(f"Large fit: {large_fit_fn}")
    print(f"Large r2: {large_r2}")

    return {'small': {'elements': small_elements, 'times': small_times, 'fit': small_fit_fn, 'r2': small_r2},'large': {'elements': large_elements, 'times': large_times, 'fit': large_fit_fn, 'r2': large_r2}}
    



    # time_small = np.mean([s[1] for s in small_samples], axis=0)
    # print(time_small)


fit_samples = analyze(samples, 132000)
fit_samples_n2 = analyze(samples_n2, 33000)

plot(samples, samples_n2, fit_samples, fit_samples_n2) 

