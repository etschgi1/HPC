#!/bin/bash
#SBATCH --job-name="01_hello"
#SBATCH --time=00:00:45
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=1GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU



echo "Test one!!!"
srun ../MPI_Poisson.out 4 1 1.8 #> output/omega_test.txt
echo "Done with test"
