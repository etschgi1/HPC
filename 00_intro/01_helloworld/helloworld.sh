#!/bin/bash
#
#SBATCH --job-name="hello"
#SBATCH --time=00:03:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=1G
#SBATCH --account=Education-EEMCS-Courses-WI4049TU
#SBATCH --reservation=wi4049tu
#SBATCH --qos=reservation

echo "Hello, World!" >> helloworld.txt
echo "The following nodes are reporting for duty:" >> helloworld.txt
srun hostname >> helloworld.txt
echo "Have a great day!" >> helloworld.txt
