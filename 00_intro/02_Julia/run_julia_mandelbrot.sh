#!/bin/bash 
#
#SBATCH --job-name="julia"
#SBATCH --time=00:03:00
#SBATCH --partition=compute
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --account=Education-EEMCS-Courses-WI4049TU
#SBATCH --reservation=wi4049tu
#SBATCH --qos=reservation

module load 2023r1
module load julia 

srun julia mandelbrot.jl
