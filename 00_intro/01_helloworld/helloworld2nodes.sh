#!/bin/bash
#
#SBATCH --job-name="hello"
#SBATCH --time=00:03:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=1G
#SBATCH --account=Education-EEMCS-Courses-WI4049TU
#SBATCH --reservation=wi4049tu
#SBATCH --qos=reservation

echo "Hello, World!" 
echo "The following nodes are reporting for duty:" 
srun hostname 
echo "Have a great day!"
