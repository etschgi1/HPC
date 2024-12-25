#!/bin/sh –l
#SBATCH --time=00:01:00
#SBATCH --partition=gpu-a100-small
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-task=1
#SBATCH --mem-per-cpu=4GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU
# adding the following lines will compile the code
# (actually, a makefile would be more appropriate)
# module load 2024r1 nvhpc
# file=’HelloWorld’
# nvcc –o $file $file.cu
# srun ./$file
srun HelloWorld